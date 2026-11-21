#!/usr/bin/env python3
"""Compute local / pointwise FCI intrinsic dimensionality against a train reference manifold.

This script adapts the global Full Correlation Integral (FCI) estimator of
Erba, Gherardi, and Rotondo (Scientific Reports, 2019) to a pointwise
query-to-reference setting.

The original method is global: one preprocesses a full dataset, builds its
empirical full correlation integral, and fits the analytic FCI model to obtain
one intrinsic-dimension estimate.

The present script implements a local adaptation:
1. choose one query sentence;
2. select its k nearest train/reference neighbours inside a shared nested
   reference subset;
3. build a local cloud containing the query point plus those k neighbours;
4. apply the FCI preprocessing locally (center-of-mass subtraction and
   per-point normalization to the unit sphere);
5. build the empirical full correlation integral of that local cloud;
6. estimate the local FCI curve with either pyFCI.local_FCI (default) or the
   older in-script exact-pairwise backend;
7. report pointwise_fci_id in the requested k-reference-neighbour convention.

This is therefore a research-oriented local / pointwise adaptation of a global
estimator. The script records that fact explicitly in the saved metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

IMPORT_ERROR = None

try:
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    from scipy.optimize import curve_fit, least_squares
    from scipy.special import betainc, gamma, gammaln, hyp2f1
    import torch
    from tqdm import tqdm
except ModuleNotFoundError as exc:
    IMPORT_ERROR = exc


DEFAULT_REFERENCE_SIZES = "100,200,300,400,500,600,700,800,900,1000"
DEFAULT_K_VALUES = "2,5,10,15,20,25,30,35,50,70,100"
DEFAULT_REFERENCE_COUNT = 15_000
DEFAULT_EVAL_KNOWN_COUNT = 2000
DEFAULT_MAX_CURVE_POINTS = 1000
DEFAULT_LONG_QUERY_CHUNK = 128
DEFAULT_PREVIEW_ROWS = 5
FCI_BACKEND_PYFCI_LOCAL = "pyfci_local"
FCI_BACKEND_CUSTOM_EXACT = "custom_exact"
FCI_NOTES = [
    "This output stores a local / pointwise adaptation of the original global FCI estimator.",
    "For each query, the local cloud is the query point plus the k nearest train/reference neighbours.",
    "FCI preprocessing is applied locally: subtract the local center of mass and normalize each centered point.",
    "The same nested train-reference subsets are reused for eval_known and eval_unknown so the two query splits remain directly comparable.",
]
PYFCI_LOCAL_NOTES = [
    "The FCI backend is pyFCI.local_FCI from vittorioerba/pyFCI.",
    "pyFCI.local_FCI treats k as the local cloud size including the center point, so requested k reference neighbours are passed to pyFCI as k + 1.",
    "pyFCI.local_FCI uses its package defaults: FCI_MC for the empirical curve and fit_FCI for curve fitting.",
    "pyfci_random_seed is a best-effort seed before each pyFCI.local_FCI call; pyFCI still uses randomized Monte Carlo sampling internally.",
]
CUSTOM_EXACT_NOTES = [
    "The FCI backend is the earlier local custom implementation in this script.",
    "The custom backend enumerates all local pairwise distances and fits the analytic FCI curve with SciPy.",
    "The fitted parameter d_fit refers to the dimension on the normalized sphere, and the reported pointwise_fci_id is d_fit + 1.",
]


class FitFailureError(RuntimeError):
    """Raised when the nonlinear regression step fails."""


class NumericalFCIError(RuntimeError):
    """Raised when local preprocessing or curve construction becomes ill-conditioned."""


@dataclass
class SplitData:
    """Normalized one-split representation bundle loaded from a .pt file."""

    split_name: str
    input_path: Path
    reps: torch.Tensor
    texts: list[str]
    num_examples: int
    num_layers: int
    hidden_size: int
    sample_kind: str | None
    source_name: str | None
    source_repo_or_file: str | None
    source_config: str | None
    source_split: str | None
    source_is_official_split: bool | None
    source_doc_indices: torch.Tensor | None
    source_sentence_indices_in_doc: torch.Tensor | None
    num_chars: torch.Tensor | None
    num_words: torch.Tensor | None
    num_tokens: torch.Tensor | None
    pile_set_name: list[str] | None
    model_name: str | None
    revision: str | None
    layer_names: list[str] | None
    include_embeddings: bool | None
    seed: int | None
    buffer_size: int | None


@dataclass
class LoadedInputs:
    """Resolved input mode plus normalized train/eval split bundles."""

    input_mode: str
    train: SplitData
    eval_known: SplitData
    eval_unknown: SplitData
    combined_pt: Path | None
    train_pt: Path | None
    eval_known_pt: Path | None
    eval_unknown_pt: Path | None
    seen_pt: Path | None = None
    unseen_pt: Path | None = None


@dataclass
class ReferenceSetup:
    """Reference-pool metadata shared across eval_known and eval_unknown."""

    ordered_train_reference_indices: torch.Tensor
    reference_indices_by_size: dict[int, list[int]]
    reference_sizes_requested: list[int]
    k_values_requested: list[int]
    valid_reference_size_mask: torch.Tensor
    valid_k_mask: torch.Tensor
    invalid_reference_sizes: list[int]
    invalid_k_by_reference_size: dict[int, list[int]]


@dataclass
class FCIComputationCounts:
    """NaN accounting for one query split."""

    structural: int = 0
    fit_failures: int = 0
    numerical: int = 0


def update_signature_with_text(digest: Any, name: str, value: Any) -> None:
    """Update a hash digest with one scalar text field."""
    digest.update(str(name).encode("utf-8"))
    digest.update(b"\0")
    text_value = "" if value is None else str(value)
    digest.update(text_value.encode("utf-8"))
    digest.update(b"\0")


def update_signature_with_text_values(digest: Any, name: str, values: Sequence[Any]) -> None:
    """Update a hash digest with a sequence of text values."""
    update_signature_with_text(digest, f"{name}__len", len(values))
    for value in values:
        update_signature_with_text(digest, name, value)


def update_signature_with_int_values(digest: Any, name: str, values: Sequence[Any] | torch.Tensor) -> None:
    """Update a hash digest with a sequence of integer-like values."""
    tensor = torch.as_tensor(values, dtype=torch.long).reshape(-1).cpu()
    update_signature_with_text(digest, f"{name}__len", int(tensor.numel()))
    digest.update(tensor.numpy().tobytes())
    digest.update(b"\0")


def update_signature_with_bool_values(digest: Any, name: str, values: Sequence[Any] | torch.Tensor) -> None:
    """Update a hash digest with a sequence of booleans."""
    tensor = torch.as_tensor(values, dtype=torch.bool).reshape(-1).cpu()
    update_signature_with_text(digest, f"{name}__len", int(tensor.numel()))
    digest.update(tensor.numpy().astype(np.uint8, copy=False).tobytes())
    digest.update(b"\0")


def parse_args() -> argparse.Namespace:
    """Parse and validate CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Compute pointwise Full Correlation Integral (FCI) intrinsic dimensionality "
            "for eval_known and eval_unknown query sets against a train reference manifold."
        )
    )
    parser.add_argument("--combined_pt", type=str, default=None)
    parser.add_argument("--seen_pt", type=str, default=None)
    parser.add_argument("--unseen_pt", type=str, default=None)
    parser.add_argument("--train_pt", type=str, default=None)
    parser.add_argument("--eval_known_pt", type=str, default=None)
    parser.add_argument("--eval_unknown_pt", type=str, default=None)
    parser.add_argument("--reuse_reference_setup_pt", type=str, default=None)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--reference_count", type=int, default=DEFAULT_REFERENCE_COUNT)
    parser.add_argument("--eval_known_count", type=int, default=DEFAULT_EVAL_KNOWN_COUNT)
    parser.add_argument("--reshuffle_seen_before_split", action="store_true")
    parser.add_argument("--reference_sizes", type=str, default=DEFAULT_REFERENCE_SIZES)
    parser.add_argument("--k_values", type=str, default=DEFAULT_K_VALUES)
    parser.add_argument(
        "--layers",
        type=str,
        default=None,
        help="Optional comma-separated 1-based layer numbers to compute. Defaults to all layers.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--chunk_size", type=int, default=128)
    parser.add_argument("--max_curve_points", type=int, default=DEFAULT_MAX_CURVE_POINTS)
    parser.add_argument(
        "--fci_backend",
        type=str,
        default=FCI_BACKEND_PYFCI_LOCAL,
        choices=(FCI_BACKEND_PYFCI_LOCAL, FCI_BACKEND_CUSTOM_EXACT),
        help=(
            "`pyfci_local` uses vittorioerba/pyFCI local_FCI with requested k mapped to k+1 "
            "because pyFCI includes the center point in k. `custom_exact` preserves the older "
            "in-script exact-pairwise implementation."
        ),
    )
    parser.add_argument(
        "--pyfci_random_seed",
        type=int,
        default=None,
        help=(
            "Optional best-effort base seed used before each pyFCI.local_FCI call. pyFCI uses "
            "random sampling inside FCI_MC/fit_FCI."
        ),
    )
    parser.add_argument(
        "--fit_method",
        type=str,
        default="least_squares",
        choices=("curve_fit", "least_squares"),
        help="Curve-fitting method for --fci_backend custom_exact.",
    )
    parser.add_argument("--min_local_points_for_fci_fit", type=int, default=10)
    parser.add_argument("--min_curve_points_for_fit", type=int, default=20)
    parser.add_argument("--strict_reference_sizes", action="store_true")
    parser.add_argument("--strict_k_values", action="store_true")
    parser.add_argument("--save_nan_rows", action="store_true")
    parser.add_argument("--save_combined_pt", action="store_true")
    parser.add_argument("--include_reference_texts_in_output", action="store_true")
    parser.add_argument(
        "--compute_reference_queries",
        action="store_true",
        help=(
            "Also compute pyFCI/FCI for each sentence in the train/reference pool. "
            "The query sentence is excluded from its own neighbour set."
        ),
    )

    args = parser.parse_args()

    if args.chunk_size <= 0:
        parser.error("--chunk_size must be a positive integer.")
    if args.reference_count <= 0:
        parser.error("--reference_count must be a positive integer.")
    if args.eval_known_count <= 0:
        parser.error("--eval_known_count must be a positive integer.")
    if args.max_curve_points <= 0:
        parser.error("--max_curve_points must be a positive integer.")
    if args.min_local_points_for_fci_fit < 3:
        parser.error("--min_local_points_for_fci_fit must be at least 3.")
    if args.min_curve_points_for_fit < 3:
        parser.error("--min_curve_points_for_fit must be at least 3.")
    if args.max_curve_points < args.min_curve_points_for_fit:
        parser.error("--max_curve_points must be >= --min_curve_points_for_fit.")

    combined_requested = args.combined_pt is not None
    explicit_split_requested = any(
        value is not None
        for value in (args.train_pt, args.eval_known_pt, args.eval_unknown_pt)
    )
    seen_unseen_requested = args.seen_pt is not None or args.unseen_pt is not None
    if combined_requested and (explicit_split_requested or seen_unseen_requested):
        parser.error(
            "Provide either --combined_pt, or all of --train_pt/--eval_known_pt/--eval_unknown_pt, "
            "or both --seen_pt/--unseen_pt, not multiple modes."
        )
    if explicit_split_requested and seen_unseen_requested:
        parser.error(
            "Provide either explicit --train_pt/--eval_known_pt/--eval_unknown_pt or "
            "--seen_pt/--unseen_pt, not both."
        )
    if not combined_requested and not explicit_split_requested and not seen_unseen_requested:
        parser.error(
            "Provide either --combined_pt, all of --train_pt/--eval_known_pt/--eval_unknown_pt, "
            "or both --seen_pt/--unseen_pt."
        )
    if explicit_split_requested and not all(
        value is not None
        for value in (args.train_pt, args.eval_known_pt, args.eval_unknown_pt)
    ):
        parser.error(
            "When not using --combined_pt, you must provide all of --train_pt, --eval_known_pt, and --eval_unknown_pt."
        )
    if seen_unseen_requested and not (args.seen_pt is not None and args.unseen_pt is not None):
        parser.error("When using seen/unseen mode, provide both --seen_pt and --unseen_pt.")
    return args


def safe_torch_load(path: Path):
    """Load a torch file across PyTorch versions."""
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def ensure_input_file_exists(path: Path, description: str) -> None:
    """Validate a required file path."""
    if not path.exists():
        raise FileNotFoundError(f"{description} does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"{description} is not a file: {path}")


def parse_int_list(values: str, name: str) -> list[int]:
    """Parse a comma-separated integer list while preserving request order."""
    parts = [part.strip() for part in str(values).split(",")]
    if not parts or any(part == "" for part in parts):
        raise ValueError(f"{name} must be a non-empty comma-separated list of integers.")
    parsed: list[int] = []
    for part in parts:
        try:
            value = int(part)
        except ValueError as exc:
            raise ValueError(f"Invalid integer {part!r} in {name}.") from exc
        if value <= 0:
            raise ValueError(f"All values in {name} must be positive. Got {value}.")
        parsed.append(value)
    return parsed


def layer_number_from_name(layer_name: str, fallback_idx: int) -> int:
    """Return the human-facing model layer number for a saved layer name."""
    name = str(layer_name)
    if name == "embedding":
        return 0
    if name.startswith("layer_"):
        suffix = name.removeprefix("layer_")
        if suffix.isdigit():
            return int(suffix)
    return int(fallback_idx) + 1


def layer_numbers_from_indices(layer_indices: Sequence[int], layer_names: Sequence[str]) -> list[int]:
    """Map tensor layer positions back to model layer numbers when names are available."""
    return [
        layer_number_from_name(str(layer_names[int(layer_idx)]), int(layer_idx))
        for layer_idx in layer_indices
    ]


def parse_layer_indices(
    values: str | None,
    num_layers: int,
    layer_names: Sequence[str] | None = None,
) -> list[int]:
    """Parse an optional layer filter into tensor indices."""
    if values is None or str(values).strip() == "":
        return list(range(int(num_layers)))
    normalized = str(values).strip()
    if normalized.lower() == "all":
        return list(range(int(num_layers)))

    names = [str(name) for name in layer_names] if layer_names is not None else []
    if names and len(names) != int(num_layers):
        raise ValueError(f"layer_names length {len(names)} does not match num_layers={num_layers}.")
    name_to_idx = {name: idx for idx, name in enumerate(names)}
    seen: set[int] = set()
    indices: list[int] = []
    for raw in normalized.split(","):
        item = raw.strip()
        if not item:
            continue
        if item in name_to_idx:
            layer_idx = name_to_idx[item]
        else:
            try:
                layer_number = int(item)
            except ValueError as exc:
                raise ValueError(f"Invalid layer selector {item!r} in layers.") from exc
            named_layer = f"layer_{layer_number}"
            if named_layer in name_to_idx:
                layer_idx = name_to_idx[named_layer]
            elif layer_number == 0 and "embedding" in name_to_idx:
                layer_idx = name_to_idx["embedding"]
            elif 1 <= layer_number <= int(num_layers):
                layer_idx = int(layer_number) - 1
            else:
                raise ValueError(
                    f"Layer {item} is outside the available 1..{num_layers} range "
                    "and does not match layer_names."
                )
        if layer_idx not in seen:
            indices.append(layer_idx)
            seen.add(layer_idx)
    if not indices:
        raise ValueError("layers did not contain any valid layer numbers.")
    return indices


def resolve_device(device_arg: str | None) -> torch.device:
    """Choose CUDA automatically unless the user explicitly overrides it."""
    if device_arg is not None:
        return torch.device(device_arg)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def backend_notes(fci_backend: str) -> list[str]:
    """Return provenance notes for the selected FCI backend."""
    if str(fci_backend) == FCI_BACKEND_PYFCI_LOCAL:
        return list(FCI_NOTES) + list(PYFCI_LOCAL_NOTES)
    if str(fci_backend) == FCI_BACKEND_CUSTOM_EXACT:
        return list(FCI_NOTES) + list(CUSTOM_EXACT_NOTES)
    raise ValueError(f"Unsupported FCI backend: {fci_backend!r}.")


def load_pyfci_module() -> Any:
    """Import pyFCI lazily and provide a focused installation hint if unavailable."""
    try:
        import pyFCI as pyfci_module
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The selected FCI backend requires `pyFCI`. Install it with "
            "the exact VCS pin in this project's requirements-full.txt."
        ) from exc
    return pyfci_module


def pyfci_seed_for_call(
    base_seed: int | None,
    *,
    global_query_index: int,
    layer_idx: int,
    ref_idx: int,
) -> int | None:
    """Derive a deterministic per-call seed for pyFCI's stochastic local estimator."""
    if base_seed is None:
        return None
    modulus = 2**32 - 1
    seed = (
        int(base_seed)
        + 1_000_003 * int(global_query_index)
        + 10_007 * int(layer_idx)
        + 1_009 * int(ref_idx)
    ) % modulus
    return int(seed)


def is_vector_like(value: Any) -> bool:
    """Return True when a metadata field behaves like a per-example vector."""
    if value is None or isinstance(value, (str, bytes, dict)):
        return False
    if isinstance(value, torch.Tensor):
        return value.ndim > 0
    if isinstance(value, np.ndarray):
        return value.ndim > 0
    return isinstance(value, (list, tuple, pd.Series))


def scalar_to_string(value: Any) -> str | None:
    """Convert a scalar metadata field into a readable string."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list, tuple)):
        try:
            return json.dumps(value, sort_keys=True)
        except TypeError:
            return str(value)
    return str(value)


def normalize_optional_tensor(
    value: Any,
    expected_length: int,
    name: str,
    *,
    dtype: torch.dtype = torch.long,
) -> torch.Tensor | None:
    """Normalize optional vector metadata to a 1D CPU tensor."""
    if value is None:
        return None
    try:
        tensor = torch.as_tensor(value)
    except Exception as exc:
        raise ValueError(f"Could not convert {name} to a tensor.") from exc
    tensor = tensor.detach().cpu().reshape(-1)
    if int(tensor.numel()) != int(expected_length):
        raise ValueError(
            f"{name} length does not match reps.shape[0]: {tensor.numel()} vs {expected_length}."
        )
    return tensor.to(dtype=dtype).contiguous()


def normalize_optional_string_list(
    value: Any,
    expected_length: int,
    name: str,
) -> list[str] | None:
    """Normalize optional vector metadata to a list of strings."""
    if value is None:
        return None
    if not is_vector_like(value):
        raise ValueError(f"{name} must be sequence-like when provided as per-example metadata.")
    items = list(value.detach().cpu().tolist() if isinstance(value, torch.Tensor) else list(value))
    if len(items) != expected_length:
        raise ValueError(
            f"{name} length does not match reps.shape[0]: {len(items)} vs {expected_length}."
        )
    return ["" if item is None else str(item) for item in items]


def normalize_optional_scalar_string(value: Any) -> str | None:
    """Normalize one optional scalar provenance field."""
    return scalar_to_string(value)


def normalize_optional_scalar_bool(value: Any) -> bool | None:
    """Normalize one optional scalar boolean field."""
    if value is None:
        return None
    if isinstance(value, (list, tuple, np.ndarray, torch.Tensor, pd.Series)):
        values = list(value.detach().cpu().reshape(-1).tolist() if isinstance(value, torch.Tensor) else list(value))
        unique = {bool(item) for item in values}
        if len(unique) != 1:
            raise ValueError("Expected one scalar boolean value, but received varying per-example values.")
        return next(iter(unique))
    return bool(value)


def normalize_optional_scalar_int(value: Any) -> int | None:
    """Normalize one optional scalar integer field."""
    if value is None:
        return None
    if isinstance(value, (list, tuple, np.ndarray, torch.Tensor, pd.Series)):
        values = list(value.detach().cpu().reshape(-1).tolist() if isinstance(value, torch.Tensor) else list(value))
        unique = {int(item) for item in values}
        if len(unique) != 1:
            raise ValueError("Expected one scalar integer value, but received varying per-example values.")
        return next(iter(unique))
    return int(value)


def normalize_sample_kind(value: Any, expected_length: int, expected_kind: str, name: str) -> str | None:
    """Normalize optional sample_kind metadata and verify that it matches the split."""
    if value is None:
        return None
    if is_vector_like(value):
        items = list(value.detach().cpu().reshape(-1).tolist() if isinstance(value, torch.Tensor) else list(value))
        if len(items) != expected_length:
            raise ValueError(
                f"{name} length does not match reps.shape[0]: {len(items)} vs {expected_length}."
            )
        unique = {str(item) for item in items}
        if len(unique) != 1:
            raise ValueError(f"{name} must be consistent within the split; got {sorted(unique)}.")
        normalized = next(iter(unique))
    else:
        normalized = str(value)
    if normalized != expected_kind:
        raise ValueError(f"{name} is {normalized!r}, expected {expected_kind!r}.")
    return normalized


def normalize_layer_names(value: Any, num_layers: int) -> list[str] | None:
    """Normalize optional layer names and check their length."""
    if value is None:
        return None
    layer_names = [str(item) for item in list(value)]
    if len(layer_names) != int(num_layers):
        raise ValueError(
            f"layer_names length does not match reps.shape[1]: {len(layer_names)} vs {num_layers}."
        )
    return layer_names


def infer_layer_names(
    num_layers: int,
    include_embeddings: bool,
    provided_layer_names: Sequence[str] | None,
) -> list[str]:
    """Infer readable layer names when they are not stored in the input bundle."""
    if provided_layer_names is not None:
        layer_names = [str(value) for value in list(provided_layer_names)]
        if len(layer_names) != int(num_layers):
            raise ValueError(
                f"layer_names length does not match reps.shape[1]: {len(layer_names)} vs {num_layers}."
            )
        return layer_names
    if include_embeddings:
        return ["embedding"] + [f"layer_{index}" for index in range(1, num_layers)]
    return [f"layer_{index}" for index in range(1, num_layers + 1)]


def load_split_bundle(bundle: Any, *, split_name: str, input_path: Path) -> SplitData:
    """Validate and normalize one train/eval split bundle."""
    if not isinstance(bundle, dict):
        raise ValueError(f"The {split_name} split must be stored as a dictionary.")
    if "reps" not in bundle or "texts" not in bundle:
        raise KeyError(f"The {split_name} split must contain at least 'reps' and 'texts'.")

    reps = torch.as_tensor(bundle["reps"]).detach().cpu().contiguous()
    if reps.ndim != 3:
        raise ValueError(f"{split_name}.reps must have shape [N, L, D], got {tuple(reps.shape)}.")
    num_examples, num_layers, hidden_size = map(int, reps.shape)

    texts = normalize_optional_string_list(bundle.get("texts"), num_examples, f"{split_name}.texts")
    if texts is None:
        raise KeyError(f"The {split_name} split must contain a 'texts' field.")

    include_embeddings = None
    if "include_embeddings" in bundle:
        include_embeddings = bool(bundle["include_embeddings"])

    num_layers_metadata = bundle.get("num_layers")
    if num_layers_metadata is not None and int(num_layers_metadata) != int(num_layers):
        raise ValueError(
            f"{split_name}.num_layers metadata does not match reps.shape[1]: "
            f"{num_layers_metadata} vs {num_layers}."
        )
    hidden_size_metadata = bundle.get("hidden_size")
    if hidden_size_metadata is not None and int(hidden_size_metadata) != int(hidden_size):
        raise ValueError(
            f"{split_name}.hidden_size metadata does not match reps.shape[2]: "
            f"{hidden_size_metadata} vs {hidden_size}."
        )

    pile_value = bundle.get("pile_set_name")
    if pile_value is None:
        pile_value = bundle.get("pile_set_names")

    return SplitData(
        split_name=split_name,
        input_path=input_path,
        reps=reps,
        texts=texts,
        num_examples=num_examples,
        num_layers=num_layers,
        hidden_size=hidden_size,
        sample_kind=normalize_sample_kind(
            bundle.get("sample_kind"),
            num_examples,
            split_name,
            f"{split_name}.sample_kind",
        ),
        source_name=normalize_optional_scalar_string(bundle.get("source_name")),
        source_repo_or_file=normalize_optional_scalar_string(
            bundle.get("source_repo_or_file", bundle.get("source_file"))
        ),
        source_config=normalize_optional_scalar_string(bundle.get("source_config")),
        source_split=normalize_optional_scalar_string(
            bundle.get("source_split", bundle.get("source_kind"))
        ),
        source_is_official_split=normalize_optional_scalar_bool(bundle.get("source_is_official_split")),
        source_doc_indices=normalize_optional_tensor(
            bundle.get("source_doc_indices"),
            num_examples,
            f"{split_name}.source_doc_indices",
            dtype=torch.long,
        ),
        source_sentence_indices_in_doc=normalize_optional_tensor(
            bundle.get("source_sentence_indices_in_doc", bundle.get("line_indices")),
            num_examples,
            f"{split_name}.source_sentence_indices_in_doc",
            dtype=torch.long,
        ),
        num_chars=normalize_optional_tensor(bundle.get("num_chars"), num_examples, f"{split_name}.num_chars"),
        num_words=normalize_optional_tensor(bundle.get("num_words"), num_examples, f"{split_name}.num_words"),
        num_tokens=normalize_optional_tensor(bundle.get("num_tokens"), num_examples, f"{split_name}.num_tokens"),
        pile_set_name=normalize_optional_string_list(pile_value, num_examples, f"{split_name}.pile_set_name"),
        model_name=normalize_optional_scalar_string(bundle.get("model_name")),
        revision=normalize_optional_scalar_string(bundle.get("revision")),
        layer_names=normalize_layer_names(bundle.get("layer_names"), num_layers),
        include_embeddings=include_embeddings,
        seed=normalize_optional_scalar_int(bundle.get("seed")),
        buffer_size=normalize_optional_scalar_int(bundle.get("buffer_size")),
    )


def resolve_input_mode(args: argparse.Namespace) -> LoadedInputs:
    """Resolve train/eval inputs from either explicit or seen/unseen-style bundles."""
    if args.combined_pt is not None:
        combined_path = Path(args.combined_pt).expanduser()
        ensure_input_file_exists(combined_path, "Combined input file")
        bundle = safe_torch_load(combined_path)
        if not isinstance(bundle, dict):
            raise ValueError("The combined .pt file must contain a dictionary.")
        if all(key in bundle for key in ("train", "eval_known", "eval_unknown")):
            return LoadedInputs(
                input_mode="combined",
                train=load_split_bundle(bundle["train"], split_name="train", input_path=combined_path),
                eval_known=load_split_bundle(bundle["eval_known"], split_name="eval_known", input_path=combined_path),
                eval_unknown=load_split_bundle(bundle["eval_unknown"], split_name="eval_unknown", input_path=combined_path),
                combined_pt=combined_path,
                train_pt=None,
                eval_known_pt=None,
                eval_unknown_pt=None,
            )
        if all(key in bundle for key in ("seen", "unseen")):
            seen = load_split_bundle(bundle["seen"], split_name="seen", input_path=combined_path)
            unseen = load_split_bundle(bundle["unseen"], split_name="unseen", input_path=combined_path)
            if args.reuse_reference_setup_pt is not None:
                reference_pool_indices, eval_known_indices = load_seen_split_override(
                    path=Path(args.reuse_reference_setup_pt).expanduser(),
                    num_seen=seen.num_examples,
                    reference_count=int(args.reference_count),
                    eval_known_count=int(args.eval_known_count),
                )
            else:
                reference_pool_indices, eval_known_indices = split_seen_into_reference_and_eval_known(
                    seen.num_examples,
                    reference_count=int(args.reference_count),
                    eval_known_count=int(args.eval_known_count),
                    reshuffle_seen_before_split=bool(args.reshuffle_seen_before_split),
                    seed=int(args.seed),
                )
            return LoadedInputs(
                input_mode="combined_seen_unseen",
                train=subset_split_data(seen, reference_pool_indices, new_split_name="train"),
                eval_known=subset_split_data(seen, eval_known_indices, new_split_name="eval_known"),
                eval_unknown=subset_split_data(
                    unseen,
                    torch.arange(unseen.num_examples, dtype=torch.long),
                    new_split_name="eval_unknown",
                ),
                combined_pt=combined_path,
                train_pt=None,
                eval_known_pt=None,
                eval_unknown_pt=None,
            )
        raise KeyError(
            "The combined .pt file must contain either "
            "`train`/`eval_known`/`eval_unknown` or `seen`/`unseen` keys."
        )

    if args.seen_pt is not None or args.unseen_pt is not None:
        seen_path = Path(args.seen_pt).expanduser()
        unseen_path = Path(args.unseen_pt).expanduser()
        ensure_input_file_exists(seen_path, "Seen input file")
        ensure_input_file_exists(unseen_path, "Unseen input file")
        seen = load_split_bundle(safe_torch_load(seen_path), split_name="seen", input_path=seen_path)
        unseen = load_split_bundle(safe_torch_load(unseen_path), split_name="unseen", input_path=unseen_path)
        if args.reuse_reference_setup_pt is not None:
            reference_pool_indices, eval_known_indices = load_seen_split_override(
                path=Path(args.reuse_reference_setup_pt).expanduser(),
                num_seen=seen.num_examples,
                reference_count=int(args.reference_count),
                eval_known_count=int(args.eval_known_count),
            )
        else:
            reference_pool_indices, eval_known_indices = split_seen_into_reference_and_eval_known(
                seen.num_examples,
                reference_count=int(args.reference_count),
                eval_known_count=int(args.eval_known_count),
                reshuffle_seen_before_split=bool(args.reshuffle_seen_before_split),
                seed=int(args.seed),
            )
        return LoadedInputs(
            input_mode="seen_unseen",
            train=subset_split_data(seen, reference_pool_indices, new_split_name="train"),
            eval_known=subset_split_data(seen, eval_known_indices, new_split_name="eval_known"),
            eval_unknown=subset_split_data(
                unseen,
                torch.arange(unseen.num_examples, dtype=torch.long),
                new_split_name="eval_unknown",
            ),
            combined_pt=None,
            train_pt=None,
            eval_known_pt=None,
            eval_unknown_pt=None,
            seen_pt=seen_path,
            unseen_pt=unseen_path,
        )

    train_path = Path(args.train_pt).expanduser()
    eval_known_path = Path(args.eval_known_pt).expanduser()
    eval_unknown_path = Path(args.eval_unknown_pt).expanduser()
    ensure_input_file_exists(train_path, "Train input file")
    ensure_input_file_exists(eval_known_path, "eval_known input file")
    ensure_input_file_exists(eval_unknown_path, "eval_unknown input file")
    return LoadedInputs(
        input_mode="separate",
        train=load_split_bundle(safe_torch_load(train_path), split_name="train", input_path=train_path),
        eval_known=load_split_bundle(
            safe_torch_load(eval_known_path),
            split_name="eval_known",
            input_path=eval_known_path,
        ),
        eval_unknown=load_split_bundle(
            safe_torch_load(eval_unknown_path),
            split_name="eval_unknown",
            input_path=eval_unknown_path,
        ),
        combined_pt=None,
        train_pt=train_path,
        eval_known_pt=eval_known_path,
        eval_unknown_pt=eval_unknown_path,
    )


def choose_matching_optional_metadata(
    field_name: str,
    train_value: Any,
    eval_known_value: Any,
    eval_unknown_value: Any,
) -> Any:
    """Require agreement when all three inputs provide the same optional metadata field."""
    provided = [value for value in (train_value, eval_known_value, eval_unknown_value) if value is not None]
    if not provided:
        return None
    if len(provided) == 3 and not (train_value == eval_known_value == eval_unknown_value):
        raise ValueError(
            f"Mismatch across train/eval_known/eval_unknown for {field_name}: "
            f"{train_value!r}, {eval_known_value!r}, {eval_unknown_value!r}."
        )
    return train_value if train_value is not None else provided[0]


def validate_compatible_rep_shapes(loaded: LoadedInputs) -> dict[str, Any]:
    """Validate that train/eval splits can be compared directly."""
    train = loaded.train
    eval_known = loaded.eval_known
    eval_unknown = loaded.eval_unknown

    if train.num_layers != eval_known.num_layers or train.num_layers != eval_unknown.num_layers:
        raise ValueError(
            "All splits must have the same number of layers. "
            f"Got train={train.num_layers}, eval_known={eval_known.num_layers}, eval_unknown={eval_unknown.num_layers}."
        )
    if train.hidden_size != eval_known.hidden_size or train.hidden_size != eval_unknown.hidden_size:
        raise ValueError(
            "All splits must have the same hidden size. "
            f"Got train={train.hidden_size}, eval_known={eval_known.hidden_size}, eval_unknown={eval_unknown.hidden_size}."
        )

    if (
        train.layer_names is not None
        and eval_known.layer_names is not None
        and train.layer_names != eval_known.layer_names
    ):
        raise ValueError("train.layer_names and eval_known.layer_names do not match.")
    if (
        train.layer_names is not None
        and eval_unknown.layer_names is not None
        and train.layer_names != eval_unknown.layer_names
    ):
        raise ValueError("train.layer_names and eval_unknown.layer_names do not match.")

    model_name = choose_matching_optional_metadata(
        "model_name",
        train.model_name,
        eval_known.model_name,
        eval_unknown.model_name,
    )
    revision = choose_matching_optional_metadata(
        "revision",
        train.revision,
        eval_known.revision,
        eval_unknown.revision,
    )
    include_embeddings = choose_matching_optional_metadata(
        "include_embeddings",
        train.include_embeddings,
        eval_known.include_embeddings,
        eval_unknown.include_embeddings,
    )
    include_embeddings = bool(include_embeddings) if include_embeddings is not None else False

    layer_names = infer_layer_names(
        train.num_layers,
        include_embeddings,
        train.layer_names if train.layer_names is not None else eval_known.layer_names or eval_unknown.layer_names,
    )
    return {
        "num_layers": int(train.num_layers),
        "hidden_size": int(train.hidden_size),
        "model_name": model_name,
        "revision": revision,
        "include_embeddings": include_embeddings,
        "layer_names": layer_names,
    }


def build_validity_masks(
    *,
    num_reference_pool: int,
    reference_sizes: Sequence[int],
    k_values: Sequence[int],
    min_local_points_for_fci_fit: int,
    min_curve_points_for_fit: int,
    strict_reference_sizes: bool,
    strict_k_values: bool,
) -> tuple[torch.Tensor, torch.Tensor, list[int], dict[int, list[int]]]:
    """Build structural validity masks for reference sizes and k values."""
    valid_reference_size_mask = torch.tensor(
        [1 <= int(reference_size) <= int(num_reference_pool) for reference_size in reference_sizes],
        dtype=torch.bool,
    ).contiguous()
    invalid_reference_sizes = [
        int(reference_size)
        for reference_size, is_valid in zip(reference_sizes, valid_reference_size_mask.tolist())
        if not is_valid
    ]
    if invalid_reference_sizes and strict_reference_sizes:
        raise ValueError(
            "Requested reference sizes exceed the available train/reference pool. "
            f"num_reference_pool={num_reference_pool}, invalid_reference_sizes={invalid_reference_sizes}."
        )

    valid_k_mask = torch.zeros((len(reference_sizes), len(k_values)), dtype=torch.bool)
    invalid_k_by_reference_size: dict[int, list[int]] = {}
    for ref_idx, reference_size in enumerate(reference_sizes):
        invalid_ks: list[int] = []
        if not bool(valid_reference_size_mask[ref_idx].item()):
            invalid_k_by_reference_size[int(reference_size)] = list(map(int, k_values))
            continue
        for k_idx, k_value in enumerate(k_values):
            local_points = int(k_value) + 1
            curve_points = local_points * (local_points - 1) // 2
            is_valid = (
                int(k_value) <= int(reference_size)
                and local_points >= int(min_local_points_for_fci_fit)
                and curve_points >= int(min_curve_points_for_fit)
            )
            valid_k_mask[ref_idx, k_idx] = bool(is_valid)
            if not is_valid:
                invalid_ks.append(int(k_value))
        if invalid_ks:
            invalid_k_by_reference_size[int(reference_size)] = invalid_ks

    if invalid_k_by_reference_size and strict_k_values:
        raise ValueError(
            "Some requested k values are structurally invalid for FCI under at least one reference size: "
            f"{invalid_k_by_reference_size}. "
            "Invalid combinations include k > reference_size and local clouds / empirical curves that are too small "
            "for the requested min_local_points_for_fci_fit or min_curve_points_for_fit."
        )
    return (
        valid_reference_size_mask.contiguous(),
        valid_k_mask.contiguous(),
        invalid_reference_sizes,
        invalid_k_by_reference_size,
    )


def build_nested_reference_sets(
    num_reference_pool: int,
    reference_sizes: Sequence[int],
    valid_reference_size_mask: torch.Tensor,
    seed: int,
) -> tuple[torch.Tensor, dict[int, list[int]]]:
    """Create one nested family of train-reference subsets from a single permutation."""
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    ordered_train_reference_indices = torch.randperm(int(num_reference_pool), generator=generator).contiguous()
    reference_indices_by_size: dict[int, list[int]] = {}
    for reference_size, is_valid in zip(reference_sizes, valid_reference_size_mask.tolist()):
        if not is_valid:
            continue
        reference_indices_by_size[int(reference_size)] = [
            int(index)
            for index in ordered_train_reference_indices[: int(reference_size)].tolist()
        ]
    return ordered_train_reference_indices, reference_indices_by_size


def build_reference_setup_signature(reference_setup: ReferenceSetup) -> str:
    """Hash the exact nested train-reference construction."""
    digest = hashlib.sha1()
    update_signature_with_int_values(
        digest,
        "ordered_train_reference_indices",
        reference_setup.ordered_train_reference_indices,
    )
    update_signature_with_int_values(
        digest,
        "reference_sizes_requested",
        reference_setup.reference_sizes_requested,
    )
    update_signature_with_int_values(
        digest,
        "k_values_requested",
        reference_setup.k_values_requested,
    )
    update_signature_with_bool_values(
        digest,
        "valid_reference_size_mask",
        reference_setup.valid_reference_size_mask,
    )
    update_signature_with_bool_values(
        digest,
        "valid_k_mask",
        reference_setup.valid_k_mask,
    )
    for reference_size in reference_setup.reference_sizes_requested:
        update_signature_with_int_values(
            digest,
            f"reference_indices_by_size::{int(reference_size)}",
            reference_setup.reference_indices_by_size.get(int(reference_size), []),
        )
    return digest.hexdigest()


def build_query_selection_signature(
    *,
    query_indices: torch.Tensor,
    sample_kind: str,
    query_source_name: str | None,
    query_source_repo_or_file: str | None,
) -> str:
    """Hash the exact query subset used for one split."""
    digest = hashlib.sha1()
    update_signature_with_int_values(digest, "query_indices", query_indices)
    update_signature_with_text(digest, "sample_kind", sample_kind)
    update_signature_with_text(digest, "query_source_name", query_source_name)
    update_signature_with_text(digest, "query_source_repo_or_file", query_source_repo_or_file)
    return digest.hexdigest()


def build_split_setup_signature(
    *,
    reference_setup_signature: str,
    query_selection_signature: str,
    common_metadata: dict[str, Any],
) -> str:
    """Hash the metric-invariant setup shared across pointwise metrics."""
    digest = hashlib.sha1()
    update_signature_with_text(digest, "reference_setup_signature", reference_setup_signature)
    update_signature_with_text(digest, "query_selection_signature", query_selection_signature)
    update_signature_with_text(digest, "model_name", common_metadata.get("model_name"))
    update_signature_with_text(digest, "revision", common_metadata.get("revision"))
    update_signature_with_text(
        digest,
        "include_embeddings",
        str(bool(common_metadata.get("include_embeddings", False))),
    )
    update_signature_with_text_values(digest, "layer_names", common_metadata["layer_names"])
    update_signature_with_int_values(digest, "num_layers", [int(common_metadata["num_layers"])])
    update_signature_with_int_values(digest, "hidden_size", [int(common_metadata["hidden_size"])])
    return digest.hexdigest()


def _extract_reference_setup_payload(raw_payload: Any) -> dict[str, Any]:
    """Unwrap supported payload layouts for an externally saved reference setup."""
    if not isinstance(raw_payload, dict):
        raise ValueError("The reused reference setup file must contain a dictionary payload.")
    if "reference_info" in raw_payload and isinstance(raw_payload["reference_info"], dict):
        return dict(raw_payload["reference_info"])
    return dict(raw_payload)


def load_reference_setup_override(
    *,
    path: Path,
    num_reference_pool: int,
    reference_sizes_requested: Sequence[int],
    k_values_requested: Sequence[int],
    valid_reference_size_mask: torch.Tensor,
    valid_k_mask: torch.Tensor,
) -> tuple[torch.Tensor, dict[int, list[int]]]:
    """Load and validate an externally saved reference setup.

    This lets FCI reuse the exact same reference sentences that were already
    selected for another metric such as MLE or ESS.
    """
    ensure_input_file_exists(path, "Reference setup file")
    payload = _extract_reference_setup_payload(safe_torch_load(path))

    saved_reference_sizes = [int(value) for value in list(payload.get("reference_sizes_requested", []))]
    saved_k_values = [int(value) for value in list(payload.get("k_values_requested", []))]
    requested_reference_sizes = [int(value) for value in reference_sizes_requested]
    requested_k_values = [int(value) for value in k_values_requested]
    missing_reference_sizes = [
        value for value in requested_reference_sizes if value not in set(saved_reference_sizes)
    ]
    if missing_reference_sizes:
        raise ValueError(
            "The reused reference setup file does not contain all requested reference sizes. "
            f"Saved={saved_reference_sizes}, requested={requested_reference_sizes}, "
            f"missing={missing_reference_sizes}."
        )
    missing_k_values = [value for value in requested_k_values if value not in set(saved_k_values)]
    if missing_k_values:
        raise ValueError(
            "The reused reference setup file does not contain all requested k values. "
            f"Saved={saved_k_values}, requested={requested_k_values}, missing={missing_k_values}."
        )

    saved_num_reference_pool = payload.get(
        "num_reference_pool",
        payload.get("train_num_reference_pool", payload.get("reference_count")),
    )
    if saved_num_reference_pool is None:
        saved_order = payload.get("ordered_train_reference_indices", payload.get("ordered_reference_pool_indices"))
        if saved_order is not None:
            saved_num_reference_pool = int(torch.as_tensor(saved_order).numel())
    if saved_num_reference_pool is not None and int(saved_num_reference_pool) != int(num_reference_pool):
        raise ValueError(
            "The reused reference setup file was built for a different reference pool size. "
            f"Saved={saved_num_reference_pool}, current={num_reference_pool}."
        )

    saved_valid_reference_size_mask = payload.get("valid_reference_size_mask")
    if saved_valid_reference_size_mask is not None:
        saved_valid_reference_size_mask = torch.as_tensor(saved_valid_reference_size_mask, dtype=torch.bool).reshape(-1).cpu()
        if saved_valid_reference_size_mask.numel() != len(saved_reference_sizes):
            raise ValueError("The reused reference setup file has an invalid valid_reference_size_mask length.")
        saved_valid_by_reference_size = {
            reference_size: bool(is_valid)
            for reference_size, is_valid in zip(saved_reference_sizes, saved_valid_reference_size_mask.tolist())
        }
        requested_valid_by_reference_size = {
            reference_size: bool(is_valid)
            for reference_size, is_valid in zip(requested_reference_sizes, valid_reference_size_mask.cpu().tolist())
        }
        for reference_size, requested_is_valid in requested_valid_by_reference_size.items():
            saved_is_valid = saved_valid_by_reference_size.get(reference_size)
            if saved_is_valid != requested_is_valid:
                raise ValueError(
                    "The reused reference setup file has a different valid_reference_size_mask "
                    f"for reference size {reference_size}."
                )
    # Do not require the saved valid_k_mask to match. Reference reuse is about
    # reusing the exact reference sentences, while k-validity is estimator-
    # specific: FCI can structurally invalidate small-k settings that were
    # perfectly valid for MLE/ESS.

    reference_indices_by_size_raw = payload.get("reference_indices_by_size")
    if not isinstance(reference_indices_by_size_raw, dict):
        raise ValueError("The reused reference setup file is missing `reference_indices_by_size`.")
    reference_indices_by_size: dict[int, list[int]] = {}
    for key, values in reference_indices_by_size_raw.items():
        reference_size = int(key)
        indices = [int(value) for value in list(values)]
        if any(index < 0 or index >= int(num_reference_pool) for index in indices):
            raise ValueError(
                f"Reused reference indices for size {reference_size} fall outside the current train/reference pool."
            )
        reference_indices_by_size[reference_size] = indices

    valid_reference_sizes = [
        int(reference_size)
        for reference_size, is_valid in zip(reference_sizes_requested, valid_reference_size_mask.tolist())
        if is_valid
    ]
    for reference_size in valid_reference_sizes:
        if reference_size not in reference_indices_by_size:
            raise ValueError(
                f"The reused reference setup file is missing reference indices for valid size {reference_size}."
            )
        indices = reference_indices_by_size[reference_size]
        if len(indices) != reference_size:
            raise ValueError(
                f"The reused reference indices for size {reference_size} have length {len(indices)}, expected {reference_size}."
            )

    ordered_train_reference_indices = torch.empty(0, dtype=torch.long)
    previous_indices: list[int] = []
    for reference_size in valid_reference_sizes:
        indices = reference_indices_by_size[reference_size]
        if previous_indices and indices[: len(previous_indices)] != previous_indices:
            raise ValueError(
                f"The reused reference setup is not nested: size {reference_size} is not a prefix extension "
                "of the smaller reference sizes."
            )
        previous_indices = list(indices)
    if previous_indices:
        ordered_train_reference_indices = torch.tensor(previous_indices, dtype=torch.long).contiguous()

    return ordered_train_reference_indices, reference_indices_by_size


def split_seen_into_reference_and_eval_known(
    num_seen: int,
    *,
    reference_count: int,
    eval_known_count: int,
    reshuffle_seen_before_split: bool,
    seed: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Split seen indices into train-reference and eval_known subsets."""
    total_needed = int(reference_count) + int(eval_known_count)
    if int(num_seen) < total_needed:
        raise ValueError(
            f"Seen file contains only {num_seen} examples, but {total_needed} are required "
            f"for reference_count={reference_count} and eval_known_count={eval_known_count}."
        )

    if reshuffle_seen_before_split:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(int(seed))
        ordered_seen_indices = torch.randperm(int(num_seen), generator=generator)
    else:
        ordered_seen_indices = torch.arange(int(num_seen), dtype=torch.long)

    reference_pool_indices = ordered_seen_indices[: int(reference_count)].cpu().long().contiguous()
    eval_known_indices = (
        ordered_seen_indices[int(reference_count) : int(reference_count) + int(eval_known_count)]
        .cpu()
        .long()
        .contiguous()
    )
    return reference_pool_indices, eval_known_indices


def load_seen_split_override(
    *,
    path: Path,
    num_seen: int,
    reference_count: int,
    eval_known_count: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Load exact seen->train/eval_known split indices from another saved run."""
    ensure_input_file_exists(path, "Reference setup file")
    payload = _extract_reference_setup_payload(safe_torch_load(path))

    reference_pool_indices = payload.get("reference_pool_indices")
    eval_known_indices = payload.get("eval_known_indices")
    if reference_pool_indices is None or eval_known_indices is None:
        raise ValueError(
            "The reused reference setup file must contain both `reference_pool_indices` and "
            "`eval_known_indices` to recreate the seen/train split exactly."
        )

    reference_pool_indices = torch.as_tensor(reference_pool_indices, dtype=torch.long).reshape(-1).cpu().contiguous()
    eval_known_indices = torch.as_tensor(eval_known_indices, dtype=torch.long).reshape(-1).cpu().contiguous()

    if int(reference_pool_indices.numel()) != int(reference_count):
        raise ValueError(
            "The reused split file does not match the requested reference_count. "
            f"Saved={int(reference_pool_indices.numel())}, requested={int(reference_count)}."
        )
    if int(eval_known_indices.numel()) != int(eval_known_count):
        raise ValueError(
            "The reused split file does not match the requested eval_known_count. "
            f"Saved={int(eval_known_indices.numel())}, requested={int(eval_known_count)}."
        )
    if bool(((reference_pool_indices < 0) | (reference_pool_indices >= int(num_seen))).any().item()):
        raise ValueError("The reused reference_pool_indices fall outside the current seen set.")
    if bool(((eval_known_indices < 0) | (eval_known_indices >= int(num_seen))).any().item()):
        raise ValueError("The reused eval_known_indices fall outside the current seen set.")
    if set(reference_pool_indices.tolist()).intersection(eval_known_indices.tolist()):
        raise ValueError("The reused reference_pool_indices and eval_known_indices overlap.")

    return reference_pool_indices, eval_known_indices


def subset_split_data(
    split: SplitData,
    indices: torch.Tensor,
    *,
    new_split_name: str,
) -> SplitData:
    """Create a subset SplitData with per-example metadata sliced consistently."""
    indices = indices.detach().cpu().long().contiguous()
    texts = [split.texts[int(index)] for index in indices.tolist()]
    return SplitData(
        split_name=new_split_name,
        input_path=split.input_path,
        reps=split.reps.index_select(0, indices).contiguous(),
        texts=texts,
        num_examples=int(indices.numel()),
        num_layers=split.num_layers,
        hidden_size=split.hidden_size,
        sample_kind=new_split_name,
        source_name=split.source_name,
        source_repo_or_file=split.source_repo_or_file,
        source_config=split.source_config,
        source_split=new_split_name,
        source_is_official_split=split.source_is_official_split,
        source_doc_indices=(
            split.source_doc_indices.index_select(0, indices).contiguous()
            if split.source_doc_indices is not None
            else None
        ),
        source_sentence_indices_in_doc=(
            split.source_sentence_indices_in_doc.index_select(0, indices).contiguous()
            if split.source_sentence_indices_in_doc is not None
            else None
        ),
        num_chars=split.num_chars.index_select(0, indices).contiguous() if split.num_chars is not None else None,
        num_words=split.num_words.index_select(0, indices).contiguous() if split.num_words is not None else None,
        num_tokens=split.num_tokens.index_select(0, indices).contiguous() if split.num_tokens is not None else None,
        pile_set_name=[split.pile_set_name[int(index)] for index in indices.tolist()] if split.pile_set_name is not None else None,
        model_name=split.model_name,
        revision=split.revision,
        layer_names=list(split.layer_names) if split.layer_names is not None else None,
        include_embeddings=split.include_embeddings,
        seed=split.seed,
        buffer_size=split.buffer_size,
    )


def gather_query_metadata(split: SplitData) -> dict[str, Any]:
    """Gather query metadata for one eval split."""
    return {
        "query_indices": torch.arange(split.num_examples, dtype=torch.long),
        "texts": list(split.texts),
        "sample_kind": split.sample_kind or split.split_name,
        "source_name": split.source_name,
        "source_repo_or_file": split.source_repo_or_file,
        "source_config": split.source_config,
        "source_split": split.source_split,
        "source_is_official_split": split.source_is_official_split,
        "source_doc_indices": split.source_doc_indices.clone().contiguous() if split.source_doc_indices is not None else None,
        "source_sentence_indices_in_doc": (
            split.source_sentence_indices_in_doc.clone().contiguous()
            if split.source_sentence_indices_in_doc is not None
            else None
        ),
        "num_chars": split.num_chars.clone().contiguous() if split.num_chars is not None else None,
        "num_words": split.num_words.clone().contiguous() if split.num_words is not None else None,
        "num_tokens": split.num_tokens.clone().contiguous() if split.num_tokens is not None else None,
        "pile_set_name": list(split.pile_set_name) if split.pile_set_name is not None else None,
    }


def solid_angle(dim: float | np.ndarray) -> np.ndarray:
    """Return the d-dimensional solid angle Ω_d = 2π^((d+1)/2) / Γ((d+1)/2)."""
    dim_array = np.asarray(dim, dtype=np.float64)
    return 2.0 * np.pi ** ((dim_array + 1.0) / 2.0) / gamma((dim_array + 1.0) / 2.0)


def fci_prefactor(d_fit: float) -> float:
    """Return Ω(d-1) / (2 Ω(d)) using a log-gamma form for numerical stability."""
    d_value = float(d_fit)
    if not np.isfinite(d_value) or d_value <= 0.0:
        return float("nan")
    with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
        log_prefactor = (
            gammaln((d_value + 1.0) / 2.0)
            - gammaln(d_value / 2.0)
            - np.log(2.0 * np.sqrt(np.pi))
        )
        prefactor = float(np.exp(log_prefactor))
    return prefactor if np.isfinite(prefactor) else float("nan")


def fci_model_hypergeometric(r: np.ndarray, d_fit: float, r_s: float) -> np.ndarray:
    """Evaluate the paper's hypergeometric FCI formula directly.

    Notes
    -----
    This is the analytic expression reported in the paper. In practice,
    SciPy's direct analytic continuation of ``hyp2f1`` can become numerically
    unstable for some real-valued arguments, so ``fci_model`` falls back to a
    mathematically equivalent incomplete-beta form when needed.
    """
    radius = np.asarray(r, dtype=np.float64)
    d_value = float(d_fit)
    r_scale = float(r_s)
    if not np.isfinite(d_value) or not np.isfinite(r_scale) or d_value <= 0.0 or r_scale <= 0.0:
        return np.full_like(radius, np.nan, dtype=np.float64)
    r_bar = np.clip(radius / r_scale, 0.0, 2.0)
    prefactor = fci_prefactor(d_value)
    if not np.isfinite(prefactor):
        return np.full_like(radius, np.nan, dtype=np.float64)
    z_value = (r_bar**2 - 2.0) ** 2
    with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
        hyper = hyp2f1(0.5, 1.0 - d_value / 2.0, 1.5, z_value)
        result = 0.5 + prefactor * (r_bar**2 - 2.0) * hyper
    return np.asarray(np.real(result), dtype=np.float64)


def fci_model_stable_equivalent(r: np.ndarray, d_fit: float, r_s: float) -> np.ndarray:
    """Evaluate the same analytic FCI model with a numerically stable equivalent form.

    For uniformly sampled hyperspheres, the full correlation integral can be
    written as a regularized incomplete-beta expression in the polar angle.
    This yields the same model while keeping the fit real-valued on the
    physical chord-distance interval r_bar in [0, 2].
    """
    radius = np.asarray(r, dtype=np.float64)
    d_value = float(d_fit)
    r_scale = float(r_s)
    if not np.isfinite(d_value) or not np.isfinite(r_scale) or d_value <= 0.0 or r_scale <= 0.0:
        return np.full_like(radius, np.nan, dtype=np.float64)
    r_bar = np.clip(radius / r_scale, 0.0, 2.0)
    beta_argument = np.clip(r_bar**2 * (1.0 - 0.25 * r_bar**2), 0.0, 1.0)
    lower_branch = 0.5 * betainc(d_value / 2.0, 0.5, beta_argument)
    return np.where(r_bar <= np.sqrt(2.0), lower_branch, 1.0 - lower_branch)


def fci_model(r: np.ndarray, d_fit: float, r_s: float) -> np.ndarray:
    """Evaluate the analytic FCI model used in the nonlinear regression.

    The implementation first evaluates the paper's hypergeometric formula. When
    SciPy returns unstable values, it falls back to a mathematically equivalent
    incomplete-beta expression so the fit remains real-valued and bounded.
    """
    direct = fci_model_hypergeometric(r, d_fit=d_fit, r_s=r_s)
    stable = fci_model_stable_equivalent(r, d_fit=d_fit, r_s=r_s)
    if direct.shape != stable.shape:
        return stable
    bad_mask = (~np.isfinite(direct)) | (direct < -1e-8) | (direct > 1.0 + 1e-8)
    if np.any(bad_mask):
        direct = direct.copy()
        direct[bad_mask] = stable[bad_mask]
    return direct


def build_local_cloud_for_query(query_point: np.ndarray, neighbor_points: np.ndarray) -> np.ndarray:
    """Build the local cloud used for one pointwise FCI estimate."""
    query_row = np.asarray(query_point, dtype=np.float64).reshape(1, -1)
    neighbors = np.asarray(neighbor_points, dtype=np.float64)
    if neighbors.ndim != 2:
        raise NumericalFCIError(f"neighbor_points must be rank-2; got shape {neighbors.shape}.")
    return np.concatenate([query_row, neighbors], axis=0)


def preprocess_local_cloud_for_fci(local_cloud: np.ndarray, *, eps: float = 1e-12) -> np.ndarray:
    """Apply the FCI preprocessing locally.

    This follows the original FCI procedure, but on the local cloud defined by
    one query point plus its k nearest reference neighbours.
    """
    cloud = np.asarray(local_cloud, dtype=np.float64)
    if cloud.ndim != 2 or cloud.shape[0] < 2:
        raise NumericalFCIError(f"local_cloud must have shape [n_local, d], got {cloud.shape}.")
    if not np.all(np.isfinite(cloud)):
        raise NumericalFCIError("local_cloud contains non-finite values before preprocessing.")

    center_of_mass = np.mean(cloud, axis=0, keepdims=True)
    centered = cloud - center_of_mass
    norms = np.linalg.norm(centered, axis=1)
    if not np.all(np.isfinite(norms)):
        raise NumericalFCIError("Non-finite norms encountered after centering the local cloud.")
    if np.any(norms <= float(eps)):
        raise NumericalFCIError(
            "At least one local point collapsed to zero norm after centering; "
            "the local FCI normalization is ill-defined for this query/patch."
        )
    normalized = centered / norms[:, None]
    if not np.all(np.isfinite(normalized)):
        raise NumericalFCIError("Non-finite values encountered after local FCI normalization.")
    return normalized


def subsample_curve_points(
    radii: np.ndarray,
    rho_emp: np.ndarray,
    *,
    max_curve_points: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Evenly subsample the empirical curve for faster nonlinear fitting."""
    if int(max_curve_points) <= 0 or radii.shape[0] <= int(max_curve_points):
        return radii, rho_emp
    indices = np.unique(
        np.linspace(0, radii.shape[0] - 1, num=int(max_curve_points)).round().astype(np.int64)
    )
    return radii[indices], rho_emp[indices]


def build_empirical_fci_curve(
    local_cloud: np.ndarray,
    *,
    max_curve_points: int,
    eps: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray]:
    """Construct the empirical full correlation-integral curve for one local cloud.

    We follow the convention reported in the original paper's Methods section:
    after sorting all pairwise distances, the empirical density is stored as
    rho_emp[i] = i / num_pairs for i = 0, ..., num_pairs - 1.
    """
    normalized_cloud = preprocess_local_cloud_for_fci(local_cloud, eps=eps)
    pairwise_distances = torch.pdist(
        torch.as_tensor(normalized_cloud, dtype=torch.float64),
        p=2.0,
    ).cpu().numpy()
    pairwise_distances = np.asarray(pairwise_distances, dtype=np.float64)
    pairwise_distances = pairwise_distances[np.isfinite(pairwise_distances)]
    if pairwise_distances.size == 0:
        raise NumericalFCIError("The local cloud produced no finite pairwise distances.")
    pairwise_distances.sort()
    rho_emp = np.arange(pairwise_distances.size, dtype=np.float64) / float(pairwise_distances.size)
    pairwise_distances = np.clip(pairwise_distances, float(eps), None)
    pairwise_distances, rho_emp = subsample_curve_points(
        pairwise_distances,
        rho_emp,
        max_curve_points=int(max_curve_points),
    )
    if pairwise_distances.size == 0 or rho_emp.size == 0:
        raise NumericalFCIError("The empirical FCI curve is empty after subsampling.")
    if np.unique(pairwise_distances).size < 2:
        raise NumericalFCIError("The empirical FCI curve has fewer than 2 unique radii.")
    return pairwise_distances, rho_emp


def initialize_d_guess(radii: np.ndarray, rho_emp: np.ndarray) -> float:
    """Build a simple slope-based initialization for the nonlinear fit."""
    positive_mask = (radii > 0.0) & (rho_emp > 0.0) & np.isfinite(radii) & np.isfinite(rho_emp)
    if int(np.sum(positive_mask)) < 4:
        return 5.0
    r_positive = radii[positive_mask]
    rho_positive = rho_emp[positive_mask]
    take = min(max(4, r_positive.size // 5), r_positive.size)
    try:
        slope = np.polyfit(np.log(r_positive[:take]), np.log(rho_positive[:take]), 1)[0]
    except Exception:
        return 5.0
    if not np.isfinite(slope):
        return 5.0
    return float(np.clip(slope, 0.25, 512.0))


def fit_local_fci_curve(
    radii: np.ndarray,
    rho_emp: np.ndarray,
    *,
    fit_method: str,
    min_curve_points_for_fit: int,
) -> dict[str, float]:
    """Fit the local empirical FCI curve and return d_fit, r_s, and pointwise_fci_id."""
    radius_values = np.asarray(radii, dtype=np.float64)
    rho_values = np.asarray(rho_emp, dtype=np.float64)
    finite_mask = np.isfinite(radius_values) & np.isfinite(rho_values)
    radius_values = radius_values[finite_mask]
    rho_values = rho_values[finite_mask]
    if radius_values.size < int(min_curve_points_for_fit):
        raise NumericalFCIError(
            "The empirical FCI curve does not have enough finite points for the requested fit."
        )
    if np.unique(radius_values).size < 2 or np.unique(rho_values).size < 2:
        raise NumericalFCIError("The empirical FCI curve is too degenerate for nonlinear fitting.")

    lower_bounds = np.asarray([1e-3, 5e-2], dtype=np.float64)
    upper_bounds = np.asarray([4096.0, 4.0], dtype=np.float64)
    x0 = np.asarray(
        [
            initialize_d_guess(radius_values, rho_values),
            1.0,
        ],
        dtype=np.float64,
    )
    x0 = np.clip(x0, lower_bounds + 1e-6, upper_bounds - 1e-6)

    if str(fit_method) == "curve_fit":
        try:
            params, _ = curve_fit(
                fci_model,
                radius_values,
                rho_values,
                p0=x0,
                bounds=(lower_bounds, upper_bounds),
                maxfev=4000,
            )
        except Exception as exc:
            raise FitFailureError(f"curve_fit failed: {exc}") from exc
    else:
        def residuals(parameters: np.ndarray) -> np.ndarray:
            prediction = fci_model(radius_values, float(parameters[0]), float(parameters[1]))
            if not np.all(np.isfinite(prediction)):
                return np.full_like(radius_values, 1e6, dtype=np.float64)
            return prediction - rho_values

        try:
            result = least_squares(
                residuals,
                x0=x0,
                bounds=(lower_bounds, upper_bounds),
                max_nfev=400,
            )
        except Exception as exc:
            raise FitFailureError(f"least_squares failed: {exc}") from exc
        if not bool(result.success):
            raise FitFailureError(f"least_squares did not converge: {result.message}")
        params = result.x

    d_fit = float(params[0])
    r_s = float(params[1])
    if not np.isfinite(d_fit) or not np.isfinite(r_s) or d_fit <= 0.0 or r_s <= 0.0:
        raise FitFailureError(f"Invalid fitted parameters returned: d_fit={d_fit}, r_s={r_s}.")

    fitted_curve = fci_model(radius_values, d_fit, r_s)
    if not np.all(np.isfinite(fitted_curve)):
        raise FitFailureError("The fitted FCI model evaluated to non-finite values.")
    return {
        "d_fit": d_fit,
        "r_s": r_s,
        "pointwise_fci_id": float(d_fit + 1.0),
    }


def compute_local_pointwise_fci_id(
    query_point: np.ndarray,
    neighbor_points: np.ndarray,
    *,
    fit_method: str,
    max_curve_points: int,
    min_curve_points_for_fit: int,
    eps: float = 1e-12,
) -> float:
    """Compute one pointwise FCI estimate for one query / layer / reference-size / k tuple."""
    local_cloud = build_local_cloud_for_query(query_point, neighbor_points)
    radii, rho_emp = build_empirical_fci_curve(
        local_cloud,
        max_curve_points=int(max_curve_points),
        eps=eps,
    )
    fit_result = fit_local_fci_curve(
        radii,
        rho_emp,
        fit_method=fit_method,
        min_curve_points_for_fit=int(min_curve_points_for_fit),
    )
    return float(fit_result["pointwise_fci_id"])


def compute_pyfci_local_pointwise_fci_ids(
    query_point: np.ndarray,
    sorted_neighbor_points: np.ndarray,
    *,
    k_values: Sequence[int],
    pyfci_module: Any,
    random_seed: int | None,
) -> dict[int, float]:
    """Compute multiscale local FCI IDs with pyFCI while preserving our reference-only neighbours.

    ``pyFCI.local_FCI`` expects the center point to be a row of the same dataset
    and interprets each ``k`` as the local cloud size including that center.
    Our public output keeps ``k`` as the number of train/reference neighbours,
    so this adapter constructs ``[query, neighbour_1, ..., neighbour_k]`` and
    passes ``k + 1`` to pyFCI.
    """
    requested_k_values = [int(k_value) for k_value in k_values]
    if not requested_k_values:
        return {}
    unique_sorted_k_values = sorted(set(requested_k_values))
    max_k = max(unique_sorted_k_values)
    neighbors = np.asarray(sorted_neighbor_points, dtype=np.float64)
    if neighbors.ndim != 2:
        raise NumericalFCIError(f"sorted_neighbor_points must be rank-2; got shape {neighbors.shape}.")
    if int(neighbors.shape[0]) < int(max_k):
        raise NumericalFCIError(
            f"Need at least {max_k} sorted reference neighbours for pyFCI, got {neighbors.shape[0]}."
        )
    local_dataset = build_local_cloud_for_query(query_point, neighbors[:max_k])
    if not np.all(np.isfinite(local_dataset)):
        raise NumericalFCIError("pyFCI local dataset contains non-finite values.")

    pyfci_ks = [int(k_value) + 1 for k_value in unique_sorted_k_values]
    if random_seed is not None:
        np.random.seed(int(random_seed))
    try:
        local_result = pyfci_module.local_FCI(local_dataset, 0, pyfci_ks)
    except Exception as exc:
        raise FitFailureError(f"pyFCI.local_FCI failed: {exc}") from exc

    result_array = np.asarray(local_result, dtype=np.float64)
    if result_array.ndim != 2 or result_array.shape[1] < 3:
        raise FitFailureError(f"pyFCI.local_FCI returned an unexpected shape: {result_array.shape}.")
    if result_array.shape[0] != len(unique_sorted_k_values):
        raise FitFailureError(
            "pyFCI.local_FCI returned a different number of rows than requested k values: "
            f"{result_array.shape[0]} vs {len(unique_sorted_k_values)}."
        )

    output_by_unique_k: dict[int, float] = {}
    for requested_k, row in zip(unique_sorted_k_values, result_array):
        fitted_id = float(row[2])
        output_by_unique_k[int(requested_k)] = (
            fitted_id if np.isfinite(fitted_id) and fitted_id > 0.0 else float("nan")
        )
    return {int(k_value): output_by_unique_k[int(k_value)] for k_value in requested_k_values}


def compute_structural_nan_count(
    *,
    num_queries: int,
    num_layers: int,
    valid_k_mask: torch.Tensor,
) -> int:
    """Count NaNs introduced by structurally invalid reference-size/k combinations."""
    invalid_entries = int((~valid_k_mask).sum().item())
    return int(num_queries * num_layers * invalid_entries)


def compute_pointwise_fci_for_query_set(
    *,
    reference_source_reps: torch.Tensor,
    query_source_reps: torch.Tensor,
    ordered_train_reference_indices: torch.Tensor,
    reference_indices_by_size: dict[int, list[int]],
    reference_sizes_requested: Sequence[int],
    k_values_requested: Sequence[int],
    valid_reference_size_mask: torch.Tensor,
    valid_k_mask: torch.Tensor,
    layer_names: Sequence[str],
    device: torch.device,
    chunk_size: int,
    max_curve_points: int,
    fci_backend: str,
    fit_method: str,
    min_curve_points_for_fit: int,
    pyfci_module: Any | None,
    pyfci_random_seed: int | None,
    layer_indices: Sequence[int] | None = None,
    query_reference_indices: torch.Tensor | None = None,
) -> tuple[torch.Tensor, FCIComputationCounts]:
    """Compute pointwise FCI IDs for one query split.

    The train/reference subsets are assumed to be nested prefixes of
    ``ordered_train_reference_indices`` and therefore shared exactly between
    eval_known and eval_unknown.
    """
    num_queries = int(query_source_reps.shape[0])
    num_layers = int(query_source_reps.shape[1])
    output = torch.full(
        (num_queries, num_layers, len(reference_sizes_requested), len(k_values_requested)),
        float("nan"),
        dtype=torch.float32,
    )
    counts = FCIComputationCounts()

    valid_reference_sizes = [
        int(reference_size)
        for reference_size, is_valid in zip(reference_sizes_requested, valid_reference_size_mask.tolist())
        if is_valid
    ]
    max_valid_reference_size = max(valid_reference_sizes) if valid_reference_sizes else 0
    if max_valid_reference_size == 0:
        return output.contiguous(), counts

    ordered_reference_tensor = ordered_train_reference_indices[:max_valid_reference_size].cpu().long().contiguous()
    reference_position_by_index: dict[int, int] | None = None
    if query_reference_indices is not None:
        query_reference_indices = query_reference_indices.detach().cpu().long().contiguous()
        if int(query_reference_indices.numel()) != num_queries:
            raise ValueError(
                "query_reference_indices length must match the number of query representations: "
                f"{int(query_reference_indices.numel())} vs {num_queries}."
            )
        reference_position_by_index = {
            int(reference_index): int(position)
            for position, reference_index in enumerate(ordered_reference_tensor.tolist())
        }

    with torch.inference_mode():
        selected_layer_indices = list(range(len(layer_names))) if layer_indices is None else [int(value) for value in layer_indices]
        for layer_idx in tqdm(selected_layer_indices, desc="Layers", unit="layer"):
            reference_layer_cpu = (
                reference_source_reps.index_select(0, ordered_reference_tensor)[:, layer_idx, :]
                .detach()
                .cpu()
                .numpy()
                .astype(np.float64, copy=False)
            )
            reference_layer_device = torch.as_tensor(
                reference_layer_cpu,
                dtype=torch.float32,
                device=device,
            )

            for start in tqdm(
                range(0, num_queries, int(chunk_size)),
                desc=f"Query chunks (layer {layer_idx})",
                unit="chunk",
                leave=False,
            ):
                end = min(start + int(chunk_size), num_queries)
                query_chunk_cpu = (
                    query_source_reps[start:end, layer_idx, :]
                    .detach()
                    .cpu()
                    .numpy()
                    .astype(np.float64, copy=False)
                )
                query_chunk_device = torch.as_tensor(
                    query_chunk_cpu,
                    dtype=torch.float32,
                    device=device,
                )
                distance_matrix = torch.cdist(query_chunk_device, reference_layer_device, p=2.0)
                if reference_position_by_index is not None and query_reference_indices is not None:
                    chunk_reference_indices = query_reference_indices[start:end].tolist()
                    row_positions: list[int] = []
                    col_positions: list[int] = []
                    for row_offset, reference_index in enumerate(chunk_reference_indices):
                        column = reference_position_by_index.get(int(reference_index))
                        if column is not None:
                            row_positions.append(int(row_offset))
                            col_positions.append(int(column))
                    if row_positions:
                        distance_matrix[
                            torch.tensor(row_positions, dtype=torch.long, device=device),
                            torch.tensor(col_positions, dtype=torch.long, device=device),
                        ] = float("inf")

                for ref_idx, reference_size in enumerate(reference_sizes_requested):
                    if not bool(valid_reference_size_mask[ref_idx].item()):
                        continue

                    valid_k_positions = [
                        k_idx
                        for k_idx, is_valid in enumerate(valid_k_mask[ref_idx].tolist())
                        if is_valid
                    ]
                    if not valid_k_positions:
                        continue

                    max_k_for_size = max(int(k_values_requested[k_idx]) for k_idx in valid_k_positions)
                    distance_subset = distance_matrix[:, : int(reference_size)]
                    topk = torch.topk(
                        distance_subset,
                        k=int(max_k_for_size),
                        dim=1,
                        largest=False,
                        sorted=True,
                    )
                    neighbor_indices = topk.indices.detach().cpu().numpy()
                    reference_subset_cpu = reference_layer_cpu[: int(reference_size)]

                    for row_offset in range(end - start):
                        query_point = query_chunk_cpu[row_offset]
                        global_query_index = start + row_offset
                        if str(fci_backend) == FCI_BACKEND_PYFCI_LOCAL:
                            if pyfci_module is None:
                                raise RuntimeError("pyfci_module is required when fci_backend='pyfci_local'.")
                            requested_ks_for_row = [
                                int(k_values_requested[k_idx])
                                for k_idx in valid_k_positions
                            ]
                            max_k_for_row = max(requested_ks_for_row)
                            neighbor_points = reference_subset_cpu[neighbor_indices[row_offset, :max_k_for_row]]
                            pyfci_call_failed = False
                            try:
                                pointwise_by_k = compute_pyfci_local_pointwise_fci_ids(
                                    query_point,
                                    neighbor_points,
                                    k_values=requested_ks_for_row,
                                    pyfci_module=pyfci_module,
                                    random_seed=pyfci_seed_for_call(
                                        pyfci_random_seed,
                                        global_query_index=global_query_index,
                                        layer_idx=layer_idx,
                                        ref_idx=ref_idx,
                                    ),
                                )
                            except FitFailureError:
                                counts.fit_failures += len(valid_k_positions)
                                pyfci_call_failed = True
                                pointwise_by_k = {
                                    int(k_values_requested[k_idx]): float("nan")
                                    for k_idx in valid_k_positions
                                }
                            except NumericalFCIError:
                                counts.numerical += len(valid_k_positions)
                                pyfci_call_failed = True
                                pointwise_by_k = {
                                    int(k_values_requested[k_idx]): float("nan")
                                    for k_idx in valid_k_positions
                                }
                            for k_idx in valid_k_positions:
                                k_value = int(k_values_requested[k_idx])
                                pointwise_fci_id = float(pointwise_by_k.get(k_value, float("nan")))
                                if not pyfci_call_failed and not np.isfinite(pointwise_fci_id):
                                    counts.fit_failures += 1
                                output[global_query_index, layer_idx, ref_idx, k_idx] = pointwise_fci_id
                        else:
                            for k_idx in valid_k_positions:
                                k_value = int(k_values_requested[k_idx])
                                neighbor_points = reference_subset_cpu[neighbor_indices[row_offset, :k_value]]
                                try:
                                    pointwise_fci_id = compute_local_pointwise_fci_id(
                                        query_point,
                                        neighbor_points,
                                        fit_method=fit_method,
                                        max_curve_points=int(max_curve_points),
                                        min_curve_points_for_fit=int(min_curve_points_for_fit),
                                    )
                                except FitFailureError:
                                    counts.fit_failures += 1
                                    pointwise_fci_id = float("nan")
                                except NumericalFCIError:
                                    counts.numerical += 1
                                    pointwise_fci_id = float("nan")
                                output[global_query_index, layer_idx, ref_idx, k_idx] = float(pointwise_fci_id)

    return output.contiguous(), counts


def repeat_optional_tensor_column(value: torch.Tensor | None, rows_per_query: int) -> np.ndarray | None:
    """Expand an optional per-query tensor column to long-table row count."""
    if value is None:
        return None
    return np.repeat(value.detach().cpu().numpy(), rows_per_query)


def repeat_optional_string_list(value: Sequence[str] | None, rows_per_query: int) -> np.ndarray | None:
    """Expand an optional per-query string column to long-table row count."""
    if value is None:
        return None
    return np.repeat(np.asarray(list(value), dtype=object), rows_per_query)


def build_long_dataframe(
    *,
    pointwise_fci_chunk: torch.Tensor,
    query_start: int,
    chunk_metadata: dict[str, Any],
    layer_names: Sequence[str],
    reference_sizes_requested: Sequence[int],
    k_values_requested: Sequence[int],
    valid_reference_size_mask: torch.Tensor,
    valid_k_mask: torch.Tensor,
    model_name: str | None,
    revision: str | None,
    reference_setup_signature: str,
    query_selection_signature: str,
    split_setup_signature: str,
    save_nan_rows: bool,
    layer_indices: Sequence[int] | None = None,
) -> pd.DataFrame:
    """Build one chunk of the long-format output table."""
    num_queries = int(pointwise_fci_chunk.shape[0])
    num_layers = len(layer_names)
    num_reference_sizes = len(reference_sizes_requested)
    num_k = len(k_values_requested)
    rows_per_query = num_layers * num_reference_sizes * num_k
    total_rows = num_queries * rows_per_query

    layer_idx_array = np.tile(
        np.repeat(np.arange(num_layers, dtype=np.int64), num_reference_sizes * num_k),
        num_queries,
    )
    layer_name_array = np.tile(
        np.repeat(np.asarray(layer_names, dtype=object), num_reference_sizes * num_k),
        num_queries,
    )
    reference_size_array = np.tile(
        np.repeat(np.asarray(reference_sizes_requested, dtype=np.int64), num_k),
        num_queries * num_layers,
    )
    k_array = np.tile(
        np.asarray(k_values_requested, dtype=np.int64),
        num_queries * num_layers * num_reference_sizes,
    )
    valid_reference_array = np.tile(
        np.repeat(valid_reference_size_mask.cpu().numpy().astype(bool), num_k),
        num_queries * num_layers,
    )
    valid_k_array = np.tile(
        valid_k_mask.cpu().numpy().astype(bool).reshape(-1),
        num_queries * num_layers,
    )

    data: dict[str, Any] = {
        "query_index": np.repeat(
            np.arange(query_start, query_start + num_queries, dtype=np.int64),
            rows_per_query,
        ),
        "text": np.repeat(np.asarray(chunk_metadata["texts"], dtype=object), rows_per_query),
        "sample_kind": np.full(total_rows, chunk_metadata["sample_kind"], dtype=object),
        "layer_idx": layer_idx_array,
        "layer_name": layer_name_array,
        "reference_size": reference_size_array,
        "k": k_array,
        "pointwise_fci_id": pointwise_fci_chunk.detach().cpu().numpy().reshape(-1),
        "is_valid_reference_size": valid_reference_array,
        "is_valid_k_for_reference_size": valid_k_array,
        "reference_setup_signature": np.full(total_rows, reference_setup_signature, dtype=object),
        "query_selection_signature": np.full(total_rows, query_selection_signature, dtype=object),
        "split_setup_signature": np.full(total_rows, split_setup_signature, dtype=object),
    }

    source_name = chunk_metadata.get("source_name")
    if source_name is not None:
        data["source_name"] = np.full(total_rows, source_name, dtype=object)
    source_repo_or_file = chunk_metadata.get("source_repo_or_file")
    if source_repo_or_file is not None:
        data["source_repo_or_file"] = np.full(total_rows, source_repo_or_file, dtype=object)
    source_config = chunk_metadata.get("source_config")
    if source_config is not None:
        data["source_config"] = np.full(total_rows, source_config, dtype=object)
    source_split = chunk_metadata.get("source_split")
    if source_split is not None:
        data["source_split"] = np.full(total_rows, source_split, dtype=object)
    source_is_official_split = chunk_metadata.get("source_is_official_split")
    if source_is_official_split is not None:
        data["source_is_official_split"] = np.full(total_rows, bool(source_is_official_split), dtype=bool)

    pile_set_name = repeat_optional_string_list(chunk_metadata.get("pile_set_name"), rows_per_query)
    if pile_set_name is not None:
        data["pile_set_name"] = pile_set_name

    num_chars = repeat_optional_tensor_column(chunk_metadata.get("num_chars"), rows_per_query)
    if num_chars is not None:
        data["num_chars"] = num_chars
    num_words = repeat_optional_tensor_column(chunk_metadata.get("num_words"), rows_per_query)
    if num_words is not None:
        data["num_words"] = num_words
    num_tokens = repeat_optional_tensor_column(chunk_metadata.get("num_tokens"), rows_per_query)
    if num_tokens is not None:
        data["num_tokens"] = num_tokens

    source_doc_indices = repeat_optional_tensor_column(chunk_metadata.get("source_doc_indices"), rows_per_query)
    if source_doc_indices is not None:
        data["source_doc_indices"] = source_doc_indices
    source_sentence_indices_in_doc = repeat_optional_tensor_column(
        chunk_metadata.get("source_sentence_indices_in_doc"),
        rows_per_query,
    )
    if source_sentence_indices_in_doc is not None:
        data["source_sentence_indices_in_doc"] = source_sentence_indices_in_doc

    if model_name is not None:
        data["model_name"] = np.full(total_rows, model_name, dtype=object)
    if revision is not None:
        data["revision"] = np.full(total_rows, revision, dtype=object)

    dataframe = pd.DataFrame(data)
    if layer_indices is not None:
        selected_layers = {int(layer_idx) for layer_idx in layer_indices}
        dataframe = dataframe.loc[dataframe["layer_idx"].isin(selected_layers)].reset_index(drop=True)
    if not save_nan_rows:
        dataframe = dataframe.loc[dataframe["is_valid_k_for_reference_size"]].reset_index(drop=True)
    return dataframe


def write_long_outputs(
    *,
    pointwise_fci_id: torch.Tensor,
    output_parquet_path: Path,
    output_csv_path: Path,
    query_metadata: dict[str, Any],
    layer_names: Sequence[str],
    reference_sizes_requested: Sequence[int],
    k_values_requested: Sequence[int],
    valid_reference_size_mask: torch.Tensor,
    valid_k_mask: torch.Tensor,
    model_name: str | None,
    revision: str | None,
    reference_setup_signature: str,
    query_selection_signature: str,
    split_setup_signature: str,
    save_nan_rows: bool,
    layer_indices: Sequence[int] | None = None,
) -> pd.DataFrame:
    """Stream the long-format parquet/csv outputs in query chunks."""
    preview_frames: list[pd.DataFrame] = []
    parquet_writer = None
    csv_header = True

    try:
        for start in tqdm(
            range(0, int(pointwise_fci_id.shape[0]), DEFAULT_LONG_QUERY_CHUNK),
            desc=f"Long table ({query_metadata['sample_kind']})",
            unit="chunk",
        ):
            end = min(start + DEFAULT_LONG_QUERY_CHUNK, int(pointwise_fci_id.shape[0]))
            chunk_metadata = {
                "texts": query_metadata["texts"][start:end],
                "sample_kind": query_metadata["sample_kind"],
                "source_name": query_metadata.get("source_name"),
                "source_repo_or_file": query_metadata.get("source_repo_or_file"),
                "source_config": query_metadata.get("source_config"),
                "source_split": query_metadata.get("source_split"),
                "source_is_official_split": query_metadata.get("source_is_official_split"),
                "source_doc_indices": (
                    query_metadata["source_doc_indices"][start:end]
                    if query_metadata.get("source_doc_indices") is not None
                    else None
                ),
                "source_sentence_indices_in_doc": (
                    query_metadata["source_sentence_indices_in_doc"][start:end]
                    if query_metadata.get("source_sentence_indices_in_doc") is not None
                    else None
                ),
                "num_chars": query_metadata["num_chars"][start:end] if query_metadata.get("num_chars") is not None else None,
                "num_words": query_metadata["num_words"][start:end] if query_metadata.get("num_words") is not None else None,
                "num_tokens": query_metadata["num_tokens"][start:end] if query_metadata.get("num_tokens") is not None else None,
                "pile_set_name": (
                    query_metadata["pile_set_name"][start:end]
                    if query_metadata.get("pile_set_name") is not None
                    else None
                ),
            }
            dataframe = build_long_dataframe(
                pointwise_fci_chunk=pointwise_fci_id[start:end],
                query_start=start,
                chunk_metadata=chunk_metadata,
                layer_names=layer_names,
                reference_sizes_requested=reference_sizes_requested,
                k_values_requested=k_values_requested,
                valid_reference_size_mask=valid_reference_size_mask,
                valid_k_mask=valid_k_mask,
                model_name=model_name,
                revision=revision,
                reference_setup_signature=reference_setup_signature,
                query_selection_signature=query_selection_signature,
                split_setup_signature=split_setup_signature,
                save_nan_rows=save_nan_rows,
                layer_indices=layer_indices,
            )
            if dataframe.empty:
                continue
            if sum(len(frame) for frame in preview_frames) < DEFAULT_PREVIEW_ROWS:
                preview_frames.append(
                    dataframe.head(DEFAULT_PREVIEW_ROWS - sum(len(frame) for frame in preview_frames))
                )

            table = pa.Table.from_pandas(dataframe, preserve_index=False)
            if parquet_writer is None:
                parquet_writer = pq.ParquetWriter(output_parquet_path, table.schema)
            parquet_writer.write_table(table)
            dataframe.to_csv(
                output_csv_path,
                mode="w" if csv_header else "a",
                header=csv_header,
                index=False,
            )
            csv_header = False
    finally:
        if parquet_writer is not None:
            parquet_writer.close()

    if preview_frames:
        return pd.concat(preview_frames, ignore_index=True).head(DEFAULT_PREVIEW_ROWS)

    empty_columns = [
        "query_index",
        "text",
        "sample_kind",
        "layer_idx",
        "layer_name",
        "reference_size",
        "k",
        "pointwise_fci_id",
        "is_valid_reference_size",
        "is_valid_k_for_reference_size",
        "reference_setup_signature",
        "query_selection_signature",
        "split_setup_signature",
    ]
    empty_df = pd.DataFrame(columns=empty_columns)
    pq.write_table(pa.Table.from_pandas(empty_df, preserve_index=False), output_parquet_path)
    empty_df.to_csv(output_csv_path, index=False)
    return empty_df


def save_split_outputs(
    *,
    output_dir: Path,
    split_name: str,
    pointwise_fci_id: torch.Tensor,
    query_metadata: dict[str, Any],
    reference_setup: ReferenceSetup,
    common_metadata: dict[str, Any],
    train_split: SplitData,
    query_split: SplitData,
    fci_backend: str,
    fit_method: str,
    pyfci_random_seed: int | None,
    min_local_points_for_fci_fit: int,
    min_curve_points_for_fit: int,
    counts: FCIComputationCounts,
    include_reference_texts_in_output: bool,
    save_nan_rows: bool,
) -> tuple[dict[str, Any], dict[str, Path], pd.DataFrame]:
    """Save one split-specific tensor bundle and long-format outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pt_path = output_dir / f"{split_name}_pointwise_fci.pt"
    parquet_path = output_dir / f"{split_name}_pointwise_fci_long.parquet"
    csv_path = output_dir / f"{split_name}_pointwise_fci_long.csv"
    reference_setup_signature = build_reference_setup_signature(reference_setup)
    query_selection_signature = build_query_selection_signature(
        query_indices=query_metadata["query_indices"],
        sample_kind=str(query_metadata["sample_kind"]),
        query_source_name=query_split.source_name,
        query_source_repo_or_file=query_split.source_repo_or_file,
    )
    split_setup_signature = build_split_setup_signature(
        reference_setup_signature=reference_setup_signature,
        query_selection_signature=query_selection_signature,
        common_metadata=common_metadata,
    )

    payload: dict[str, Any] = {
        "pointwise_fci_id": pointwise_fci_id.contiguous(),
        "reference_sizes_requested": list(reference_setup.reference_sizes_requested),
        "k_values_requested": list(reference_setup.k_values_requested),
        "valid_reference_size_mask": reference_setup.valid_reference_size_mask.clone().contiguous(),
        "valid_k_mask": reference_setup.valid_k_mask.clone().contiguous(),
        "reference_indices_by_size": {
            int(reference_size): [int(index) for index in indices]
            for reference_size, indices in reference_setup.reference_indices_by_size.items()
        },
        "query_indices": query_metadata["query_indices"].clone().contiguous(),
        "query_texts": list(query_metadata["texts"]),
        "query_sample_kind": query_metadata["sample_kind"],
        "layer_names": list(common_metadata["layer_names"]),
        "num_queries": int(pointwise_fci_id.shape[0]),
        "num_reference_pool": int(train_split.num_examples),
        "seed": int(common_metadata["seed"]),
        "fci_local_adaptation": True,
        "fci_backend": str(fci_backend),
        "fit_method": str(fit_method),
        "pyfci_random_seed": pyfci_random_seed,
        "min_local_points_for_fci_fit": int(min_local_points_for_fci_fit),
        "min_curve_points_for_fit": int(min_curve_points_for_fit),
        "nan_count_structural": int(counts.structural),
        "nan_count_fit_failures": int(counts.fit_failures),
        "nan_count_numerical": int(counts.numerical),
        "model_name": common_metadata.get("model_name"),
        "revision": common_metadata.get("revision"),
        "include_embeddings": bool(common_metadata["include_embeddings"]),
        "hidden_size": int(common_metadata["hidden_size"]),
        "num_layers": int(common_metadata["num_layers"]),
        "reference_source_name": train_split.source_name,
        "reference_source_repo_or_file": train_split.source_repo_or_file,
        "reference_source_config": train_split.source_config,
        "reference_source_split": train_split.source_split,
        "reference_source_is_official_split": train_split.source_is_official_split,
        "source_name": query_split.source_name,
        "source_repo_or_file": query_split.source_repo_or_file,
        "source_config": query_split.source_config,
        "source_split": query_split.source_split,
        "source_is_official_split": query_split.source_is_official_split,
        "local_adaptation_notes": backend_notes(str(fci_backend)),
        "reference_setup_signature": reference_setup_signature,
        "query_selection_signature": query_selection_signature,
        "split_setup_signature": split_setup_signature,
        "computed_layer_indices": list(common_metadata.get("computed_layer_indices", range(int(common_metadata["num_layers"])))),
        "computed_layer_numbers": list(common_metadata.get("computed_layer_numbers", range(1, int(common_metadata["num_layers"]) + 1))),
    }

    if query_split.source_doc_indices is not None:
        payload["source_doc_indices"] = query_split.source_doc_indices.clone().contiguous()
    if query_split.source_sentence_indices_in_doc is not None:
        payload["source_sentence_indices_in_doc"] = (
            query_split.source_sentence_indices_in_doc.clone().contiguous()
        )
    if query_split.num_chars is not None:
        payload["num_chars"] = query_split.num_chars.clone().contiguous()
    if query_split.num_words is not None:
        payload["num_words"] = query_split.num_words.clone().contiguous()
    if query_split.num_tokens is not None:
        payload["num_tokens"] = query_split.num_tokens.clone().contiguous()
    if query_split.pile_set_name is not None:
        payload["pile_set_name"] = list(query_split.pile_set_name)
    if include_reference_texts_in_output:
        payload["reference_texts"] = list(train_split.texts)

    torch.save(payload, pt_path)

    preview_df = write_long_outputs(
        pointwise_fci_id=pointwise_fci_id,
        output_parquet_path=parquet_path,
        output_csv_path=csv_path,
        query_metadata=query_metadata,
        layer_names=common_metadata["layer_names"],
        reference_sizes_requested=reference_setup.reference_sizes_requested,
        k_values_requested=reference_setup.k_values_requested,
        valid_reference_size_mask=reference_setup.valid_reference_size_mask,
        valid_k_mask=reference_setup.valid_k_mask,
        model_name=common_metadata.get("model_name"),
        revision=common_metadata.get("revision"),
        reference_setup_signature=reference_setup_signature,
        query_selection_signature=query_selection_signature,
        split_setup_signature=split_setup_signature,
        save_nan_rows=save_nan_rows,
        layer_indices=common_metadata.get("computed_layer_indices"),
    )

    return payload, {"pt": pt_path, "parquet": parquet_path, "csv": csv_path}, preview_df


def save_combined_output(
    *,
    output_dir: Path,
    reference_setup: ReferenceSetup,
    common_metadata: dict[str, Any],
    train_split: SplitData,
    eval_known_payload: dict[str, Any],
    eval_unknown_payload: dict[str, Any],
    reference_payload: dict[str, Any] | None,
    fci_backend: str,
    fit_method: str,
    pyfci_random_seed: int | None,
) -> Path:
    """Save a combined bundle with shared reference info plus both eval splits."""
    combined_path = output_dir / "combined_pointwise_fci.pt"
    reference_setup_signature = build_reference_setup_signature(reference_setup)
    reference_info = {
        "train_num_reference_pool": int(train_split.num_examples),
        "reference_indices_by_size": {
            int(reference_size): [int(index) for index in indices]
            for reference_size, indices in reference_setup.reference_indices_by_size.items()
        },
        "reference_sizes_requested": list(reference_setup.reference_sizes_requested),
        "k_values_requested": list(reference_setup.k_values_requested),
        "valid_reference_size_mask": reference_setup.valid_reference_size_mask.clone().contiguous(),
        "valid_k_mask": reference_setup.valid_k_mask.clone().contiguous(),
        "model_name": common_metadata.get("model_name"),
        "revision": common_metadata.get("revision"),
        "include_embeddings": bool(common_metadata["include_embeddings"]),
        "hidden_size": int(common_metadata["hidden_size"]),
        "num_layers": int(common_metadata["num_layers"]),
        "layer_names": list(common_metadata["layer_names"]),
        "computed_layer_indices": list(common_metadata.get("computed_layer_indices", range(int(common_metadata["num_layers"])))),
        "computed_layer_numbers": list(common_metadata.get("computed_layer_numbers", range(1, int(common_metadata["num_layers"]) + 1))),
        "reference_source_name": train_split.source_name,
        "reference_source_repo_or_file": train_split.source_repo_or_file,
        "reference_source_config": train_split.source_config,
        "reference_source_split": train_split.source_split,
        "reference_source_is_official_split": train_split.source_is_official_split,
        "fci_local_adaptation": True,
        "fci_backend": str(fci_backend),
        "fit_method": str(fit_method),
        "pyfci_random_seed": pyfci_random_seed,
        "reference_setup_signature": reference_setup_signature,
        "notes": backend_notes(str(fci_backend)),
    }
    payload = {
        "reference_info": reference_info,
        "eval_known": eval_known_payload,
        "eval_unknown": eval_unknown_payload,
    }
    if reference_payload is not None:
        payload["reference"] = reference_payload
    torch.save(payload, combined_path)
    return combined_path


def print_dataframe_preview(title: str, dataframe: pd.DataFrame) -> None:
    """Print a compact preview of a long-format dataframe."""
    print(title)
    if dataframe.empty:
        print("  <empty>")
        return
    print(dataframe.to_string(index=False))


def print_example_commands() -> None:
    """Print example CLI invocations for both supported input modes."""
    print("\nExample commands:")
    print("python compute_train_reference_eval_known_unknown_pointwise_fci_id.py \\")
    print("  --seen_pt outputs/local_seen_unseen_100/seen_last_token_reps.pt \\")
    print("  --unseen_pt outputs/local_seen_unseen_100/unseen_last_token_reps.pt \\")
    print("  --output_dir outputs/local_seen_unseen_100_fci_aligned \\")
    print("  --reference_count 15000 \\")
    print("  --eval_known_count 2000 \\")
    print("  --reference_sizes \"500,1000,2000,5000,7500,10000,12000,15000\" \\")
    print("  --k_values \"5,10,15,20,25,30,35,50,70,100,150,200,250,300,350,500,750,1000\" \\")
    print("  --seed 42 \\")
    print("  --reuse_reference_setup_pt outputs/local_seen_unseen_100_mle_ess_aligned/combined_pointwise_mle.pt \\")
    print("  --fci_backend pyfci_local \\")
    print("  --pyfci_random_seed 42 \\")
    print("  --save_combined_pt")
    print("")
    print("python compute_train_reference_eval_known_unknown_pointwise_fci_id.py \\")
    print("  --combined_pt outputs/pilecc_train_known_unknown/combined_last_token_reps.pt \\")
    print("  --output_dir outputs/pilecc_train_known_unknown_fci \\")
    print("  --fci_backend pyfci_local \\")
    print("  --save_combined_pt")
    print("")
    print("python compute_train_reference_eval_known_unknown_pointwise_fci_id.py \\")
    print("  --train_pt outputs/pilecc_train_known_unknown/train_last_token_reps.pt \\")
    print("  --eval_known_pt outputs/pilecc_train_known_unknown/eval_known_last_token_reps.pt \\")
    print("  --eval_unknown_pt outputs/pilecc_train_known_unknown/eval_unknown_last_token_reps.pt \\")
    print("  --output_dir outputs/pilecc_train_known_unknown_fci \\")
    print("  --reuse_reference_setup_pt outputs/pilecc_train_known_unknown_mle/eval_known_pointwise_mle.pt \\")
    print("  --fci_backend pyfci_local \\")
    print("  --save_combined_pt")


def main() -> None:
    """Entry point."""
    args = parse_args()
    if IMPORT_ERROR is not None:
        raise ModuleNotFoundError(
            "Missing required package(s). Install them with "
            "`python3 -m pip install -r requirements.txt`."
        ) from IMPORT_ERROR

    reference_sizes_requested = parse_int_list(args.reference_sizes, "reference_sizes")
    k_values_requested = parse_int_list(args.k_values, "k_values")
    device = resolve_device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError(f"Requested CUDA device {device}, but CUDA is not available.")
    pyfci_module = load_pyfci_module() if str(args.fci_backend) == FCI_BACKEND_PYFCI_LOCAL else None

    loaded_inputs = resolve_input_mode(args)
    common_metadata = validate_compatible_rep_shapes(loaded_inputs)
    common_metadata["seed"] = int(args.seed)
    layer_indices = parse_layer_indices(
        args.layers,
        int(common_metadata["num_layers"]),
        common_metadata["layer_names"],
    )
    common_metadata["computed_layer_indices"] = [int(layer_idx) for layer_idx in layer_indices]
    common_metadata["computed_layer_numbers"] = layer_numbers_from_indices(
        layer_indices,
        common_metadata["layer_names"],
    )

    (
        valid_reference_size_mask,
        valid_k_mask,
        invalid_reference_sizes,
        invalid_k_by_reference_size,
    ) = build_validity_masks(
        num_reference_pool=loaded_inputs.train.num_examples,
        reference_sizes=reference_sizes_requested,
        k_values=k_values_requested,
        min_local_points_for_fci_fit=int(args.min_local_points_for_fci_fit),
        min_curve_points_for_fit=int(args.min_curve_points_for_fit),
        strict_reference_sizes=bool(args.strict_reference_sizes),
        strict_k_values=bool(args.strict_k_values),
    )
    reused_reference_setup_path = (
        Path(args.reuse_reference_setup_pt).expanduser()
        if args.reuse_reference_setup_pt is not None
        else None
    )
    if reused_reference_setup_path is not None:
        ordered_train_reference_indices, reference_indices_by_size = load_reference_setup_override(
            path=reused_reference_setup_path,
            num_reference_pool=loaded_inputs.train.num_examples,
            reference_sizes_requested=reference_sizes_requested,
            k_values_requested=k_values_requested,
            valid_reference_size_mask=valid_reference_size_mask,
            valid_k_mask=valid_k_mask,
        )
    else:
        ordered_train_reference_indices, reference_indices_by_size = build_nested_reference_sets(
            loaded_inputs.train.num_examples,
            reference_sizes_requested,
            valid_reference_size_mask,
            int(args.seed),
        )
    reference_setup = ReferenceSetup(
        ordered_train_reference_indices=ordered_train_reference_indices,
        reference_indices_by_size=reference_indices_by_size,
        reference_sizes_requested=reference_sizes_requested,
        k_values_requested=k_values_requested,
        valid_reference_size_mask=valid_reference_size_mask,
        valid_k_mask=valid_k_mask,
        invalid_reference_sizes=invalid_reference_sizes,
        invalid_k_by_reference_size=invalid_k_by_reference_size,
    )

    eval_known_query_metadata = gather_query_metadata(loaded_inputs.eval_known)
    eval_unknown_query_metadata = gather_query_metadata(loaded_inputs.eval_unknown)
    reference_query_metadata = gather_query_metadata(loaded_inputs.train) if bool(args.compute_reference_queries) else None

    eval_known_counts = FCIComputationCounts(
        structural=compute_structural_nan_count(
            num_queries=loaded_inputs.eval_known.num_examples,
            num_layers=len(layer_indices),
            valid_k_mask=reference_setup.valid_k_mask,
        )
    )
    eval_unknown_counts = FCIComputationCounts(
        structural=compute_structural_nan_count(
            num_queries=loaded_inputs.eval_unknown.num_examples,
            num_layers=len(layer_indices),
            valid_k_mask=reference_setup.valid_k_mask,
        )
    )
    reference_counts = (
        FCIComputationCounts(
            structural=compute_structural_nan_count(
                num_queries=loaded_inputs.train.num_examples,
                num_layers=len(layer_indices),
                valid_k_mask=reference_setup.valid_k_mask,
            )
        )
        if bool(args.compute_reference_queries)
        else None
    )

    eval_known_pointwise_fci_id, eval_known_runtime_counts = compute_pointwise_fci_for_query_set(
        reference_source_reps=loaded_inputs.train.reps,
        query_source_reps=loaded_inputs.eval_known.reps,
        ordered_train_reference_indices=reference_setup.ordered_train_reference_indices,
        reference_indices_by_size=reference_setup.reference_indices_by_size,
        reference_sizes_requested=reference_setup.reference_sizes_requested,
        k_values_requested=reference_setup.k_values_requested,
        valid_reference_size_mask=reference_setup.valid_reference_size_mask,
        valid_k_mask=reference_setup.valid_k_mask,
        layer_names=common_metadata["layer_names"],
        device=device,
        chunk_size=int(args.chunk_size),
        max_curve_points=int(args.max_curve_points),
        fci_backend=str(args.fci_backend),
        fit_method=str(args.fit_method),
        min_curve_points_for_fit=int(args.min_curve_points_for_fit),
        pyfci_module=pyfci_module,
        pyfci_random_seed=args.pyfci_random_seed,
        layer_indices=layer_indices,
    )
    eval_known_counts.fit_failures += eval_known_runtime_counts.fit_failures
    eval_known_counts.numerical += eval_known_runtime_counts.numerical

    eval_unknown_pointwise_fci_id, eval_unknown_runtime_counts = compute_pointwise_fci_for_query_set(
        reference_source_reps=loaded_inputs.train.reps,
        query_source_reps=loaded_inputs.eval_unknown.reps,
        ordered_train_reference_indices=reference_setup.ordered_train_reference_indices,
        reference_indices_by_size=reference_setup.reference_indices_by_size,
        reference_sizes_requested=reference_setup.reference_sizes_requested,
        k_values_requested=reference_setup.k_values_requested,
        valid_reference_size_mask=reference_setup.valid_reference_size_mask,
        valid_k_mask=reference_setup.valid_k_mask,
        layer_names=common_metadata["layer_names"],
        device=device,
        chunk_size=int(args.chunk_size),
        max_curve_points=int(args.max_curve_points),
        fci_backend=str(args.fci_backend),
        fit_method=str(args.fit_method),
        min_curve_points_for_fit=int(args.min_curve_points_for_fit),
        pyfci_module=pyfci_module,
        pyfci_random_seed=args.pyfci_random_seed,
        layer_indices=layer_indices,
    )
    eval_unknown_counts.fit_failures += eval_unknown_runtime_counts.fit_failures
    eval_unknown_counts.numerical += eval_unknown_runtime_counts.numerical

    reference_pointwise_fci_id = None
    if bool(args.compute_reference_queries):
        if reference_counts is None:
            raise RuntimeError("reference_counts should be initialized when --compute_reference_queries is set.")
        reference_pointwise_fci_id, reference_runtime_counts = compute_pointwise_fci_for_query_set(
            reference_source_reps=loaded_inputs.train.reps,
            query_source_reps=loaded_inputs.train.reps,
            ordered_train_reference_indices=reference_setup.ordered_train_reference_indices,
            reference_indices_by_size=reference_setup.reference_indices_by_size,
            reference_sizes_requested=reference_setup.reference_sizes_requested,
            k_values_requested=reference_setup.k_values_requested,
            valid_reference_size_mask=reference_setup.valid_reference_size_mask,
            valid_k_mask=reference_setup.valid_k_mask,
            layer_names=common_metadata["layer_names"],
            device=device,
            chunk_size=int(args.chunk_size),
            max_curve_points=int(args.max_curve_points),
            fci_backend=str(args.fci_backend),
            fit_method=str(args.fit_method),
            min_curve_points_for_fit=int(args.min_curve_points_for_fit),
            pyfci_module=pyfci_module,
            pyfci_random_seed=args.pyfci_random_seed,
            layer_indices=layer_indices,
            query_reference_indices=torch.arange(loaded_inputs.train.num_examples, dtype=torch.long),
        )
        reference_counts.fit_failures += reference_runtime_counts.fit_failures
        reference_counts.numerical += reference_runtime_counts.numerical

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    eval_known_payload, eval_known_paths, eval_known_preview = save_split_outputs(
        output_dir=output_dir,
        split_name="eval_known",
        pointwise_fci_id=eval_known_pointwise_fci_id,
        query_metadata=eval_known_query_metadata,
        reference_setup=reference_setup,
        common_metadata=common_metadata,
        train_split=loaded_inputs.train,
        query_split=loaded_inputs.eval_known,
        fci_backend=str(args.fci_backend),
        fit_method=str(args.fit_method),
        pyfci_random_seed=args.pyfci_random_seed,
        min_local_points_for_fci_fit=int(args.min_local_points_for_fci_fit),
        min_curve_points_for_fit=int(args.min_curve_points_for_fit),
        counts=eval_known_counts,
        include_reference_texts_in_output=bool(args.include_reference_texts_in_output),
        save_nan_rows=bool(args.save_nan_rows),
    )
    eval_unknown_payload, eval_unknown_paths, eval_unknown_preview = save_split_outputs(
        output_dir=output_dir,
        split_name="eval_unknown",
        pointwise_fci_id=eval_unknown_pointwise_fci_id,
        query_metadata=eval_unknown_query_metadata,
        reference_setup=reference_setup,
        common_metadata=common_metadata,
        train_split=loaded_inputs.train,
        query_split=loaded_inputs.eval_unknown,
        fci_backend=str(args.fci_backend),
        fit_method=str(args.fit_method),
        pyfci_random_seed=args.pyfci_random_seed,
        min_local_points_for_fci_fit=int(args.min_local_points_for_fci_fit),
        min_curve_points_for_fit=int(args.min_curve_points_for_fit),
        counts=eval_unknown_counts,
        include_reference_texts_in_output=bool(args.include_reference_texts_in_output),
        save_nan_rows=bool(args.save_nan_rows),
    )

    reference_payload = None
    reference_paths = None
    reference_preview = None
    if reference_pointwise_fci_id is not None:
        if reference_query_metadata is None or reference_counts is None:
            raise RuntimeError("Reference query metadata/counts should exist when reference outputs are computed.")
        reference_payload, reference_paths, reference_preview = save_split_outputs(
            output_dir=output_dir,
            split_name="reference",
            pointwise_fci_id=reference_pointwise_fci_id,
            query_metadata=reference_query_metadata,
            reference_setup=reference_setup,
            common_metadata=common_metadata,
            train_split=loaded_inputs.train,
            query_split=loaded_inputs.train,
            fci_backend=str(args.fci_backend),
            fit_method=str(args.fit_method),
            pyfci_random_seed=args.pyfci_random_seed,
            min_local_points_for_fci_fit=int(args.min_local_points_for_fci_fit),
            min_curve_points_for_fit=int(args.min_curve_points_for_fit),
            counts=reference_counts,
            include_reference_texts_in_output=bool(args.include_reference_texts_in_output),
            save_nan_rows=bool(args.save_nan_rows),
        )

    combined_output_path = None
    if args.save_combined_pt:
        combined_output_path = save_combined_output(
            output_dir=output_dir,
            reference_setup=reference_setup,
            common_metadata=common_metadata,
            train_split=loaded_inputs.train,
            eval_known_payload=eval_known_payload,
            eval_unknown_payload=eval_unknown_payload,
            reference_payload=reference_payload,
            fci_backend=str(args.fci_backend),
            fit_method=str(args.fit_method),
            pyfci_random_seed=args.pyfci_random_seed,
        )

    valid_reference_sizes = [
        int(reference_size)
        for reference_size, is_valid in zip(
            reference_setup.reference_sizes_requested,
            reference_setup.valid_reference_size_mask.tolist(),
        )
        if is_valid
    ]

    print("\nFinal summary:")
    print(f"  input mode: {loaded_inputs.input_mode}")
    if loaded_inputs.input_mode in {"combined", "combined_seen_unseen"}:
        print(f"  combined file path: {loaded_inputs.combined_pt}")
        if loaded_inputs.input_mode == "combined_seen_unseen":
            print("  combined file format: seen/unseen")
    elif loaded_inputs.input_mode == "seen_unseen":
        print(f"  seen file path: {loaded_inputs.seen_pt}")
        print(f"  unseen file path: {loaded_inputs.unseen_pt}")
    else:
        print(f"  train file path: {loaded_inputs.train_pt}")
        print(f"  eval_known file path: {loaded_inputs.eval_known_pt}")
        print(f"  eval_unknown file path: {loaded_inputs.eval_unknown_pt}")
    print(f"  number of train/reference sentences: {loaded_inputs.train.num_examples}")
    print(f"  number of eval_known sentences: {loaded_inputs.eval_known.num_examples}")
    print(f"  number of eval_unknown sentences: {loaded_inputs.eval_unknown.num_examples}")
    print(f"  number of layers: {common_metadata['num_layers']}")
    print(f"  computed layers (1-based): {common_metadata['computed_layer_numbers']}")
    print(f"  hidden size: {common_metadata['hidden_size']}")
    print(f"  requested reference sizes: {reference_setup.reference_sizes_requested}")
    print(f"  requested k values: {reference_setup.k_values_requested}")
    print(f"  valid reference sizes: {valid_reference_sizes}")
    print(f"  FCI backend: {args.fci_backend}")
    if args.pyfci_random_seed is not None:
        print(f"  pyFCI random seed: {args.pyfci_random_seed}")
    if reused_reference_setup_path is not None:
        print(f"  reused reference setup file: {reused_reference_setup_path}")
    if reference_setup.invalid_reference_sizes:
        print(f"  invalid reference sizes: {reference_setup.invalid_reference_sizes}")
    if reference_setup.invalid_k_by_reference_size:
        print(f"  invalid k values by reference size: {reference_setup.invalid_k_by_reference_size}")
    print(f"  eval_known output tensor shape: {tuple(eval_known_pointwise_fci_id.shape)}")
    print(f"  eval_unknown output tensor shape: {tuple(eval_unknown_pointwise_fci_id.shape)}")
    if reference_pointwise_fci_id is not None and reference_counts is not None:
        print(f"  reference output tensor shape: {tuple(reference_pointwise_fci_id.shape)}")
    print(f"  eval_known structural NaN count: {eval_known_counts.structural}")
    print(f"  eval_known fit-failure NaN count: {eval_known_counts.fit_failures}")
    print(f"  eval_known numerical NaN count: {eval_known_counts.numerical}")
    print(f"  eval_unknown structural NaN count: {eval_unknown_counts.structural}")
    print(f"  eval_unknown fit-failure NaN count: {eval_unknown_counts.fit_failures}")
    print(f"  eval_unknown numerical NaN count: {eval_unknown_counts.numerical}")
    if reference_counts is not None:
        print(f"  reference structural NaN count: {reference_counts.structural}")
        print(f"  reference fit-failure NaN count: {reference_counts.fit_failures}")
        print(f"  reference numerical NaN count: {reference_counts.numerical}")
    print(f"  eval_known PT output: {eval_known_paths['pt']}")
    print(f"  eval_unknown PT output: {eval_unknown_paths['pt']}")
    print(f"  eval_known parquet output: {eval_known_paths['parquet']}")
    print(f"  eval_unknown parquet output: {eval_unknown_paths['parquet']}")
    if reference_paths is not None:
        print(f"  reference PT output: {reference_paths['pt']}")
        print(f"  reference parquet output: {reference_paths['parquet']}")
    if combined_output_path is not None:
        print(f"  combined PT output: {combined_output_path}")

    print("")
    print_dataframe_preview("Example eval_known rows:", eval_known_preview)
    print("")
    print_dataframe_preview("Example eval_unknown rows:", eval_unknown_preview)
    if reference_preview is not None:
        print("")
        print_dataframe_preview("Example reference rows:", reference_preview)
    print_example_commands()


if __name__ == "__main__":
    main()

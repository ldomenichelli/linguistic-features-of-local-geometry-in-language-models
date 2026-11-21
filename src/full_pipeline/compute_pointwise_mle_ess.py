#!/usr/bin/env python3
"""Compute pointwise MLE ID, with optional ESS, for local seen/unseen rep bundles."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

IMPORT_ERROR = None

try:
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    from scipy.special import gamma
    import torch
    from tqdm import tqdm
except ModuleNotFoundError as exc:
    IMPORT_ERROR = exc


DEFAULT_REFERENCE_SIZES = "500,1000, 2000,5000,7500,10000,12000,15000"
DEFAULT_K_VALUES = "5,10,15,20,25,30,35,50,70,100, 150,200,250,300,350,500,750,1000"
DEFAULT_REFERENCE_COUNT = 15_000
DEFAULT_EVAL_KNOWN_COUNT = 2000
DEFAULT_EVAL_UNKNOWN_COUNT = 2000
LONG_TABLE_QUERY_CHUNK = 128
PREVIEW_ROWS = 5
ESS_MAX_PAIR_SAMPLES = 5_000
ESS_QUERY_CHUNK_SIZE = 8
ESS_PAIR_BATCH_SIZE = 256

@dataclass
class SplitData:
    """Normalized split bundle loaded from a .pt file."""

    split_name: str
    input_path: Path
    reps: torch.Tensor
    texts: list[str]
    num_examples: int
    num_layers: int
    hidden_size: int
    labels: torch.Tensor | None
    label_name: str | None
    source_file: str | None
    source_kind: str | None
    line_indices: torch.Tensor | None
    num_chars: torch.Tensor | None
    num_words: torch.Tensor | None
    num_tokens: torch.Tensor | None
    model_name: str | None
    revision: str | None
    layer_names: list[str] | None
    include_embeddings: bool | None


@dataclass
class LoadedInputs:
    """Resolved input mode plus normalized seen/unseen split bundles."""

    input_mode: str
    seen: SplitData
    unseen: SplitData
    combined_pt: Path | None
    seen_pt: Path | None
    unseen_pt: Path | None


@dataclass
class ReferenceSetup:
    """Reference-pool split information shared across eval_known/eval_unknown."""

    reference_pool_indices: torch.Tensor
    eval_known_indices: torch.Tensor
    eval_unknown_indices: torch.Tensor
    ordered_reference_pool_indices: torch.Tensor
    reference_indices_by_size: dict[int, list[int]]
    reference_sizes_requested: list[int]
    k_values_requested: list[int]
    valid_reference_size_mask: torch.Tensor
    valid_k_mask: torch.Tensor
    invalid_reference_sizes: list[int]
    invalid_k_by_reference_size: dict[int, list[int]]


def parse_args() -> argparse.Namespace:
    """Parse and validate CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Use a seen representation bundle as the reference manifold, split it into "
            "reference/eval_known subsets, and compute pointwise MLE intrinsic dimensionality, "
            "with optional ESS, for eval_known and eval_unknown examples."
        )
    )
    parser.add_argument("--combined_pt", type=str, default=None)
    parser.add_argument("--seen_pt", type=str, default=None)
    parser.add_argument("--unseen_pt", type=str, default=None)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument(
        "--unseen_output_name",
        type=str,
        default="eval_unknown",
        help=(
            "Output split name for the --unseen_pt query set. The default preserves "
            "the historical eval_unknown filenames; use eval_known_1 for that split."
        ),
    )

    parser.add_argument("--reference_count", type=int, default=DEFAULT_REFERENCE_COUNT)
    parser.add_argument("--eval_known_count", type=int, default=DEFAULT_EVAL_KNOWN_COUNT)
    parser.add_argument("--eval_unknown_count", type=int, default=DEFAULT_EVAL_UNKNOWN_COUNT)
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
    parser.add_argument("--chunk_size", type=int, default=256)
    parser.add_argument("--eps", type=float, default=1e-12)
    parser.add_argument("--bias_corrected", action="store_true")
    parser.add_argument("--strict_reference_sizes", action="store_true")
    parser.add_argument("--strict_k_values", action="store_true")
    parser.add_argument("--save_nan_rows", action="store_true")
    parser.add_argument("--save_combined_pt", action="store_true")
    parser.add_argument("--include_reference_texts_in_output", action="store_true")
    parser.add_argument(
        "--include_ess",
        action="store_true",
        help=(
            "Also compute pointwise ESS using the scikit-dimension ESS default "
            "(ver='a', d=1) semantics."
        ),
    )

    args = parser.parse_args()

    if args.reference_count <= 0:
        parser.error("--reference_count must be a positive integer.")
    if args.eval_known_count <= 0:
        parser.error("--eval_known_count must be a positive integer.")
    if args.eval_unknown_count <= 0:
        parser.error("--eval_unknown_count must be a positive integer.")
    if args.chunk_size <= 0:
        parser.error("--chunk_size must be a positive integer.")
    if args.eps <= 0:
        parser.error("--eps must be positive.")
    if not args.unseen_output_name.strip():
        parser.error("--unseen_output_name cannot be empty.")
    if any(separator in args.unseen_output_name for separator in ("/", "\\")):
        parser.error("--unseen_output_name must be a filename stem, not a path.")

    return args


def safe_torch_load(path: Path):
    """Load a torch file across PyTorch versions."""
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def parse_int_list(values: str, name: str) -> list[int]:
    """Parse a comma-separated integer list while preserving the requested order."""
    parts = [part.strip() for part in values.split(",")]
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


def ensure_input_file_exists(path: Path, description: str) -> None:
    """Validate a required file path."""
    if not path.exists():
        raise FileNotFoundError(f"{description} does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"{description} is not a file: {path}")


def normalize_optional_tensor(
    value: Any,
    expected_length: int,
    name: str,
    *,
    dtype: torch.dtype | None = None,
) -> torch.Tensor | None:
    """Normalize optional vector metadata to a 1D CPU tensor."""
    if value is None:
        return None

    try:
        tensor = torch.as_tensor(value)
    except Exception as exc:
        raise ValueError(f"Could not convert {name} to a tensor.") from exc

    tensor = tensor.detach().cpu().reshape(-1)
    if tensor.numel() != expected_length:
        raise ValueError(
            f"{name} length does not match reps.shape[0]: {tensor.numel()} vs {expected_length}."
        )
    if dtype is not None:
        tensor = tensor.to(dtype=dtype)
    return tensor.contiguous()


def normalize_optional_list(
    value: Any,
    expected_length: int,
    name: str,
    *,
    item_transform=None,
) -> list[Any] | None:
    """Normalize optional vector metadata to a Python list."""
    if value is None:
        return None

    try:
        items = list(value)
    except TypeError as exc:
        raise ValueError(f"Could not interpret {name} as a sequence.") from exc

    if len(items) != expected_length:
        raise ValueError(
            f"{name} length does not match reps.shape[0]: {len(items)} vs {expected_length}."
        )

    if item_transform is None:
        return items
    return [item_transform(item) for item in items]


def normalize_optional_string(value: Any) -> str | None:
    """Normalize an optional scalar string-like metadata field."""
    if value is None:
        return None
    return str(value)


def normalize_layer_names(value: Any, num_layers: int) -> list[str] | None:
    """Normalize optional layer names and check that their length matches the tensor."""
    if value is None:
        return None
    layer_names = [str(item) for item in list(value)]
    if len(layer_names) != num_layers:
        raise ValueError(
            f"layer_names length does not match reps.shape[1]: {len(layer_names)} vs {num_layers}."
        )
    return layer_names


def load_split_bundle(
    bundle: Any,
    *,
    split_name: str,
    input_path: Path,
    expected_source_kind: str,
) -> SplitData:
    """Validate and normalize one seen/unseen split bundle."""
    if not isinstance(bundle, dict):
        raise ValueError(f"The {split_name} split must be stored as a dictionary.")
    if "reps" not in bundle or "texts" not in bundle:
        raise KeyError(f"The {split_name} split must contain at least 'reps' and 'texts'.")

    reps = torch.as_tensor(bundle["reps"]).detach().cpu().contiguous()
    if reps.ndim != 3:
        raise ValueError(
            f"{split_name} reps must have shape [N, L, D], got {tuple(reps.shape)}."
        )

    num_examples, num_layers, hidden_size = reps.shape
    texts = normalize_optional_list(bundle.get("texts"), num_examples, f"{split_name}.texts")
    if texts is None:
        raise KeyError(f"The {split_name} split must contain 'texts'.")
    texts = [str(text) for text in texts]

    source_kind = normalize_optional_string(bundle.get("source_kind"))
    if source_kind is not None and source_kind != expected_source_kind:
        raise ValueError(
            f"{split_name}.source_kind is {source_kind!r}, expected {expected_source_kind!r}."
        )

    include_embeddings = None
    if "include_embeddings" in bundle:
        include_embeddings = bool(bundle.get("include_embeddings"))

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

    return SplitData(
        split_name=split_name,
        input_path=input_path,
        reps=reps,
        texts=texts,
        num_examples=int(num_examples),
        num_layers=int(num_layers),
        hidden_size=int(hidden_size),
        labels=normalize_optional_tensor(bundle.get("labels"), num_examples, f"{split_name}.labels", dtype=torch.long),
        label_name=normalize_optional_string(bundle.get("label_name")),
        source_file=normalize_optional_string(bundle.get("source_file")),
        source_kind=source_kind,
        line_indices=normalize_optional_tensor(bundle.get("line_indices"), num_examples, f"{split_name}.line_indices", dtype=torch.long),
        num_chars=normalize_optional_tensor(bundle.get("num_chars"), num_examples, f"{split_name}.num_chars", dtype=torch.long),
        num_words=normalize_optional_tensor(bundle.get("num_words"), num_examples, f"{split_name}.num_words", dtype=torch.long),
        num_tokens=normalize_optional_tensor(bundle.get("num_tokens"), num_examples, f"{split_name}.num_tokens", dtype=torch.long),
        model_name=normalize_optional_string(bundle.get("model_name")),
        revision=normalize_optional_string(bundle.get("revision")),
        layer_names=normalize_layer_names(bundle.get("layer_names"), int(num_layers)),
        include_embeddings=include_embeddings,
    )


def resolve_input_mode(args: argparse.Namespace) -> LoadedInputs:
    """Resolve whether we are using a combined .pt or separate seen/unseen .pt files."""
    combined_requested = args.combined_pt is not None
    separate_requested = args.seen_pt is not None or args.unseen_pt is not None

    if combined_requested and separate_requested:
        raise ValueError("Provide either --combined_pt or both --seen_pt/--unseen_pt, not both modes.")

    if combined_requested:
        combined_path = Path(args.combined_pt)
        ensure_input_file_exists(combined_path, "Combined input file")
        bundle = safe_torch_load(combined_path)
        if not isinstance(bundle, dict):
            raise ValueError("The combined .pt file must contain a dictionary.")
        if "seen" not in bundle or "unseen" not in bundle:
            raise KeyError("The combined .pt file must contain 'seen' and 'unseen' keys.")

        seen = load_split_bundle(
            bundle["seen"],
            split_name="seen",
            input_path=combined_path,
            expected_source_kind="seen",
        )
        unseen = load_split_bundle(
            bundle["unseen"],
            split_name="unseen",
            input_path=combined_path,
            expected_source_kind="unseen",
        )
        return LoadedInputs(
            input_mode="combined",
            seen=seen,
            unseen=unseen,
            combined_pt=combined_path,
            seen_pt=None,
            unseen_pt=None,
        )

    if args.seen_pt is None or args.unseen_pt is None:
        raise ValueError("Either provide --combined_pt, or provide both --seen_pt and --unseen_pt.")

    seen_path = Path(args.seen_pt)
    unseen_path = Path(args.unseen_pt)
    ensure_input_file_exists(seen_path, "Seen input file")
    ensure_input_file_exists(unseen_path, "Unseen input file")

    seen_bundle = safe_torch_load(seen_path)
    unseen_bundle = safe_torch_load(unseen_path)

    seen = load_split_bundle(
        seen_bundle,
        split_name="seen",
        input_path=seen_path,
        expected_source_kind="seen",
    )
    unseen = load_split_bundle(
        unseen_bundle,
        split_name="unseen",
        input_path=unseen_path,
        expected_source_kind="unseen",
    )
    return LoadedInputs(
        input_mode="separate",
        seen=seen,
        unseen=unseen,
        combined_pt=None,
        seen_pt=seen_path,
        unseen_pt=unseen_path,
    )


def choose_compatible_metadata(name: str, seen_value: Any, unseen_value: Any) -> Any:
    """Validate that optional metadata agrees across seen and unseen when both exist."""
    if seen_value is None:
        return unseen_value
    if unseen_value is None:
        return seen_value
    if seen_value != unseen_value:
        raise ValueError(
            f"Mismatch between seen and unseen {name}: {seen_value!r} vs {unseen_value!r}."
        )
    return seen_value


def infer_layer_names(
    num_layers: int,
    include_embeddings: bool,
    provided_layer_names: Sequence[str] | None,
) -> list[str]:
    """Infer readable layer names when they are not stored in the input bundle."""
    if provided_layer_names is not None:
        layer_names = [str(name) for name in list(provided_layer_names)]
        if len(layer_names) != num_layers:
            raise ValueError(
                f"layer_names length does not match reps.shape[1]: {len(layer_names)} vs {num_layers}."
            )
        return layer_names

    if include_embeddings:
        return ["embedding"] + [f"layer_{index}" for index in range(1, num_layers)]
    return [f"layer_{index}" for index in range(1, num_layers + 1)]


def validate_compatible_rep_shapes(seen: SplitData, unseen: SplitData) -> dict[str, Any]:
    """Validate that seen and unseen representations can be compared directly."""
    if seen.num_layers != unseen.num_layers:
        raise ValueError(
            f"Seen/unseen num_layers mismatch: {seen.num_layers} vs {unseen.num_layers}."
        )
    if seen.hidden_size != unseen.hidden_size:
        raise ValueError(
            f"Seen/unseen hidden_size mismatch: {seen.hidden_size} vs {unseen.hidden_size}."
        )

    model_name = choose_compatible_metadata("model_name", seen.model_name, unseen.model_name)
    revision = choose_compatible_metadata("revision", seen.revision, unseen.revision)
    include_embeddings = choose_compatible_metadata(
        "include_embeddings",
        seen.include_embeddings,
        unseen.include_embeddings,
    )
    if include_embeddings is None:
        include_embeddings = False

    if seen.layer_names is not None and unseen.layer_names is not None and seen.layer_names != unseen.layer_names:
        raise ValueError("Seen and unseen layer_names metadata do not match.")
    provided_layer_names = seen.layer_names if seen.layer_names is not None else unseen.layer_names
    layer_names = infer_layer_names(
        seen.num_layers,
        bool(include_embeddings),
        provided_layer_names,
    )

    return {
        "num_layers": seen.num_layers,
        "hidden_size": seen.hidden_size,
        "model_name": model_name,
        "revision": revision,
        "include_embeddings": bool(include_embeddings),
        "layer_names": layer_names,
    }


def split_seen_into_reference_and_eval_known(
    num_seen: int,
    *,
    reference_count: int,
    eval_known_count: int,
    reshuffle_seen_before_split: bool,
    seed: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Split seen indices into a reference pool and an eval_known subset."""
    total_needed = reference_count + eval_known_count
    if num_seen < total_needed:
        raise ValueError(
            f"Seen file contains only {num_seen} examples, but {total_needed} are required "
            f"for reference_count={reference_count} and eval_known_count={eval_known_count}."
        )

    if reshuffle_seen_before_split:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        ordered_seen_indices = torch.randperm(num_seen, generator=generator)
    else:
        ordered_seen_indices = torch.arange(num_seen, dtype=torch.long)

    reference_pool_indices = ordered_seen_indices[:reference_count].cpu().long().contiguous()
    eval_known_indices = ordered_seen_indices[reference_count : reference_count + eval_known_count].cpu().long().contiguous()
    return reference_pool_indices, eval_known_indices


def build_validity_masks(
    num_reference_pool: int,
    reference_sizes: Sequence[int],
    k_values: Sequence[int],
    strict_reference_sizes: bool,
    strict_k_values: bool,
) -> tuple[torch.Tensor, torch.Tensor, list[int], dict[int, list[int]]]:
    """Build structural validity masks for reference sizes and k values."""
    valid_reference_size_mask = torch.tensor(
        [2 <= int(size) <= num_reference_pool for size in reference_sizes],
        dtype=torch.bool,
    ).contiguous()

    invalid_reference_sizes = [
        int(size)
        for size, is_valid in zip(reference_sizes, valid_reference_size_mask.tolist())
        if not is_valid
    ]
    if invalid_reference_sizes and strict_reference_sizes:
        raise ValueError(
            "Requested reference sizes are invalid for the available reference pool. "
            f"num_reference_pool={num_reference_pool}, invalid_reference_sizes={invalid_reference_sizes}."
        )

    valid_k_mask = torch.zeros((len(reference_sizes), len(k_values)), dtype=torch.bool)
    invalid_k_by_reference_size: dict[int, list[int]] = {}
    for ref_idx, reference_size in enumerate(reference_sizes):
        if not bool(valid_reference_size_mask[ref_idx].item()):
            continue
        invalid_ks_for_size: list[int] = []
        for k_idx, k_value in enumerate(k_values):
            is_valid = 2 <= int(k_value) <= int(reference_size)
            valid_k_mask[ref_idx, k_idx] = is_valid
            if not is_valid:
                invalid_ks_for_size.append(int(k_value))
        if invalid_ks_for_size:
            invalid_k_by_reference_size[int(reference_size)] = invalid_ks_for_size

    if invalid_k_by_reference_size and strict_k_values:
        raise ValueError(
            "Some requested k values are invalid for at least one reference size: "
            f"{invalid_k_by_reference_size}."
        )

    return (
        valid_reference_size_mask.contiguous(),
        valid_k_mask.contiguous(),
        invalid_reference_sizes,
        invalid_k_by_reference_size,
    )


def build_nested_reference_sets(
    reference_pool_indices: torch.Tensor,
    reference_sizes: Sequence[int],
    valid_reference_size_mask: torch.Tensor,
    seed: int,
) -> tuple[torch.Tensor, dict[int, list[int]]]:
    """Create one nested reference-set family from a single pool permutation."""
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    permutation = torch.randperm(reference_pool_indices.numel(), generator=generator)
    ordered_reference_pool_indices = reference_pool_indices.index_select(0, permutation.cpu()).contiguous()

    reference_indices_by_size: dict[int, list[int]] = {}
    for reference_size, is_valid in zip(reference_sizes, valid_reference_size_mask.tolist()):
        if not is_valid:
            continue
        selected = ordered_reference_pool_indices[: int(reference_size)].cpu().tolist()
        reference_indices_by_size[int(reference_size)] = [int(index) for index in selected]

    return ordered_reference_pool_indices, reference_indices_by_size


def subset_optional_tensor(value: torch.Tensor | None, indices: torch.Tensor) -> torch.Tensor | None:
    """Select a subset from an optional tensor metadata field."""
    if value is None:
        return None
    return value.index_select(0, indices.cpu()).contiguous()


def subset_optional_list(value: Sequence[Any] | None, indices: torch.Tensor) -> list[Any] | None:
    """Select a subset from an optional list metadata field."""
    if value is None:
        return None
    index_list = indices.cpu().tolist()
    return [value[index] for index in index_list]


def update_signature_with_int_values(
    digest: Any,
    tag: str,
    values: Sequence[int] | torch.Tensor | np.ndarray,
) -> None:
    """Update a hash digest with a stable stream of integer values."""
    digest.update(tag.encode("utf-8"))
    digest.update(b"\0")
    tensor = torch.as_tensor(values, dtype=torch.long).detach().cpu().reshape(-1)
    digest.update(np.asarray(tensor.tolist(), dtype=np.int64).tobytes())
    digest.update(b"\0")


def update_signature_with_bool_values(
    digest: Any,
    tag: str,
    values: Sequence[bool] | torch.Tensor | np.ndarray,
) -> None:
    """Update a hash digest with a stable stream of boolean values."""
    digest.update(tag.encode("utf-8"))
    digest.update(b"\0")
    tensor = torch.as_tensor(values, dtype=torch.bool).detach().cpu().reshape(-1)
    digest.update(np.asarray(tensor.tolist(), dtype=np.uint8).tobytes())
    digest.update(b"\0")


def update_signature_with_text(digest: Any, tag: str, value: str | None) -> None:
    """Update a hash digest with one optional text field."""
    digest.update(tag.encode("utf-8"))
    digest.update(b"\0")
    digest.update((value or "").encode("utf-8"))
    digest.update(b"\0")


def update_signature_with_text_values(digest: Any, tag: str, values: Sequence[str]) -> None:
    """Update a hash digest with a stable sequence of text values."""
    digest.update(tag.encode("utf-8"))
    digest.update(b"\0")
    for value in values:
        digest.update(str(value).encode("utf-8"))
        digest.update(b"\0")


def build_reference_setup_signature(reference_setup: ReferenceSetup) -> str:
    """Hash the exact reference-pool and nested-subset construction."""
    digest = hashlib.sha1()
    update_signature_with_int_values(
        digest,
        "reference_pool_indices",
        reference_setup.reference_pool_indices,
    )
    update_signature_with_int_values(
        digest,
        "ordered_reference_pool_indices",
        reference_setup.ordered_reference_pool_indices,
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
    query_source_kind: str | None,
    query_source_file: str | None,
) -> str:
    """Hash the exact query subset used for one split."""
    digest = hashlib.sha1()
    update_signature_with_int_values(digest, "query_indices", query_indices)
    update_signature_with_text(digest, "sample_kind", sample_kind)
    update_signature_with_text(digest, "query_source_kind", query_source_kind)
    update_signature_with_text(digest, "query_source_file", query_source_file)
    return digest.hexdigest()


def build_split_setup_signature(
    *,
    reference_setup_signature: str,
    query_selection_signature: str,
    common_metadata: dict[str, Any],
) -> str:
    """Hash the metric-invariant setup shared across MLE and ESS."""
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


def gather_query_metadata(split: SplitData, query_indices: torch.Tensor) -> dict[str, Any]:
    """Gather query metadata for one eval split."""
    return {
        "query_indices": query_indices.cpu().long().contiguous(),
        "texts": subset_optional_list(split.texts, query_indices),
        "labels": subset_optional_tensor(split.labels, query_indices),
        "label_name": split.label_name,
        "source_file": split.source_file,
        "source_kind": split.source_kind,
        "line_indices": subset_optional_tensor(split.line_indices, query_indices),
        "num_chars": subset_optional_tensor(split.num_chars, query_indices),
        "num_words": subset_optional_tensor(split.num_words, query_indices),
        "num_tokens": subset_optional_tensor(split.num_tokens, query_indices),
    }


def build_ess_pair_indices_by_k(
    k_values: Sequence[int],
    *,
    max_pair_samples: int,
    seed: int,
) -> dict[int, torch.Tensor]:
    """Build deterministic pair samples for ESS at each requested k."""
    pair_indices_by_k: dict[int, torch.Tensor] = {}
    unique_k_values = sorted({int(value) for value in k_values if int(value) >= 2})
    for offset, k_value in enumerate(unique_k_values):
        pair_indices = torch.triu_indices(k_value, k_value, offset=1).t().contiguous()
        if int(pair_indices.shape[0]) > max_pair_samples:
            generator = np.random.default_rng(seed + 10_007 * (offset + 1) + k_value)
            sampled_positions = np.sort(
                generator.choice(int(pair_indices.shape[0]), size=max_pair_samples, replace=False)
            )
            pair_indices = pair_indices.index_select(
                0,
                torch.as_tensor(sampled_positions, dtype=torch.long),
            ).contiguous()
        pair_indices_by_k[k_value] = pair_indices
    return pair_indices_by_k


@lru_cache(maxsize=None)
def ess_reference_curve(maxdim: int) -> np.ndarray:
    """Mirror the scikit-dimension ESS(ver='a', d=1) reference curve."""
    ess_d = 1
    if maxdim <= ess_d + 2:
        raise ValueError(f"maxdim must be larger than d + 2. Got {maxdim}.")

    j1 = np.array([1 + idx for idx in range(0, maxdim + 2, 2) if 1 + idx <= maxdim], dtype=np.int64)
    j2 = np.array([2 + idx for idx in range(0, maxdim + 2, 2) if 2 + idx <= maxdim], dtype=np.int64)
    factor1_j1 = (
        gamma(1 / 2)
        / gamma(2 / 2)
        * np.concatenate((np.array([1.0]), np.cumprod(j1 / (j1 + 1), dtype=np.float64)[:-1]))
    )
    factor1_j2 = (
        gamma(2 / 2)
        / gamma(3 / 2)
        * np.concatenate((np.array([1.0]), np.cumprod(j2 / (j2 + 1), dtype=np.float64)[:-1]))
    )
    factor1 = np.repeat(np.nan, maxdim).astype(np.float64)
    factor1[j1 - 1] = factor1_j1
    factor1[j2 - 1] = factor1_j2

    k1 = np.array(
        [ess_d + 1 + idx for idx in range(0, maxdim + 2, 2) if ess_d + 1 + idx <= maxdim],
        dtype=np.int64,
    )
    k2 = np.array(
        [ess_d + 2 + idx for idx in range(0, maxdim + 2, 2) if ess_d + 2 + idx <= maxdim],
        dtype=np.int64,
    )
    factor2_k1 = (
        gamma((ess_d + 1) / 2)
        / gamma(1 / 2)
        * np.concatenate((np.array([1.0]), np.cumprod(k1 / (k1 - ess_d), dtype=np.float64)[:-1]))
    )
    factor2_k2 = (
        gamma((ess_d + 2) / 2)
        / gamma(2 / 2)
        * np.concatenate((np.array([1.0]), np.cumprod(k2 / (k2 - ess_d), dtype=np.float64)[:-1]))
    )
    factor2 = np.zeros(maxdim, dtype=np.float64)
    factor2[k1 - 1] = factor2_k1
    factor2[k2 - 1] = factor2_k2
    return factor1**ess_d * factor2


def ess_values_to_dimensions(ess_values: torch.Tensor) -> torch.Tensor:
    """Map ESS values to ID estimates using the default scikit-dimension curve."""
    values = ess_values.detach().cpu().numpy().astype(np.float64, copy=False).reshape(-1)
    output = np.full(values.shape, np.nan, dtype=np.float32)
    finite_mask = np.isfinite(values)
    if not finite_mask.any():
        return torch.from_numpy(output)

    finite_values = values[finite_mask]
    maxdim = 20
    reference_values = ess_reference_curve(maxdim)
    while float(np.max(finite_values)) > reference_values[-1]:
        maxdim = 2 * (maxdim - 1)
        reference_values = ess_reference_curve(maxdim)

    insert_positions = np.searchsorted(reference_values, finite_values, side="right")
    insert_positions = np.clip(insert_positions, 1, len(reference_values) - 1)
    lower = reference_values[insert_positions - 1]
    upper = reference_values[insert_positions]
    fractions = np.divide(
        finite_values - lower,
        upper - lower,
        out=np.zeros_like(finite_values),
        where=np.abs(upper - lower) > 0,
    )
    dimensions = insert_positions.astype(np.float64) + fractions
    dimensions[finite_values <= reference_values[0]] = 1.0
    output[finite_mask] = dimensions.astype(np.float32)
    return torch.from_numpy(output)


def compute_pointwise_ess_from_sorted_indices(
    *,
    reference_layer: torch.Tensor,
    sorted_indices: torch.Tensor,
    k_values: Sequence[int],
    valid_k_mask_row: torch.Tensor,
    pair_indices_by_k: dict[int, torch.Tensor],
    eps: float,
    query_chunk_size: int,
    pair_batch_size: int,
) -> tuple[torch.Tensor, int]:
    """Compute pointwise ESS from nearest-neighbor patches for one query chunk."""
    num_queries = int(sorted_indices.shape[0])
    pointwise_ess = torch.full(
        (num_queries, len(k_values)),
        float("nan"),
        dtype=torch.float32,
        device=reference_layer.device,
    )
    numeric_nan_count = 0

    for k_idx, k_value in enumerate(k_values):
        if not bool(valid_k_mask_row[k_idx].item()):
            continue

        pair_indices = pair_indices_by_k.get(int(k_value))
        if pair_indices is None or int(pair_indices.shape[0]) == 0:
            continue
        pair_indices = pair_indices.to(device=reference_layer.device)

        for query_start in range(0, num_queries, query_chunk_size):
            query_end = min(query_start + query_chunk_size, num_queries)
            neighborhood_indices = sorted_indices[query_start:query_end, :k_value]
            if int(neighborhood_indices.shape[1]) < 2:
                continue

            neighborhoods = reference_layer.index_select(
                0,
                neighborhood_indices.reshape(-1),
            ).reshape(query_end - query_start, k_value, reference_layer.shape[1])
            centered = neighborhoods - neighborhoods.mean(dim=1, keepdim=True)

            volume_sums = torch.zeros(query_end - query_start, dtype=torch.float64, device=reference_layer.device)
            weight_sums = torch.zeros(query_end - query_start, dtype=torch.float64, device=reference_layer.device)

            for pair_start in range(0, int(pair_indices.shape[0]), pair_batch_size):
                pair_end = min(pair_start + pair_batch_size, int(pair_indices.shape[0]))
                pair_chunk = pair_indices[pair_start:pair_end]
                left = centered.index_select(1, pair_chunk[:, 0])
                right = centered.index_select(1, pair_chunk[:, 1])

                left_norm = torch.linalg.vector_norm(left, dim=2).to(torch.float64)
                right_norm = torch.linalg.vector_norm(right, dim=2).to(torch.float64)
                weight = left_norm * right_norm
                dot = (left * right).sum(dim=2).to(torch.float64)
                volume = torch.sqrt(torch.clamp(weight.square() - dot.square(), min=0.0))
                volume_sums += volume.sum(dim=1)
                weight_sums += weight.sum(dim=1)

            ess_values = torch.full(
                (query_end - query_start,),
                float("nan"),
                dtype=torch.float32,
                device=reference_layer.device,
            )
            valid = torch.isfinite(volume_sums) & torch.isfinite(weight_sums) & (weight_sums > eps)
            ess_values[valid] = (volume_sums[valid] / weight_sums[valid]).to(torch.float32)

            ess_dimensions = torch.full_like(ess_values, float("nan"))
            finite_ess = torch.isfinite(ess_values)
            if bool(finite_ess.any().item()):
                ess_dimensions[finite_ess] = ess_values_to_dimensions(ess_values[finite_ess]).to(
                    device=reference_layer.device,
                    dtype=torch.float32,
                )

            ess_dimensions[~torch.isfinite(ess_dimensions)] = float("nan")
            pointwise_ess[query_start:query_end, k_idx] = ess_dimensions
            numeric_nan_count += int(torch.isnan(ess_dimensions).sum().item())

    return pointwise_ess, numeric_nan_count


def compute_pointwise_mle_from_sorted_dists(
    sorted_dists: torch.Tensor,
    k_values: Sequence[int],
    valid_k_mask_row: torch.Tensor,
    eps: float,
    bias_corrected: bool,
) -> tuple[torch.Tensor, int]:
    """Compute pointwise MLE ID from sorted Euclidean distances for one chunk."""
    num_queries = int(sorted_dists.shape[0])
    pointwise_id = torch.full(
        (num_queries, len(k_values)),
        float("nan"),
        dtype=torch.float32,
        device=sorted_dists.device,
    )
    numeric_nan_count = 0

    for k_idx, k_value in enumerate(k_values):
        if not bool(valid_k_mask_row[k_idx].item()):
            continue

        r_k = sorted_dists[:, k_value - 1].clamp_min(eps)
        r_j = sorted_dists[:, : k_value - 1].clamp_min(eps)
        log_ratios = torch.log(r_k.unsqueeze(1) / r_j)
        denom = log_ratios.sum(dim=1)

        estimates = torch.full((num_queries,), float("nan"), dtype=torch.float32, device=sorted_dists.device)
        valid = torch.isfinite(denom) & (denom > 0)
        if bias_corrected:
            estimates[valid] = (float(k_value - 2) / denom[valid]).to(torch.float32)
        else:
            mean_log = denom / float(k_value - 1)
            valid = valid & torch.isfinite(mean_log) & (mean_log > 0)
            estimates[valid] = (1.0 / mean_log[valid]).to(torch.float32)

        estimates[~torch.isfinite(estimates)] = float("nan")
        pointwise_id[:, k_idx] = estimates
        numeric_nan_count += int(torch.isnan(estimates).sum().item())

    return pointwise_id, numeric_nan_count


def compute_metrics_for_reference_size(
    reference_layer: torch.Tensor,
    query_source_reps: torch.Tensor,
    query_indices: torch.Tensor,
    *,
    layer_idx: int,
    k_values: Sequence[int],
    valid_k_mask_row: torch.Tensor,
    device: torch.device,
    chunk_size: int,
    eps: float,
    bias_corrected: bool,
    include_ess: bool,
    pair_indices_by_k: dict[int, torch.Tensor],
) -> tuple[dict[str, torch.Tensor], dict[str, int]]:
    """Compute [N_query, n_k] pointwise metrics for one layer and one reference size."""
    num_queries = int(query_indices.numel())
    pointwise_metrics: dict[str, torch.Tensor] = {
        "mle": torch.full((num_queries, len(k_values)), float("nan"), dtype=torch.float32)
    }
    numeric_nan_count_by_metric = {"mle": 0}
    if include_ess:
        pointwise_metrics["ess"] = torch.full((num_queries, len(k_values)), float("nan"), dtype=torch.float32)
        numeric_nan_count_by_metric["ess"] = 0

    if not bool(valid_k_mask_row.any().item()):
        return (
            {metric: value.contiguous() for metric, value in pointwise_metrics.items()},
            numeric_nan_count_by_metric,
        )

    with torch.inference_mode():
        for start in range(0, num_queries, chunk_size):
            end = min(start + chunk_size, num_queries)
            chunk_indices = query_indices[start:end]
            query_chunk = query_source_reps.index_select(0, chunk_indices)[:, layer_idx, :].to(
                device=device,
                dtype=torch.float32,
            )
            distances = torch.cdist(query_chunk, reference_layer, p=2.0)
            sorted_result = torch.sort(distances, dim=1)
            sorted_dists = sorted_result.values
            sorted_indices = sorted_result.indices

            chunk_mle, chunk_mle_nan_count = compute_pointwise_mle_from_sorted_dists(
                sorted_dists,
                k_values,
                valid_k_mask_row,
                eps,
                bias_corrected,
            )
            pointwise_metrics["mle"][start:end] = chunk_mle.to("cpu", dtype=torch.float32).contiguous()
            numeric_nan_count_by_metric["mle"] += chunk_mle_nan_count

            if include_ess:
                chunk_ess, chunk_ess_nan_count = compute_pointwise_ess_from_sorted_indices(
                    reference_layer=reference_layer,
                    sorted_indices=sorted_indices,
                    k_values=k_values,
                    valid_k_mask_row=valid_k_mask_row,
                    pair_indices_by_k=pair_indices_by_k,
                    eps=eps,
                    query_chunk_size=ESS_QUERY_CHUNK_SIZE,
                    pair_batch_size=ESS_PAIR_BATCH_SIZE,
                )
                pointwise_metrics["ess"][start:end] = chunk_ess.to("cpu", dtype=torch.float32).contiguous()
                numeric_nan_count_by_metric["ess"] += chunk_ess_nan_count

    return (
        {metric: value.contiguous() for metric, value in pointwise_metrics.items()},
        numeric_nan_count_by_metric,
    )


def compute_ids_for_query_set(
    *,
    reference_source_reps: torch.Tensor,
    query_source_reps: torch.Tensor,
    query_indices: torch.Tensor,
    reference_indices_by_size: dict[int, list[int]],
    reference_sizes_requested: Sequence[int],
    k_values_requested: Sequence[int],
    valid_reference_size_mask: torch.Tensor,
    valid_k_mask: torch.Tensor,
    num_layers: int,
    device: torch.device,
    chunk_size: int,
    eps: float,
    bias_corrected: bool,
    sample_kind: str,
    include_ess: bool,
    seed: int,
    layer_indices: Sequence[int],
) -> tuple[dict[str, torch.Tensor], dict[str, int]]:
    """Compute pointwise metrics for one query split across all layers/reference sizes."""
    num_queries = int(query_indices.numel())
    pointwise_metrics: dict[str, torch.Tensor] = {
        "mle": torch.full(
            (num_queries, num_layers, len(reference_sizes_requested), len(k_values_requested)),
            float("nan"),
            dtype=torch.float32,
        )
    }
    numeric_nan_count_by_metric = {"mle": 0}
    if include_ess:
        pointwise_metrics["ess"] = torch.full(
            (num_queries, num_layers, len(reference_sizes_requested), len(k_values_requested)),
            float("nan"),
            dtype=torch.float32,
        )
        numeric_nan_count_by_metric["ess"] = 0

    pair_indices_by_k = (
        build_ess_pair_indices_by_k(
            k_values_requested,
            max_pair_samples=ESS_MAX_PAIR_SAMPLES,
            seed=seed,
        )
        if include_ess
        else {}
    )

    with torch.inference_mode():
        for ref_idx, reference_size in enumerate(
            tqdm(reference_sizes_requested, desc=f"Reference sizes ({sample_kind})", unit="size")
        ):
            if not bool(valid_reference_size_mask[ref_idx].item()):
                continue

            reference_index_tensor = torch.tensor(
                reference_indices_by_size[int(reference_size)],
                dtype=torch.long,
            )
            valid_k_mask_row = valid_k_mask[ref_idx]

            for layer_idx in layer_indices:
                reference_layer = reference_source_reps.index_select(0, reference_index_tensor)[:, layer_idx, :].to(
                    device=device,
                    dtype=torch.float32,
                )
                layer_metrics, layer_nan_count_by_metric = compute_metrics_for_reference_size(
                    reference_layer,
                    query_source_reps,
                    query_indices,
                    layer_idx=layer_idx,
                    k_values=k_values_requested,
                    valid_k_mask_row=valid_k_mask_row,
                    device=device,
                    chunk_size=chunk_size,
                    eps=eps,
                    bias_corrected=bias_corrected,
                    include_ess=include_ess,
                    pair_indices_by_k=pair_indices_by_k,
                )
                for metric_name, layer_pointwise_values in layer_metrics.items():
                    pointwise_metrics[metric_name][:, layer_idx, ref_idx, :] = layer_pointwise_values
                for metric_name, metric_nan_count in layer_nan_count_by_metric.items():
                    numeric_nan_count_by_metric[metric_name] += metric_nan_count

    return (
        {metric: value.contiguous() for metric, value in pointwise_metrics.items()},
        numeric_nan_count_by_metric,
    )


def compute_structural_nan_count(
    *,
    num_queries: int,
    num_layers: int,
    valid_k_mask: torch.Tensor,
) -> int:
    """Count NaNs introduced by structurally invalid reference-size/k combinations."""
    invalid_entries = int((~valid_k_mask).sum().item())
    return int(num_queries * num_layers * invalid_entries)


def build_long_dataframe(
    *,
    pointwise_id_chunk: torch.Tensor,
    pointwise_ess_chunk: torch.Tensor | None,
    query_start: int,
    chunk_metadata: dict[str, Any],
    sample_kind: str,
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
    """Build one chunk of the long-format table."""
    num_queries = int(pointwise_id_chunk.shape[0])
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
    valid_reference_size_array = np.tile(
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
        "query_source_index": np.repeat(
            chunk_metadata["query_indices"].cpu().numpy().astype(np.int64),
            rows_per_query,
        ),
        "text": np.repeat(np.asarray(chunk_metadata["texts"], dtype=object), rows_per_query),
        "sample_kind": np.full(total_rows, sample_kind, dtype=object),
        "layer_idx": layer_idx_array,
        "layer_name": layer_name_array,
        "reference_size": reference_size_array,
        "k": k_array,
        "pointwise_id": pointwise_id_chunk.numpy().reshape(-1),
        "is_valid_reference_size": valid_reference_size_array,
        "is_valid_k_for_reference_size": valid_k_array,
        "reference_setup_signature": np.full(total_rows, reference_setup_signature, dtype=object),
        "query_selection_signature": np.full(total_rows, query_selection_signature, dtype=object),
        "split_setup_signature": np.full(total_rows, split_setup_signature, dtype=object),
    }
    if pointwise_ess_chunk is not None:
        data["pointwise_ess"] = pointwise_ess_chunk.numpy().reshape(-1)

    labels = chunk_metadata.get("labels")
    if labels is not None:
        data["label"] = np.repeat(labels.cpu().numpy(), rows_per_query)

    label_name = chunk_metadata.get("label_name")
    if label_name is not None:
        data["label_name"] = np.full(total_rows, label_name, dtype=object)

    source_file = chunk_metadata.get("source_file")
    if source_file is not None:
        data["source_file"] = np.full(total_rows, source_file, dtype=object)

    source_kind = chunk_metadata.get("source_kind")
    if source_kind is not None:
        data["source_kind"] = np.full(total_rows, source_kind, dtype=object)

    line_indices = chunk_metadata.get("line_indices")
    if line_indices is not None:
        data["line_index"] = np.repeat(line_indices.cpu().numpy(), rows_per_query)

    num_chars = chunk_metadata.get("num_chars")
    if num_chars is not None:
        data["num_chars"] = np.repeat(num_chars.cpu().numpy(), rows_per_query)

    num_words = chunk_metadata.get("num_words")
    if num_words is not None:
        data["num_words"] = np.repeat(num_words.cpu().numpy(), rows_per_query)

    num_tokens = chunk_metadata.get("num_tokens")
    if num_tokens is not None:
        data["num_tokens"] = np.repeat(num_tokens.cpu().numpy(), rows_per_query)

    if model_name is not None:
        data["model_name"] = np.full(total_rows, model_name, dtype=object)
    if revision is not None:
        data["revision"] = np.full(total_rows, revision, dtype=object)

    dataframe = pd.DataFrame(data)
    if layer_indices is not None:
        selected_layers = {int(layer_idx) for layer_idx in layer_indices}
        dataframe = dataframe.loc[dataframe["layer_idx"].isin(selected_layers)].reset_index(drop=True)
    if not save_nan_rows:
        dataframe = dataframe[dataframe["is_valid_k_for_reference_size"]].reset_index(drop=True)
    return dataframe


def write_long_outputs(
    *,
    pointwise_id: torch.Tensor,
    pointwise_ess: torch.Tensor | None,
    output_parquet_path: Path,
    output_csv_path: Path,
    query_metadata: dict[str, Any],
    sample_kind: str,
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
    """Stream the long-format parquet/csv outputs to disk in query-sized chunks."""
    preview_frames: list[pd.DataFrame] = []
    parquet_writer = None
    csv_header = True

    try:
        for start in tqdm(
            range(0, int(pointwise_id.shape[0]), LONG_TABLE_QUERY_CHUNK),
            desc=f"Long table ({sample_kind})",
            unit="chunk",
        ):
            end = min(start + LONG_TABLE_QUERY_CHUNK, int(pointwise_id.shape[0]))
            chunk_metadata = {
                "query_indices": query_metadata["query_indices"][start:end],
                "texts": query_metadata["texts"][start:end],
                "labels": query_metadata["labels"][start:end] if query_metadata["labels"] is not None else None,
                "label_name": query_metadata["label_name"],
                "source_file": query_metadata["source_file"],
                "source_kind": query_metadata["source_kind"],
                "line_indices": query_metadata["line_indices"][start:end] if query_metadata["line_indices"] is not None else None,
                "num_chars": query_metadata["num_chars"][start:end] if query_metadata["num_chars"] is not None else None,
                "num_words": query_metadata["num_words"][start:end] if query_metadata["num_words"] is not None else None,
                "num_tokens": query_metadata["num_tokens"][start:end] if query_metadata["num_tokens"] is not None else None,
            }
            dataframe = build_long_dataframe(
                pointwise_id_chunk=pointwise_id[start:end],
                pointwise_ess_chunk=pointwise_ess[start:end] if pointwise_ess is not None else None,
                query_start=start,
                chunk_metadata=chunk_metadata,
                sample_kind=sample_kind,
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

            if len(preview_frames) < PREVIEW_ROWS:
                preview_frames.append(dataframe.head(PREVIEW_ROWS - len(preview_frames)))

            table = pa.Table.from_pandas(dataframe, preserve_index=False)
            if parquet_writer is None:
                parquet_writer = pq.ParquetWriter(output_parquet_path, table.schema)
            parquet_writer.write_table(table)
            dataframe.to_csv(output_csv_path, mode="w" if csv_header else "a", header=csv_header, index=False)
            csv_header = False
    finally:
        if parquet_writer is not None:
            parquet_writer.close()

    if preview_frames:
        return pd.concat(preview_frames, ignore_index=True).head(PREVIEW_ROWS)

    empty_df = pd.DataFrame(
        columns=[
            "query_index",
            "query_source_index",
            "text",
            "sample_kind",
            "layer_idx",
            "layer_name",
            "reference_size",
            "k",
            "pointwise_id",
            "pointwise_ess",
            "is_valid_reference_size",
            "is_valid_k_for_reference_size",
            "reference_setup_signature",
            "query_selection_signature",
            "split_setup_signature",
        ]
    )
    empty_df.to_parquet(output_parquet_path, index=False)
    empty_df.to_csv(output_csv_path, index=False)
    return empty_df


def save_split_outputs(
    *,
    output_dir: Path,
    split_name: str,
    sample_kind: str,
    pointwise_metrics: dict[str, torch.Tensor],
    query_metadata: dict[str, Any],
    reference_setup: ReferenceSetup,
    common_metadata: dict[str, Any],
    seen_split: SplitData,
    query_split: SplitData,
    bias_corrected: bool,
    eps: float,
    nan_count_numeric_by_metric: dict[str, int],
    nan_count_structural: int,
    include_reference_texts_in_output: bool,
    save_nan_rows: bool,
) -> tuple[dict[str, Any], dict[str, Path], pd.DataFrame]:
    """Save one eval split's tensor bundle plus long-format parquet/csv tables."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pt_path = output_dir / f"{split_name}_pointwise_mle.pt"
    parquet_path = output_dir / f"{split_name}_pointwise_mle_long.parquet"
    csv_path = output_dir / f"{split_name}_pointwise_mle_long.csv"
    pointwise_id = pointwise_metrics["mle"].contiguous()
    pointwise_ess = pointwise_metrics.get("ess")
    reference_setup_signature = build_reference_setup_signature(reference_setup)
    query_selection_signature = build_query_selection_signature(
        query_indices=query_metadata["query_indices"],
        sample_kind=sample_kind,
        query_source_kind=query_split.source_kind,
        query_source_file=query_split.source_file,
    )
    split_setup_signature = build_split_setup_signature(
        reference_setup_signature=reference_setup_signature,
        query_selection_signature=query_selection_signature,
        common_metadata=common_metadata,
    )

    payload: dict[str, Any] = {
        "pointwise_id": pointwise_id,
        "reference_sizes_requested": list(reference_setup.reference_sizes_requested),
        "k_values_requested": list(reference_setup.k_values_requested),
        "valid_reference_size_mask": reference_setup.valid_reference_size_mask.clone().contiguous(),
        "valid_k_mask": reference_setup.valid_k_mask.clone().contiguous(),
        "reference_indices_by_size": {
            int(size): [int(index) for index in indices]
            for size, indices in reference_setup.reference_indices_by_size.items()
        },
        "reference_pool_indices": reference_setup.reference_pool_indices.clone().contiguous(),
        "ordered_reference_pool_indices": reference_setup.ordered_reference_pool_indices.clone().contiguous(),
        "eval_known_indices": reference_setup.eval_known_indices.clone().contiguous(),
        "query_indices": query_metadata["query_indices"].clone().contiguous(),
        "query_texts": list(query_metadata["texts"]),
        "query_sample_kind": sample_kind,
        "layer_names": list(common_metadata["layer_names"]),
        "num_queries": int(pointwise_id.shape[0]),
        "num_reference_pool": int(reference_setup.reference_pool_indices.numel()),
        "seed": int(common_metadata["seed"]),
        "bias_corrected": bool(bias_corrected),
        "eps": float(eps),
        "nan_count_numeric": int(nan_count_numeric_by_metric.get("mle", 0)),
        "nan_count_numeric_by_metric": {
            metric_name: int(metric_nan_count)
            for metric_name, metric_nan_count in nan_count_numeric_by_metric.items()
        },
        "nan_count_structural": int(nan_count_structural),
        "model_name": common_metadata.get("model_name"),
        "revision": common_metadata.get("revision"),
        "include_embeddings": bool(common_metadata["include_embeddings"]),
        "hidden_size": int(common_metadata["hidden_size"]),
        "num_layers": int(common_metadata["num_layers"]),
        "reference_source_file": seen_split.source_file,
        "reference_source_kind": seen_split.source_kind,
        "source_file": query_split.source_file,
        "source_kind": query_split.source_kind,
        "label_name": query_metadata.get("label_name"),
        "available_metrics": list(pointwise_metrics.keys()),
        "reference_setup_signature": reference_setup_signature,
        "query_selection_signature": query_selection_signature,
        "split_setup_signature": split_setup_signature,
        "computed_layer_indices": list(common_metadata.get("computed_layer_indices", range(int(common_metadata["num_layers"])))),
        "computed_layer_numbers": list(common_metadata.get("computed_layer_numbers", range(1, int(common_metadata["num_layers"]) + 1))),
    }
    if pointwise_ess is not None:
        payload["pointwise_ess"] = pointwise_ess.contiguous()

    labels = query_metadata.get("labels")
    if labels is not None:
        payload["labels"] = labels.clone().contiguous()

    line_indices = query_metadata.get("line_indices")
    if line_indices is not None:
        payload["line_indices"] = line_indices.clone().contiguous()

    num_chars = query_metadata.get("num_chars")
    if num_chars is not None:
        payload["num_chars"] = num_chars.clone().contiguous()

    num_words = query_metadata.get("num_words")
    if num_words is not None:
        payload["num_words"] = num_words.clone().contiguous()

    num_tokens = query_metadata.get("num_tokens")
    if num_tokens is not None:
        payload["num_tokens"] = num_tokens.clone().contiguous()

    if include_reference_texts_in_output:
        payload["reference_texts"] = [
            seen_split.texts[index]
            for index in reference_setup.ordered_reference_pool_indices.cpu().tolist()
        ]

    torch.save(payload, pt_path)
    preview_df = write_long_outputs(
        pointwise_id=pointwise_id,
        pointwise_ess=pointwise_ess,
        output_parquet_path=parquet_path,
        output_csv_path=csv_path,
        query_metadata=query_metadata,
        sample_kind=sample_kind,
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
    seen_split: SplitData,
    eval_known_payload: dict[str, Any],
    eval_unknown_payload: dict[str, Any],
    eval_known_count: int,
    eval_unknown_name: str = "eval_unknown",
) -> Path:
    """Save a combined bundle containing shared reference info and both eval splits."""
    combined_path = output_dir / "combined_pointwise_mle.pt"
    reference_info = {
        "reference_count": int(reference_setup.reference_pool_indices.numel()),
        "eval_known_count": int(eval_known_count),
        "reference_pool_indices": reference_setup.reference_pool_indices.clone().contiguous(),
        "ordered_reference_pool_indices": reference_setup.ordered_reference_pool_indices.clone().contiguous(),
        "eval_known_indices": reference_setup.eval_known_indices.clone().contiguous(),
        "reference_indices_by_size": {
            int(size): [int(index) for index in indices]
            for size, indices in reference_setup.reference_indices_by_size.items()
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
        "reference_source_file": seen_split.source_file,
        "reference_source_kind": seen_split.source_kind,
        "available_metrics": list(eval_known_payload.get("available_metrics", ["mle"])),
    }
    torch.save(
        {
            "reference_info": reference_info,
            "eval_known": eval_known_payload,
            str(eval_unknown_name): eval_unknown_payload,
        },
        combined_path,
    )
    return combined_path


def print_dataframe_preview(title: str, dataframe: pd.DataFrame) -> None:
    """Print a compact preview of a long-format dataframe."""
    print(title)
    if dataframe.empty:
        print("  <empty>")
        return
    print(dataframe.to_string(index=False))


def print_example_commands() -> None:
    """Print example CLI invocations for both input modes."""
    print("\nExample commands:")
    print("python compute_local_seen_reference_eval_known_unknown_pointwise_mle_id.py \\")
    print("  --combined_pt outputs/local_seen_unseen_pythia14b/combined_last_token_reps.pt \\")
    print("  --output_dir outputs/local_seen_unseen_pythia14b_id \\")
    print("  --save_combined_pt")
    print("")
    print("python compute_local_seen_reference_eval_known_unknown_pointwise_mle_id.py \\")
    print("  --seen_pt outputs/local_seen_unseen_pythia14b/seen_last_token_reps.pt \\")
    print("  --unseen_pt outputs/local_seen_unseen_pythia14b/unseen_last_token_reps.pt \\")
    print("  --output_dir outputs/local_seen_unseen_pythia14b_id \\")
    print("  --reshuffle_seen_before_split \\")
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

    loaded_inputs = resolve_input_mode(args)
    common_metadata = validate_compatible_rep_shapes(loaded_inputs.seen, loaded_inputs.unseen)
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

    reference_pool_indices, eval_known_indices = split_seen_into_reference_and_eval_known(
        loaded_inputs.seen.num_examples,
        reference_count=args.reference_count,
        eval_known_count=args.eval_known_count,
        reshuffle_seen_before_split=args.reshuffle_seen_before_split,
        seed=args.seed,
    )
    if loaded_inputs.unseen.num_examples < args.eval_unknown_count:
        raise ValueError(
            f"Unseen file contains only {loaded_inputs.unseen.num_examples} examples, but at least "
            f"{args.eval_unknown_count} are required."
        )
    eval_unknown_indices = torch.arange(args.eval_unknown_count, dtype=torch.long)

    valid_reference_size_mask, valid_k_mask, invalid_reference_sizes, invalid_k_by_reference_size = build_validity_masks(
        int(reference_pool_indices.numel()),
        reference_sizes_requested,
        k_values_requested,
        args.strict_reference_sizes,
        args.strict_k_values,
    )
    ordered_reference_pool_indices, reference_indices_by_size = build_nested_reference_sets(
        reference_pool_indices,
        reference_sizes_requested,
        valid_reference_size_mask,
        args.seed,
    )
    reference_setup = ReferenceSetup(
        reference_pool_indices=reference_pool_indices,
        eval_known_indices=eval_known_indices,
        eval_unknown_indices=eval_unknown_indices,
        ordered_reference_pool_indices=ordered_reference_pool_indices,
        reference_indices_by_size=reference_indices_by_size,
        reference_sizes_requested=reference_sizes_requested,
        k_values_requested=k_values_requested,
        valid_reference_size_mask=valid_reference_size_mask,
        valid_k_mask=valid_k_mask,
        invalid_reference_sizes=invalid_reference_sizes,
        invalid_k_by_reference_size=invalid_k_by_reference_size,
    )

    eval_known_query_metadata = gather_query_metadata(loaded_inputs.seen, eval_known_indices)
    eval_unknown_query_metadata = gather_query_metadata(loaded_inputs.unseen, eval_unknown_indices)

    eval_known_pointwise_metrics, eval_known_nan_numeric_by_metric = compute_ids_for_query_set(
        reference_source_reps=loaded_inputs.seen.reps,
        query_source_reps=loaded_inputs.seen.reps,
        query_indices=eval_known_indices,
        reference_indices_by_size=reference_setup.reference_indices_by_size,
        reference_sizes_requested=reference_setup.reference_sizes_requested,
        k_values_requested=reference_setup.k_values_requested,
        valid_reference_size_mask=reference_setup.valid_reference_size_mask,
        valid_k_mask=reference_setup.valid_k_mask,
        num_layers=common_metadata["num_layers"],
        device=device,
        chunk_size=args.chunk_size,
        eps=args.eps,
        bias_corrected=args.bias_corrected,
        sample_kind="eval_known",
        include_ess=args.include_ess,
        seed=args.seed,
        layer_indices=layer_indices,
    )
    eval_unknown_pointwise_metrics, eval_unknown_nan_numeric_by_metric = compute_ids_for_query_set(
        reference_source_reps=loaded_inputs.seen.reps,
        query_source_reps=loaded_inputs.unseen.reps,
        query_indices=eval_unknown_indices,
        reference_indices_by_size=reference_setup.reference_indices_by_size,
        reference_sizes_requested=reference_setup.reference_sizes_requested,
        k_values_requested=reference_setup.k_values_requested,
        valid_reference_size_mask=reference_setup.valid_reference_size_mask,
        valid_k_mask=reference_setup.valid_k_mask,
        num_layers=common_metadata["num_layers"],
        device=device,
        chunk_size=args.chunk_size,
        eps=args.eps,
        bias_corrected=args.bias_corrected,
        sample_kind=args.unseen_output_name,
        include_ess=args.include_ess,
        seed=args.seed,
        layer_indices=layer_indices,
    )

    eval_known_nan_structural = compute_structural_nan_count(
        num_queries=int(eval_known_indices.numel()),
        num_layers=len(layer_indices),
        valid_k_mask=reference_setup.valid_k_mask,
    )
    eval_unknown_nan_structural = compute_structural_nan_count(
        num_queries=int(eval_unknown_indices.numel()),
        num_layers=len(layer_indices),
        valid_k_mask=reference_setup.valid_k_mask,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    eval_known_payload, eval_known_paths, eval_known_preview = save_split_outputs(
        output_dir=output_dir,
        split_name="eval_known",
        sample_kind="eval_known",
        pointwise_metrics=eval_known_pointwise_metrics,
        query_metadata=eval_known_query_metadata,
        reference_setup=reference_setup,
        common_metadata=common_metadata,
        seen_split=loaded_inputs.seen,
        query_split=loaded_inputs.seen,
        bias_corrected=args.bias_corrected,
        eps=args.eps,
        nan_count_numeric_by_metric=eval_known_nan_numeric_by_metric,
        nan_count_structural=eval_known_nan_structural,
        include_reference_texts_in_output=args.include_reference_texts_in_output,
        save_nan_rows=args.save_nan_rows,
    )
    eval_unknown_payload, eval_unknown_paths, eval_unknown_preview = save_split_outputs(
        output_dir=output_dir,
        split_name=args.unseen_output_name,
        sample_kind=args.unseen_output_name,
        pointwise_metrics=eval_unknown_pointwise_metrics,
        query_metadata=eval_unknown_query_metadata,
        reference_setup=reference_setup,
        common_metadata=common_metadata,
        seen_split=loaded_inputs.seen,
        query_split=loaded_inputs.unseen,
        bias_corrected=args.bias_corrected,
        eps=args.eps,
        nan_count_numeric_by_metric=eval_unknown_nan_numeric_by_metric,
        nan_count_structural=eval_unknown_nan_structural,
        include_reference_texts_in_output=args.include_reference_texts_in_output,
        save_nan_rows=args.save_nan_rows,
    )

    combined_output_path = None
    if args.save_combined_pt:
        combined_output_path = save_combined_output(
            output_dir=output_dir,
            reference_setup=reference_setup,
            common_metadata=common_metadata,
            seen_split=loaded_inputs.seen,
            eval_known_payload=eval_known_payload,
            eval_unknown_payload=eval_unknown_payload,
            eval_known_count=args.eval_known_count,
            eval_unknown_name=args.unseen_output_name,
        )

    valid_reference_sizes = [
        size
        for size, is_valid in zip(
            reference_setup.reference_sizes_requested,
            reference_setup.valid_reference_size_mask.tolist(),
        )
        if is_valid
    ]

    print("\nFinal summary:")
    print(f"  input mode: {loaded_inputs.input_mode}")
    if loaded_inputs.input_mode == "combined":
        print(f"  combined file path: {loaded_inputs.combined_pt}")
    else:
        print(f"  seen file path: {loaded_inputs.seen_pt}")
        print(f"  unseen file path: {loaded_inputs.unseen_pt}")
    print(f"  number of reference sentences: {int(reference_setup.reference_pool_indices.numel())}")
    print(f"  number of eval_known sentences: {int(reference_setup.eval_known_indices.numel())}")
    print(f"  number of {args.unseen_output_name} sentences: {int(reference_setup.eval_unknown_indices.numel())}")
    print(f"  number of layers: {common_metadata['num_layers']}")
    print(f"  computed layers (1-based): {common_metadata['computed_layer_numbers']}")
    print(f"  hidden size: {common_metadata['hidden_size']}")
    print(f"  requested reference sizes: {reference_setup.reference_sizes_requested}")
    print(f"  requested k values: {reference_setup.k_values_requested}")
    print(f"  included metrics: {eval_known_payload.get('available_metrics', ['mle'])}")
    print(f"  valid reference sizes: {valid_reference_sizes}")
    print(f"  eval_known output tensor shape: {tuple(eval_known_pointwise_metrics['mle'].shape)}")
    print(f"  {args.unseen_output_name} output tensor shape: {tuple(eval_unknown_pointwise_metrics['mle'].shape)}")
    for metric_name, metric_nan_count in eval_known_nan_numeric_by_metric.items():
        print(f"  numeric NaN count for eval_known ({metric_name}): {metric_nan_count}")
    for metric_name, metric_nan_count in eval_unknown_nan_numeric_by_metric.items():
        print(f"  numeric NaN count for {args.unseen_output_name} ({metric_name}): {metric_nan_count}")
    print(f"  structural NaN count for eval_known: {eval_known_nan_structural}")
    print(f"  structural NaN count for {args.unseen_output_name}: {eval_unknown_nan_structural}")
    print(f"  eval_known .pt: {eval_known_paths['pt']}")
    print(f"  eval_known parquet: {eval_known_paths['parquet']}")
    print(f"  eval_known csv: {eval_known_paths['csv']}")
    print(f"  {args.unseen_output_name} .pt: {eval_unknown_paths['pt']}")
    print(f"  {args.unseen_output_name} parquet: {eval_unknown_paths['parquet']}")
    print(f"  {args.unseen_output_name} csv: {eval_unknown_paths['csv']}")
    if combined_output_path is not None:
        print(f"  combined .pt: {combined_output_path}")

    print_dataframe_preview("\nExample rows from eval_known long table:", eval_known_preview)
    print_dataframe_preview(f"\nExample rows from {args.unseen_output_name} long table:", eval_unknown_preview)
    print_example_commands()


if __name__ == "__main__":
    main()

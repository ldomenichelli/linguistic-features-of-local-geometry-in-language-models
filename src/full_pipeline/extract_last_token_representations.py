#!/usr/bin/env python3
"""Extract last-token representations from local seen/unseen JSONL files.

The extractor is model-agnostic for causal language models supported by
``transformers``.  A model revision is mandatory because mutable defaults such
as ``main`` are not sufficient provenance for a new reproduction run.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

IMPORT_ERROR = None

try:
    import accelerate  # noqa: F401
    import numpy as np
    import pandas as pd
    import pyarrow  # noqa: F401
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ModuleNotFoundError as exc:
    IMPORT_ERROR = exc


DEFAULT_SEEN_FILE = "data/interim/seen_excerpts.jsonl"
DEFAULT_UNSEEN_FILE = "data/interim/unseen_excerpts.jsonl"
DEFAULT_SEEN_TARGET = 17_000
DEFAULT_UNSEEN_TARGET = 2000
DEFAULT_SEEN_PILE_SET_NAMES = (
    "Pile-CC",
    "OpenWebText2",
    "PubMed Abstracts",
    "Wikipedia (en)",
    "StackExchange",
    "USPTO Backgrounds",
    "NIH ExPorter",
    "Github",
    "Enron Emails",
    "FreeLaw",
    "OpenSubtitles",
    "YoutubeSubtitles",
    "EuroParl",
    "PubMed Central",
    "Books3",
    "PhilPapers",
)
DEFAULT_UNSEEN_PILE_SET_NAMES = ("Pile-CC",)
TEXT_FIELD_PRIORITY = ("text", "sentence", "input", "content")
TOKEN_FILTER_BATCH_SIZE = 256
WORD_RE = re.compile(r"\b\w+\b", flags=re.UNICODE)


@dataclass
class ParsedExample:
    """A text sample parsed from a local JSONL row."""

    line_index: int
    text: str
    source_file: str
    pile_set_name: str | None


@dataclass
class PreparedExample:
    """A parsed example with label metadata and tokenized content."""

    line_index: int
    text: str
    source_file: str
    source_kind: str
    label: int
    label_name: str
    pile_set_name: str | None
    num_chars: int
    num_words: int
    input_ids: list[int]
    num_tokens: int
    original_num_tokens: int
    was_truncated: bool


def format_pile_set_name(pile_set_name: str | None) -> str:
    """Render optional pile-set names consistently in logs and errors."""
    return "MISSING" if pile_set_name is None else pile_set_name


def parse_args() -> argparse.Namespace:
    """Parse and validate CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Load local JSONL files, filter/split seen and unseen examples, and extract "
            "the last-token representation from every selected hidden layer of "
            "a Hugging Face causal language model."
        )
    )
    parser.add_argument("--model_name", required=True)
    parser.add_argument(
        "--revision",
        required=True,
        help="Immutable model commit hash or tag (do not use a mutable branch for new runs).",
    )

    parser.add_argument("--seen_file", default=DEFAULT_SEEN_FILE)
    parser.add_argument("--seen_target_sentences", type=int, default=DEFAULT_SEEN_TARGET)
    parser.add_argument("--seen_label", type=int, default=1)
    parser.add_argument("--seen_label_name", default="seen")
    parser.add_argument(
        "--seen_pile_set_names",
        nargs="+",
        default=list(DEFAULT_SEEN_PILE_SET_NAMES),
        help=(
            "Allowed meta.pile_set_name values for seen examples. Defaults to "
            f"{', '.join(DEFAULT_SEEN_PILE_SET_NAMES)}."
        ),
    )

    parser.add_argument("--unseen_file", default=DEFAULT_UNSEEN_FILE)
    parser.add_argument("--unseen_target_sentences", type=int, default=DEFAULT_UNSEEN_TARGET)
    parser.add_argument("--unseen_label", type=int, default=0)
    parser.add_argument("--unseen_label_name", default="unseen")
    parser.add_argument(
        "--unseen_pile_set_names",
        nargs="+",
        default=list(DEFAULT_UNSEEN_PILE_SET_NAMES),
        help=(
            "Allowed meta.pile_set_name values for unseen examples. Defaults to "
            f"{', '.join(DEFAULT_UNSEEN_PILE_SET_NAMES)}."
        ),
    )
    parser.add_argument(
        "--match_unseen_to_seen_tail_pile_set_distribution",
        action="store_true",
        help=(
            "Sample unseen examples so their exact pile_set_name counts match the final "
            "--unseen_target_sentences examples kept in the seen split. This mirrors the "
            "seen tail that becomes eval_known in the downstream pointwise-ID pipeline."
        ),
    )

    parser.add_argument("--text_key", type=str, default=None)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument(
        "--dtype",
        type=str,
        default="float32",
        choices=("float32", "float16", "bfloat16"),
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--shuffle_before_take", action="store_true")
    parser.add_argument("--min_chars", type=int, default=1)
    parser.add_argument("--max_chars", type=int, default=None)
    parser.add_argument("--min_words", type=int, default=1)
    parser.add_argument("--max_words", type=int, default=None)
    parser.add_argument("--max_tokenized_length", type=int, default=None)
    parser.add_argument("--truncate", action="store_true")
    parser.add_argument("--include_embeddings", action="store_true")
    parser.add_argument(
        "--layers",
        type=str,
        default="all",
        help=(
            "Comma-separated layer names or layer numbers to save, e.g. "
            "'2,16,31' or 'layer_2,layer_16,layer_31'. Defaults to all layers."
        ),
    )
    parser.add_argument("--device_map_auto", action="store_true")
    parser.add_argument(
        "--skip_lm_head",
        action="store_true",
        help=(
            "Run the underlying transformer body directly instead of the causal-LM wrapper. "
            "This preserves hidden states while avoiding unused vocabulary-logit computation."
        ),
    )
    parser.add_argument("--offload_folder", type=str, default=None)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--save_combined_pt", action="store_true")

    args = parser.parse_args()

    positive_int_fields = (
        "seen_target_sentences",
        "unseen_target_sentences",
        "batch_size",
        "min_chars",
        "min_words",
    )
    for field_name in positive_int_fields:
        if getattr(args, field_name) <= 0:
            parser.error(f"--{field_name} must be a positive integer.")

    optional_positive_int_fields = ("max_chars", "max_words", "max_tokenized_length")
    for field_name in optional_positive_int_fields:
        value = getattr(args, field_name)
        if value is not None and value <= 0:
            parser.error(f"--{field_name} must be positive when provided.")

    if args.max_chars is not None and args.max_chars < args.min_chars:
        parser.error("--max_chars cannot be smaller than --min_chars.")
    if args.max_words is not None and args.max_words < args.min_words:
        parser.error("--max_words cannot be smaller than --min_words.")
    if args.truncate and args.max_tokenized_length is None:
        parser.error("--truncate requires --max_tokenized_length.")
    if args.text_key is not None and not args.text_key.strip():
        parser.error("--text_key cannot be empty.")
    if not str(args.layers).strip():
        parser.error("--layers cannot be empty.")

    return args


def resolve_device(device_arg: str | None) -> torch.device:
    """Default to CUDA when available, otherwise CPU."""
    if device_arg is not None:
        return torch.device(device_arg)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def resolve_dtype(dtype_name: str) -> torch.dtype:
    """Map the CLI dtype string to a torch dtype."""
    mapping = {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }
    return mapping[dtype_name]


def validate_runtime_choices(
    *,
    seen_path: Path,
    unseen_path: Path,
    seen_target: int,
    unseen_target: int,
    seen_label: int,
    unseen_label: int,
    device: torch.device,
    dtype: torch.dtype,
    device_map_auto: bool,
) -> None:
    """Validate inputs before we start loading data or the model."""
    for path in (seen_path, unseen_path):
        if not path.exists():
            raise FileNotFoundError(f"Input file does not exist: {path}")
        if not path.is_file():
            raise ValueError(f"Input path is not a file: {path}")

    if seen_target <= 0 or unseen_target <= 0:
        raise ValueError("Both target counts must be positive integers.")
    if not isinstance(seen_label, int) or not isinstance(unseen_label, int):
        raise ValueError("Labels must be integers.")

    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError(f"Requested CUDA device '{device}' but CUDA is not available.")
    if device.type == "cpu" and dtype == torch.float16 and not device_map_auto:
        raise ValueError("float16 inference on CPU is not supported. Use float32 or bfloat16.")
    if device_map_auto and not torch.cuda.is_available() and dtype == torch.float16:
        raise ValueError(
            "float16 with --device_map_auto requires at least one CUDA device. "
            "Use float32 or bfloat16 on CPU-only machines."
        )


def count_words(text: str) -> int:
    """Count words using a lightweight regex-based tokenizer."""
    return len(WORD_RE.findall(text))


def extract_text_from_record(
    record: Any,
    *,
    line_index: int,
    text_key: str | None,
) -> tuple[str, str | None, str]:
    """Extract text from a JSONL record and report which field was used."""
    if isinstance(record, str):
        return record, None, "json_string"

    if not isinstance(record, dict):
        raise ValueError(
            f"Line {line_index} is neither a JSON object nor a raw JSON string. "
            f"Found type: {type(record).__name__}."
        )

    candidate_keys = (text_key,) if text_key is not None else TEXT_FIELD_PRIORITY
    for key in candidate_keys:
        if key in record:
            value = record[key]
            text = "" if value is None else str(value)
            pile_set_name = None
            meta = record.get("meta")
            if isinstance(meta, dict) and meta.get("pile_set_name") is not None:
                pile_set_name = str(meta["pile_set_name"])
            return text, pile_set_name, key

    available_keys = ", ".join(sorted(str(key) for key in record.keys()))
    wanted = ", ".join(candidate_keys)
    raise ValueError(
        f"Line {line_index} has no usable text field. Tried: {wanted}. "
        f"Available keys: {available_keys or '<none>'}."
    )


def parse_jsonl_texts(path: Path, text_key: str | None) -> tuple[list[ParsedExample], Counter, Counter]:
    """Parse local JSONL text samples while preserving original line indices."""
    stats = Counter()
    field_usage = Counter()
    examples: list[ParsedExample] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_index, raw_line in enumerate(
            tqdm(handle, desc=f"Parsing {path.name}", unit="line"),
            start=1,
        ):
            stats["raw_lines_read"] += 1
            if not raw_line.strip():
                stats["skipped_empty_lines"] += 1
                continue

            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                stats["skipped_invalid_json"] += 1
                continue

            if isinstance(record, dict):
                stats["json_object_records"] += 1
            elif isinstance(record, str):
                stats["json_string_records"] += 1

            text, pile_set_name, field_name = extract_text_from_record(
                record,
                line_index=line_index,
                text_key=text_key,
            )
            field_usage[field_name] += 1
            text = text.strip()

            if not text:
                stats["skipped_empty_text"] += 1
                continue

            examples.append(
                ParsedExample(
                    line_index=line_index,
                    text=text,
                    source_file=str(path),
                    pile_set_name=pile_set_name,
                )
            )
            stats["valid_texts_found"] += 1

    if not examples:
        raise ValueError(f"No usable text examples were found in {path}.")

    return examples, stats, field_usage


def filter_and_sample_examples(
    parsed_examples: Sequence[ParsedExample],
    *,
    tokenizer,
    source_kind: str,
    target_count: int,
    label: int,
    label_name: str,
    allowed_pile_set_names: Sequence[str | None],
    seed: int,
    shuffle_before_take: bool,
    min_chars: int,
    max_chars: int | None,
    min_words: int,
    max_words: int | None,
    max_tokenized_length: int | None,
    truncate: bool,
    exact_pile_set_counts: Counter | dict[str | None, int] | None = None,
) -> tuple[list[PreparedExample], Counter]:
    """Apply source/text/token filters and take an exact number of examples."""
    stats = Counter()
    allowed_pile_sets = set(allowed_pile_set_names)

    text_filtered: list[tuple[ParsedExample, int, int]] = []
    for example in tqdm(parsed_examples, desc=f"Text filters ({source_kind})", unit="example"):
        if allowed_pile_sets and example.pile_set_name not in allowed_pile_sets:
            stats["skipped_pile_set_filter"] += 1
            continue

        num_chars = len(example.text)
        if num_chars < min_chars:
            stats["skipped_min_chars"] += 1
            continue
        if max_chars is not None and num_chars > max_chars:
            stats["skipped_max_chars"] += 1
            continue

        num_words = count_words(example.text)
        if num_words < min_words:
            stats["skipped_min_words"] += 1
            continue
        if max_words is not None and num_words > max_words:
            stats["skipped_max_words"] += 1
            continue

        text_filtered.append((example, num_chars, num_words))
        stats["passed_text_filters"] += 1

    if not text_filtered:
        raise ValueError(
            f"No {source_kind} examples remained after pile-set and text-level filtering."
        )

    prepared: list[PreparedExample] = []
    for start in tqdm(
        range(0, len(text_filtered), TOKEN_FILTER_BATCH_SIZE),
        desc=f"Token filters ({source_kind})",
        unit="batch",
    ):
        batch_items = text_filtered[start : start + TOKEN_FILTER_BATCH_SIZE]
        batch_texts = [item[0].text for item in batch_items]
        encoded = tokenizer(
            batch_texts,
            add_special_tokens=False,
            padding=False,
            truncation=False,
            return_attention_mask=False,
        )

        for (parsed, num_chars, num_words), input_ids in zip(batch_items, encoded["input_ids"]):
            original_num_tokens = len(input_ids)
            if original_num_tokens == 0:
                stats["skipped_empty_tokenization"] += 1
                continue

            was_truncated = False
            kept_input_ids = list(input_ids)
            if max_tokenized_length is not None and original_num_tokens > max_tokenized_length:
                if truncate:
                    kept_input_ids = kept_input_ids[:max_tokenized_length]
                    was_truncated = True
                    stats["truncated_examples"] += 1
                else:
                    stats["skipped_max_tokenized_length"] += 1
                    continue

            prepared.append(
                PreparedExample(
                    line_index=parsed.line_index,
                    text=parsed.text,
                    source_file=parsed.source_file,
                    source_kind=source_kind,
                    label=label,
                    label_name=label_name,
                    pile_set_name=parsed.pile_set_name,
                    num_chars=num_chars,
                    num_words=num_words,
                    input_ids=kept_input_ids,
                    num_tokens=len(kept_input_ids),
                    original_num_tokens=original_num_tokens,
                    was_truncated=was_truncated,
                )
            )
            stats["passed_token_filters"] += 1

    stats["available_after_all_filters"] = len(prepared)
    if exact_pile_set_counts is None and len(prepared) < target_count:
        counts_by_pile_set = Counter(format_pile_set_name(example.pile_set_name) for example in prepared)
        raise ValueError(
            f"{source_kind} target count cannot be satisfied. Needed {target_count} examples, "
            f"but only {len(prepared)} remained after filtering {Path(parsed_examples[0].source_file).name}. "
            f"Allowed pile sets: {[format_pile_set_name(name) for name in sorted(allowed_pile_sets, key=format_pile_set_name)]}. "
            f"Remaining counts by pile_set_name: {dict(counts_by_pile_set)}."
        )

    if exact_pile_set_counts is not None:
        requested_counts = Counter(
            {
                pile_set_name: int(count)
                for pile_set_name, count in dict(exact_pile_set_counts).items()
                if int(count) > 0
            }
        )
        if sum(requested_counts.values()) != target_count:
            raise ValueError(
                "Exact pile-set sampling requested inconsistent counts: "
                f"target_count={target_count}, requested_total={sum(requested_counts.values())}."
            )

        available_counts = Counter(example.pile_set_name for example in prepared)
        missing_counts = {
            format_pile_set_name(pile_set_name): requested_count - int(available_counts.get(pile_set_name, 0))
            for pile_set_name, requested_count in requested_counts.items()
            if int(available_counts.get(pile_set_name, 0)) < requested_count
        }
        if missing_counts:
            formatted_available = {
                format_pile_set_name(pile_set_name): int(count)
                for pile_set_name, count in available_counts.items()
            }
            raise ValueError(
                f"{source_kind} exact pile-set sampling could not be satisfied from "
                f"{Path(parsed_examples[0].source_file).name}. Missing counts: {missing_counts}. "
                f"Available counts by pile_set_name: {formatted_available}."
            )

        prepared_indices_by_pile_set: dict[str | None, list[int]] = {}
        for index, example in enumerate(prepared):
            prepared_indices_by_pile_set.setdefault(example.pile_set_name, []).append(index)

        rng = np.random.default_rng(seed)
        selected_indices: list[int] = []
        for pile_set_name in sorted(requested_counts, key=format_pile_set_name):
            requested_count = requested_counts[pile_set_name]
            candidate_indices = prepared_indices_by_pile_set[pile_set_name]
            if shuffle_before_take:
                chosen = rng.choice(candidate_indices, size=requested_count, replace=False).tolist()
            else:
                chosen = candidate_indices[:requested_count]
            selected_indices.extend(int(index) for index in chosen)
            stats[f"sampled_exact_pile_set::{format_pile_set_name(pile_set_name)}"] = requested_count

        if shuffle_before_take:
            rng.shuffle(selected_indices)
            stats["sampling_mode_exact_pile_set_match_random_within_groups"] = target_count
        else:
            selected_indices.sort()
            stats["sampling_mode_exact_pile_set_match_file_order_within_groups"] = target_count

        selected = [prepared[index] for index in selected_indices]
    elif shuffle_before_take:
        rng = np.random.default_rng(seed)
        selected_indices = rng.choice(len(prepared), size=target_count, replace=False)
        selected = [prepared[int(index)] for index in selected_indices]
        stats["sampling_mode_shuffle_without_replacement"] = target_count
    else:
        selected = prepared[:target_count]
        stats["sampling_mode_file_order"] = target_count

    stats["sampled_examples_kept"] = len(selected)
    return selected, stats


def tokenize_batch(examples: Sequence[PreparedExample], pad_token_id: int) -> dict[str, torch.Tensor]:
    """Pad pre-tokenized inputs and build attention masks."""
    if not examples:
        raise ValueError("tokenize_batch received an empty batch.")

    max_len = max(example.num_tokens for example in examples)
    input_ids = torch.full((len(examples), max_len), pad_token_id, dtype=torch.long)
    attention_mask = torch.zeros((len(examples), max_len), dtype=torch.long)

    for row_index, example in enumerate(examples):
        ids = torch.tensor(example.input_ids, dtype=torch.long)
        input_ids[row_index, : ids.numel()] = ids
        attention_mask[row_index, : ids.numel()] = 1

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
    }


def infer_model_input_device(model, fallback_device: torch.device) -> torch.device:
    """Find the device that should receive input IDs."""
    try:
        embedding_weight = model.get_input_embeddings().weight
        if embedding_weight.device.type != "meta":
            return embedding_weight.device
    except Exception:
        pass

    for parameter in model.parameters():
        if parameter.device.type != "meta":
            return parameter.device

    return fallback_device


def resolve_inference_model(model, *, skip_lm_head: bool):
    """Return the forward module used for hidden-state extraction."""
    if not skip_lm_head:
        return model

    base_model = getattr(model, "base_model", None)
    if base_model is None or base_model is model:
        raise ValueError(
            "--skip_lm_head was requested, but the loaded causal LM does not expose "
            "a distinct base_model module."
        )
    return base_model


def maybe_load_model_low_memory(
    args: argparse.Namespace,
    *,
    dtype: torch.dtype,
    device: torch.device,
):
    """Load tokenizer/model in normal mode or with device_map='auto'."""
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        revision=args.revision,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        if tokenizer.eos_token is None:
            raise ValueError("Tokenizer has no pad_token or eos_token; cannot safely batch inputs.")
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model_kwargs: dict[str, Any] = {
        "revision": args.revision,
        "torch_dtype": dtype,
        "low_cpu_mem_usage": True,
    }

    low_memory_used = bool(args.device_map_auto)
    if low_memory_used:
        model_kwargs["device_map"] = "auto"
        if args.offload_folder is not None:
            offload_folder = Path(args.offload_folder)
            offload_folder.mkdir(parents=True, exist_ok=True)
            model_kwargs["offload_folder"] = str(offload_folder)
        print(
            f"Loading {args.model_name} with device_map='auto', revision={args.revision}, "
            f"dtype={args.dtype}."
        )
    else:
        print(
            f"Loading {args.model_name} on device {device}, revision={args.revision}, "
            f"dtype={args.dtype}."
        )

    model = AutoModelForCausalLM.from_pretrained(args.model_name, **model_kwargs)

    if not low_memory_used:
        model = model.to(device)

    model.eval()
    input_device = infer_model_input_device(model, device)
    return model, tokenizer, input_device, low_memory_used


def build_layer_names(num_layers: int, include_embeddings: bool) -> list[str]:
    """Create readable layer names that match the saved tensor layout."""
    if include_embeddings:
        return ["embedding"] + [f"layer_{index}" for index in range(1, num_layers)]
    return [f"layer_{index}" for index in range(1, num_layers + 1)]


def layer_number_from_name(layer_name: str, fallback_idx: int) -> int:
    """Return the human-facing model layer number for a saved layer name."""
    if layer_name == "embedding":
        return 0
    match = re.fullmatch(r"layer_(\d+)", str(layer_name))
    if match:
        return int(match.group(1))
    return int(fallback_idx) + 1


def resolve_layer_indices(layer_selector: str, layer_names: Sequence[str]) -> list[int]:
    """Resolve comma-separated layer names/numbers against available layer names."""
    selector = str(layer_selector).strip()
    if selector.lower() == "all":
        return list(range(len(layer_names)))

    name_to_idx = {str(name): idx for idx, name in enumerate(layer_names)}
    indices: list[int] = []
    seen: set[int] = set()
    for raw in selector.split(","):
        item = raw.strip()
        if not item:
            continue
        if item in name_to_idx:
            idx = name_to_idx[item]
        else:
            try:
                value = int(item)
            except ValueError as exc:
                raise ValueError(f"Unknown layer selector {item!r}.") from exc

            named_layer = f"layer_{value}"
            if named_layer in name_to_idx:
                idx = name_to_idx[named_layer]
            elif value == 0 and "embedding" in name_to_idx:
                idx = name_to_idx["embedding"]
            elif 1 <= value <= len(layer_names):
                idx = value - 1
            else:
                raise ValueError(
                    f"Layer selector {item!r} is outside available layers "
                    f"1..{len(layer_names)} and does not match any layer name."
                )
        if idx not in seen:
            indices.append(idx)
            seen.add(idx)

    if not indices:
        raise ValueError("No layers were selected.")
    return indices


def extract_last_token_reps(
    inference_model,
    examples: Sequence[PreparedExample],
    *,
    batch_size: int,
    pad_token_id: int,
    include_embeddings: bool,
    input_device: torch.device,
    source_kind: str,
    layer_selector: str,
) -> dict[str, Any]:
    """Extract the last non-padding token representation from every selected layer."""
    rep_batches: list[torch.Tensor] = []
    full_layer_names: list[str] | None = None
    selected_layer_indices: list[int] | None = None
    selected_layer_names: list[str] | None = None

    with torch.inference_mode():
        for start in tqdm(
            range(0, len(examples), batch_size),
            desc=f"Inference ({source_kind})",
            unit="batch",
        ):
            batch_examples = examples[start : start + batch_size]
            batch = tokenize_batch(batch_examples, pad_token_id)
            input_ids = batch["input_ids"].to(input_device)
            attention_mask = batch["attention_mask"].to(input_device)

            outputs = inference_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                use_cache=False,
                return_dict=True,
            )
            hidden_states = outputs.hidden_states
            if hidden_states is None:
                raise RuntimeError("Model did not return hidden states.")

            selected_states = hidden_states if include_embeddings else hidden_states[1:]
            if not selected_states:
                raise RuntimeError("No hidden states were selected for extraction.")

            current_layer_names = build_layer_names(len(selected_states), include_embeddings)
            if selected_layer_indices is None:
                full_layer_names = current_layer_names
                selected_layer_indices = resolve_layer_indices(layer_selector, current_layer_names)
                selected_layer_names = [current_layer_names[idx] for idx in selected_layer_indices]
            elif current_layer_names != full_layer_names:
                raise RuntimeError("Layer layout changed between inference batches.")

            last_idx = attention_mask.sum(dim=1) - 1
            batch_indices = torch.arange(input_ids.size(0), device=input_ids.device)
            batch_reps = torch.stack(
                [selected_states[idx][batch_indices, last_idx] for idx in selected_layer_indices],
                dim=1,
            ).detach().to("cpu", dtype=torch.float32).contiguous()

            rep_batches.append(batch_reps)

    if not rep_batches:
        raise RuntimeError(f"No representations were extracted for {source_kind}.")

    reps = torch.cat(rep_batches, dim=0).contiguous()
    num_layers = int(reps.shape[1])
    hidden_size = int(reps.shape[2])
    if selected_layer_indices is None or selected_layer_names is None or full_layer_names is None:
        raise RuntimeError(f"No layer metadata was resolved for {source_kind}.")

    return {
        "reps": reps,
        "num_layers": num_layers,
        "hidden_size": hidden_size,
        "layer_names": selected_layer_names,
        "full_num_layers": len(full_layer_names),
        "full_layer_names": full_layer_names,
        "selected_layer_indices": selected_layer_indices,
        "selected_layer_numbers": [
            layer_number_from_name(layer_name, layer_idx)
            for layer_name, layer_idx in zip(selected_layer_names, selected_layer_indices)
        ],
    }


def build_metadata_frame(examples: Sequence[PreparedExample]) -> pd.DataFrame:
    """Create a metadata table for parquet/csv export."""
    return pd.DataFrame(
        {
            "example_index": np.arange(len(examples), dtype=np.int64),
            "line_index": [example.line_index for example in examples],
            "label": [example.label for example in examples],
            "label_name": [example.label_name for example in examples],
            "text": [example.text for example in examples],
            "source_kind": [example.source_kind for example in examples],
            "source_file": [example.source_file for example in examples],
            "pile_set_name": [example.pile_set_name for example in examples],
            "num_chars": [example.num_chars for example in examples],
            "num_words": [example.num_words for example in examples],
            "num_tokens": [example.num_tokens for example in examples],
            "original_num_tokens": [example.original_num_tokens for example in examples],
            "was_truncated": [example.was_truncated for example in examples],
        }
    )


def save_split_outputs(
    output_dir: Path,
    *,
    split_name: str,
    source_kind: str,
    examples: Sequence[PreparedExample],
    extraction: dict[str, Any],
    label_name: str,
    model_name: str,
    revision: str,
    include_embeddings: bool,
    seed: int,
) -> tuple[dict[str, Any], dict[str, Path]]:
    """Save one split's tensors and metadata in .pt/.parquet/.csv formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_df = build_metadata_frame(examples)

    pt_path = output_dir / f"{split_name}_last_token_reps.pt"
    parquet_path = output_dir / f"{split_name}_metadata.parquet"
    csv_path = output_dir / f"{split_name}_metadata.csv"

    payload = {
        "reps": extraction["reps"].contiguous(),
        "labels": torch.tensor([example.label for example in examples], dtype=torch.long).contiguous(),
        "label_name": label_name,
        "texts": [example.text for example in examples],
        "source_file": examples[0].source_file if examples else "",
        "source_kind": source_kind,
        "line_indices": torch.tensor(
            [example.line_index for example in examples],
            dtype=torch.long,
        ).contiguous(),
        "num_chars": torch.tensor(
            [example.num_chars for example in examples],
            dtype=torch.long,
        ).contiguous(),
        "num_words": torch.tensor(
            [example.num_words for example in examples],
            dtype=torch.long,
        ).contiguous(),
        "num_tokens": torch.tensor(
            [example.num_tokens for example in examples],
            dtype=torch.long,
        ).contiguous(),
        "model_name": model_name,
        "revision": revision,
        "layer_names": extraction["layer_names"],
        "full_num_layers": extraction.get("full_num_layers", extraction["num_layers"]),
        "full_layer_names": extraction.get("full_layer_names", extraction["layer_names"]),
        "selected_layer_indices": extraction.get("selected_layer_indices"),
        "selected_layer_numbers": extraction.get("selected_layer_numbers"),
        "include_embeddings": include_embeddings,
        "hidden_size": extraction["hidden_size"],
        "num_layers": extraction["num_layers"],
        "seed": seed,
        "pile_set_names": [example.pile_set_name for example in examples],
        "original_num_tokens": torch.tensor(
            [example.original_num_tokens for example in examples],
            dtype=torch.long,
        ).contiguous(),
        "was_truncated": torch.tensor(
            [1 if example.was_truncated else 0 for example in examples],
            dtype=torch.long,
        ).contiguous(),
    }

    torch.save(payload, pt_path)
    metadata_df.to_parquet(parquet_path, index=False)
    metadata_df.to_csv(csv_path, index=False)

    return payload, {
        "pt": pt_path,
        "parquet": parquet_path,
        "csv": csv_path,
    }


def save_combined_output(
    output_dir: Path,
    *,
    seen_payload: dict[str, Any],
    unseen_payload: dict[str, Any],
) -> Path:
    """Optionally save one combined .pt bundle that references both splits."""
    combined_path = output_dir / "combined_last_token_reps.pt"
    combined_payload = {
        "seen": seen_payload,
        "unseen": unseen_payload,
        "combined_labels": torch.cat(
            [seen_payload["labels"], unseen_payload["labels"]],
            dim=0,
        ).contiguous(),
        "combined_texts": list(seen_payload["texts"]) + list(unseen_payload["texts"]),
        "combined_source_kind": (
            [seen_payload["source_kind"]] * len(seen_payload["texts"])
            + [unseen_payload["source_kind"]] * len(unseen_payload["texts"])
        ),
    }
    torch.save(combined_payload, combined_path)
    return combined_path


def print_counter(title: str, counter: Counter) -> None:
    """Pretty-print a counter with stable ordering."""
    print(title)
    for key in sorted(counter):
        print(f"  {key}: {counter[key]}")


def print_field_usage(title: str, field_usage: Counter) -> None:
    """Report which text field(s) were used during parsing."""
    print(title)
    for field_name, count in field_usage.most_common():
        print(f"  {field_name}: {count}")


def print_examples(title: str, lines: Sequence[str]) -> None:
    """Print a titled block of example shell commands."""
    print(title)
    for line in lines:
        print(line)


def main() -> None:
    """Entry point."""
    args = parse_args()
    if IMPORT_ERROR is not None:
        raise ModuleNotFoundError(
            "Missing required package(s). Install them with "
            "`python3 -m pip install -r requirements.txt`."
        ) from IMPORT_ERROR

    seen_path = Path(args.seen_file)
    unseen_path = Path(args.unseen_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    device = resolve_device(args.device)
    dtype = resolve_dtype(args.dtype)
    validate_runtime_choices(
        seen_path=seen_path,
        unseen_path=unseen_path,
        seen_target=args.seen_target_sentences,
        unseen_target=args.unseen_target_sentences,
        seen_label=args.seen_label,
        unseen_label=args.unseen_label,
        device=device,
        dtype=dtype,
        device_map_auto=args.device_map_auto,
    )

    if args.device_map_auto and args.device is not None:
        print("Note: --device is ignored when --device_map_auto is enabled.")

    model, tokenizer, input_device, low_memory_used = maybe_load_model_low_memory(
        args,
        dtype=dtype,
        device=device,
    )
    inference_model = resolve_inference_model(model, skip_lm_head=bool(args.skip_lm_head))

    seen_examples_raw, seen_parse_stats, seen_field_usage = parse_jsonl_texts(
        seen_path,
        args.text_key,
    )
    unseen_examples_raw, unseen_parse_stats, unseen_field_usage = parse_jsonl_texts(
        unseen_path,
        args.text_key,
    )

    print_counter("\nSeen parse counts:", seen_parse_stats)
    print_field_usage("Seen text field usage:", seen_field_usage)
    print_counter("\nUnseen parse counts:", unseen_parse_stats)
    print_field_usage("Unseen text field usage:", unseen_field_usage)

    seen_examples = filter_and_sample_examples(
        seen_examples_raw,
        tokenizer=tokenizer,
        source_kind="seen",
        target_count=args.seen_target_sentences,
        label=args.seen_label,
        label_name=args.seen_label_name,
        allowed_pile_set_names=args.seen_pile_set_names,
        seed=args.seed,
        shuffle_before_take=args.shuffle_before_take,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        min_words=args.min_words,
        max_words=args.max_words,
        max_tokenized_length=args.max_tokenized_length,
        truncate=args.truncate,
    )
    seen_selected, seen_filter_stats = seen_examples

    unseen_exact_pile_set_counts: Counter | None = None
    unseen_allowed_pile_set_names: Sequence[str | None] = args.unseen_pile_set_names
    if args.match_unseen_to_seen_tail_pile_set_distribution:
        if len(seen_selected) < args.unseen_target_sentences:
            raise ValueError(
                "Cannot match unseen pile-set counts to the seen tail because the seen split "
                f"contains only {len(seen_selected)} selected examples, fewer than "
                f"--unseen_target_sentences={args.unseen_target_sentences}."
            )
        seen_tail = seen_selected[-args.unseen_target_sentences :]
        unseen_exact_pile_set_counts = Counter(example.pile_set_name for example in seen_tail)
        unseen_allowed_pile_set_names = list(unseen_exact_pile_set_counts.keys())
        print_counter(
            "\nTarget unseen pile-set counts from seen tail:",
            Counter(
                {
                    format_pile_set_name(pile_set_name): count
                    for pile_set_name, count in unseen_exact_pile_set_counts.items()
                }
            ),
        )

    unseen_examples = filter_and_sample_examples(
        unseen_examples_raw,
        tokenizer=tokenizer,
        source_kind="unseen",
        target_count=args.unseen_target_sentences,
        label=args.unseen_label,
        label_name=args.unseen_label_name,
        allowed_pile_set_names=unseen_allowed_pile_set_names,
        seed=args.seed,
        shuffle_before_take=args.shuffle_before_take,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        min_words=args.min_words,
        max_words=args.max_words,
        max_tokenized_length=args.max_tokenized_length,
        truncate=args.truncate,
        exact_pile_set_counts=unseen_exact_pile_set_counts,
    )
    unseen_selected, unseen_filter_stats = unseen_examples

    print_counter("\nSeen filter/sample counts:", seen_filter_stats)
    print_counter("\nUnseen filter/sample counts:", unseen_filter_stats)

    seen_extraction = extract_last_token_reps(
        inference_model,
        seen_selected,
        batch_size=args.batch_size,
        pad_token_id=tokenizer.pad_token_id,
        include_embeddings=args.include_embeddings,
        input_device=input_device,
        source_kind="seen",
        layer_selector=args.layers,
    )
    unseen_extraction = extract_last_token_reps(
        inference_model,
        unseen_selected,
        batch_size=args.batch_size,
        pad_token_id=tokenizer.pad_token_id,
        include_embeddings=args.include_embeddings,
        input_device=input_device,
        source_kind="unseen",
        layer_selector=args.layers,
    )

    if (
        seen_extraction["hidden_size"] != unseen_extraction["hidden_size"]
        or seen_extraction["num_layers"] != unseen_extraction["num_layers"]
        or seen_extraction["layer_names"] != unseen_extraction["layer_names"]
    ):
        raise RuntimeError("Seen and unseen extraction metadata do not match.")

    seen_payload, seen_paths = save_split_outputs(
        output_dir,
        split_name="seen",
        source_kind="seen",
        examples=seen_selected,
        extraction=seen_extraction,
        label_name=args.seen_label_name,
        model_name=args.model_name,
        revision=args.revision,
        include_embeddings=args.include_embeddings,
        seed=args.seed,
    )
    unseen_payload, unseen_paths = save_split_outputs(
        output_dir,
        split_name="unseen",
        source_kind="unseen",
        examples=unseen_selected,
        extraction=unseen_extraction,
        label_name=args.unseen_label_name,
        model_name=args.model_name,
        revision=args.revision,
        include_embeddings=args.include_embeddings,
        seed=args.seed,
    )

    combined_path = None
    if args.save_combined_pt:
        combined_path = save_combined_output(
            output_dir,
            seen_payload=seen_payload,
            unseen_payload=unseen_payload,
        )

    print("\nFinal summary:")
    print(f"  seen examples collected: {len(seen_selected)}")
    print(f"  unseen examples collected: {len(unseen_selected)}")
    print(f"  seen reps shape: {tuple(seen_payload['reps'].shape)}")
    print(f"  unseen reps shape: {tuple(unseen_payload['reps'].shape)}")
    print(f"  hidden size: {seen_extraction['hidden_size']}")
    print(f"  number of layers: {seen_extraction['num_layers']}")
    print(f"  saved layers: {', '.join(seen_extraction['layer_names'])}")
    print(f"  include embeddings: {args.include_embeddings}")
    print(f"  low-memory mode used: {low_memory_used}")
    print(f"  causal LM head skipped: {args.skip_lm_head}")
    print(f"  model input device: {input_device}")
    print(f"  seen .pt path: {seen_paths['pt']}")
    print(f"  seen metadata parquet: {seen_paths['parquet']}")
    print(f"  seen metadata csv: {seen_paths['csv']}")
    print(f"  unseen .pt path: {unseen_paths['pt']}")
    print(f"  unseen metadata parquet: {unseen_paths['parquet']}")
    print(f"  unseen metadata csv: {unseen_paths['csv']}")
    if combined_path is not None:
        print(f"  combined .pt path: {combined_path}")

    print_examples(
        "\nExample commands:",
        [
            "python extract_local_seen_unseen_pythia14b_last_token_reps.py \\",
            "  --output_dir outputs/local_seen_unseen_pythia14b \\",
            "  --shuffle_before_take \\",
            "  --save_combined_pt",
            "",
            "python extract_local_seen_unseen_pythia14b_last_token_reps.py \\",
            "  --output_dir outputs/local_seen_unseen_pythia14b_lowmem \\",
            "  --shuffle_before_take \\",
            "  --batch_size 2 \\",
            "  --dtype float16 \\",
            "  --device_map_auto \\",
            "  --offload_folder outputs/offload \\",
            "  --save_combined_pt",
        ],
    )


if __name__ == "__main__":
    main()

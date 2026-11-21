#!/usr/bin/env python3
"""Rebuild cleaned local JSONL inputs from 00.jsonl and test.jsonl."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

TRANSFORMERS_IMPORT_ERROR = None

try:
    from transformers import AutoTokenizer
except ModuleNotFoundError as exc:
    TRANSFORMERS_IMPORT_ERROR = exc


DEFAULT_SEEN_SOURCE = Path("data/raw/pile/train/00.jsonl")
DEFAULT_UNSEEN_SOURCE = Path("data/raw/pile/test.jsonl")
DEFAULT_SEEN_OUTPUT = Path("data/interim/seen_excerpts.jsonl")
DEFAULT_UNSEEN_OUTPUT = Path("data/interim/unseen_excerpts.jsonl")
DEFAULT_TOKENIZER_NAME = "EleutherAI/pythia-1.4b"
DEFAULT_TOKENIZER_REVISION = "fedc38a16eea3bd36a96b906d78d11d2ce18ed79"
TEXT_FIELD_PRIORITY = ("text", "sentence", "input", "content")

WHITESPACE_RE = re.compile(r"\s+")
WORD_RE = re.compile(r"\b\w+\b", flags=re.UNICODE)
TOKEN_RE = re.compile(r"\w+|[^\w\s]", flags=re.UNICODE)
NUMBER_RE = re.compile(r"\b\d+(?:[.,:/-]\d+)*\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PERIOD_BOUNDARY_RE = re.compile(r"\.(?=\s|$)")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
CODE_OPERATOR_RE = re.compile(r"(::|->|=>|==|!=|<=|>=|\+\+|--|&&|\|\|)")
CODE_KEYWORD_RE = re.compile(
    r"\b("
    r"import|from|def|class|function|return|const|let|var|public|private|protected|"
    r"package|namespace|include|pragma|console\.log|printf|LinearLayout|TextView|"
    r"ApplicationWindow|MessageDialog|SELECT|INSERT|UPDATE|DELETE"
    r")\b",
    flags=re.IGNORECASE,
)
IDENTIFIER_RE = re.compile(r"\b(?:[A-Za-z]+_[A-Za-z0-9_]+|[a-z]+[A-Z][A-Za-z0-9]+)\b")
PATHISH_RE = re.compile(r"(?:[A-Za-z]:\\|/)[^\s]+")
LICENSE_RE = re.compile(
    r"\b(?:copyright|all rights reserved|licensed under|apache license|bsd license)\b",
    flags=re.IGNORECASE,
)
SYMBOL_CHARS = set("{}[]<>;=/\\")


TokenCounter = Callable[[str], int]
TextTruncator = Callable[[str, int], str | None]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild the local seen/unseen JSONL files with prose-only filtering, "
            "email/code/number suppression, and period-boundary truncation."
        )
    )
    parser.add_argument("--seen_source", type=Path, default=DEFAULT_SEEN_SOURCE)
    parser.add_argument("--unseen_source", type=Path, default=DEFAULT_UNSEEN_SOURCE)
    parser.add_argument("--seen_output", type=Path, default=DEFAULT_SEEN_OUTPUT)
    parser.add_argument("--unseen_output", type=Path, default=DEFAULT_UNSEEN_OUTPUT)
    parser.add_argument("--max_tokens", type=int, default=100)
    parser.add_argument("--min_words", type=int, default=6)
    parser.add_argument(
        "--tokenizer_mode",
        choices=("pythia", "regex"),
        default="pythia",
        help="Tokenizer used for truncation. Defaults to the real Pythia tokenizer.",
    )
    parser.add_argument(
        "--tokenizer_name",
        type=str,
        default=DEFAULT_TOKENIZER_NAME,
        help="Tokenizer model name used when --tokenizer_mode=pythia.",
    )
    parser.add_argument(
        "--tokenizer_revision",
        type=str,
        default=DEFAULT_TOKENIZER_REVISION,
        help="Tokenizer revision used when --tokenizer_mode=pythia.",
    )
    args = parser.parse_args()

    if args.max_tokens <= 0:
        parser.error("--max_tokens must be a positive integer.")
    if args.min_words <= 0:
        parser.error("--min_words must be a positive integer.")

    return args


@lru_cache(maxsize=None)
def load_tokenizer(tokenizer_name: str, tokenizer_revision: str):
    if TRANSFORMERS_IMPORT_ERROR is not None:
        raise RuntimeError(
            "transformers is required for --tokenizer_mode=pythia but is not installed."
        ) from TRANSFORMERS_IMPORT_ERROR

    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_name,
        revision=tokenizer_revision,
        use_fast=True,
    )
    if not getattr(tokenizer, "is_fast", False):
        raise RuntimeError(
            f"Tokenizer '{tokenizer_name}' must be a fast tokenizer to expose offsets."
        )
    return tokenizer


def build_token_ops(args: argparse.Namespace) -> tuple[TokenCounter, TextTruncator]:
    if args.tokenizer_mode == "regex":
        return count_regex_tokens, truncate_to_period_boundary_regex

    tokenizer = load_tokenizer(args.tokenizer_name, args.tokenizer_revision)

    def count_tokens(text: str) -> int:
        return count_model_tokens(text, tokenizer)

    def truncate_text(text: str, max_tokens: int) -> str | None:
        return truncate_to_period_boundary_model(text, max_tokens=max_tokens, tokenizer=tokenizer)

    return count_tokens, truncate_text


def extract_text_and_meta(record: Any, *, line_index: int) -> tuple[str, dict[str, Any], str]:
    """Return the text payload, metadata, and source field name."""
    if isinstance(record, str):
        return record, {}, "json_string"

    if not isinstance(record, dict):
        raise ValueError(
            f"Line {line_index} is neither a JSON object nor a raw JSON string. "
            f"Found {type(record).__name__}."
        )

    for key in TEXT_FIELD_PRIORITY:
        if key in record:
            text = "" if record[key] is None else str(record[key])
            meta = record.get("meta")
            return text, dict(meta) if isinstance(meta, dict) else {}, key

    available_keys = ", ".join(sorted(str(key) for key in record))
    raise ValueError(
        f"Line {line_index} has no supported text field. "
        f"Available keys: {available_keys or '<none>'}."
    )


def normalize_text(text: str) -> str:
    """Collapse internal whitespace while keeping punctuation intact."""
    return WHITESPACE_RE.sub(" ", text.replace("\u00a0", " ")).strip()


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_regex_tokens(text: str) -> int:
    return len(TOKEN_RE.findall(text))


def count_model_tokens(text: str, tokenizer) -> int:
    encoded = tokenizer(
        text,
        add_special_tokens=False,
        return_attention_mask=False,
    )
    return len(encoded["input_ids"])


def period_end_positions(text: str, *, char_limit: int) -> list[int]:
    return [
        match.end()
        for match in PERIOD_BOUNDARY_RE.finditer(text)
        if match.end() <= char_limit
    ]


def truncate_to_period_boundary_regex(text: str, max_tokens: int) -> str | None:
    """Keep the longest prefix within max_tokens that ends at a period boundary."""
    token_matches = list(TOKEN_RE.finditer(text))
    if not token_matches:
        return None

    if len(token_matches) <= max_tokens:
        char_limit = len(text)
    else:
        char_limit = token_matches[max_tokens - 1].end()

    period_end = None
    for match in PERIOD_BOUNDARY_RE.finditer(text):
        if match.end() <= char_limit:
            period_end = match.end()
        else:
            break

    if period_end is None:
        return None

    candidate = text[:period_end].strip()
    if not candidate.endswith("."):
        return None
    if count_regex_tokens(candidate) > max_tokens:
        return None
    return candidate


def truncate_to_period_boundary_model(text: str, *, max_tokens: int, tokenizer) -> str | None:
    """Keep the longest prefix within max_tokens model tokens that ends at a period boundary."""
    encoded = tokenizer(
        text,
        add_special_tokens=False,
        return_attention_mask=False,
        return_offsets_mapping=True,
    )
    input_ids = encoded["input_ids"]
    offsets = encoded["offset_mapping"]
    if not input_ids:
        return None

    if len(input_ids) <= max_tokens:
        char_limit = len(text)
    else:
        char_limit = max(end for _, end in offsets[:max_tokens])

    for period_end in reversed(period_end_positions(text, char_limit=char_limit)):
        candidate = text[:period_end].strip()
        if not candidate.endswith("."):
            continue
        if count_model_tokens(candidate, tokenizer) <= max_tokens:
            return candidate

    return None


def looks_like_code(text: str) -> bool:
    """Heuristic code/noise detector tuned to filter code snippets and markup."""
    score = 0

    if HTML_TAG_RE.search(text):
        score += 3
    if CODE_OPERATOR_RE.search(text):
        score += 2
    if LICENSE_RE.search(text):
        score += 2
    if CODE_KEYWORD_RE.search(text):
        score += 1
    if IDENTIFIER_RE.search(text):
        score += 1
    if PATHISH_RE.search(text):
        score += 1

    symbol_count = sum(1 for char in text if char in SYMBOL_CHARS)
    if symbol_count >= 4:
        score += 1

    return score >= 2


def has_too_many_numbers(text: str) -> bool:
    """Reject text dominated by digits, versions, dates, or enumerations."""
    number_matches = NUMBER_RE.findall(text)
    if not number_matches:
        return False

    word_count = count_words(text)
    digit_char_count = sum(char.isdigit() for char in text)
    number_ratio = len(number_matches) / max(word_count, 1)

    return (
        digit_char_count >= 24
        or len(number_matches) >= 12
        or number_ratio > 0.15
    )


def has_enough_letters(text: str) -> bool:
    alpha_count = sum(char.isalpha() for char in text)
    alnum_count = sum(char.isalnum() for char in text)
    if alnum_count == 0:
        return False
    return alpha_count / alnum_count >= 0.65


def rebuild_file(
    source_path: Path,
    output_path: Path,
    *,
    max_tokens: int,
    min_words: int,
    truncate_text: TextTruncator,
) -> Counter:
    """Rebuild one JSONL file into cleaned, sentence-bounded text chunks."""
    stats = Counter()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    with source_path.open("r", encoding="utf-8") as source_handle, tmp_path.open(
        "w",
        encoding="utf-8",
    ) as output_handle:
        for line_index, raw_line in enumerate(source_handle, start=1):
            stats["raw_lines_read"] += 1
            if not raw_line.strip():
                stats["skipped_empty_lines"] += 1
                continue

            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                stats["skipped_invalid_json"] += 1
                continue

            try:
                text, meta, field_name = extract_text_and_meta(record, line_index=line_index)
            except ValueError:
                stats["skipped_missing_text"] += 1
                continue

            stats[f"text_field_{field_name}"] += 1
            normalized_text = normalize_text(text)
            if not normalized_text:
                stats["skipped_empty_text"] += 1
                continue

            truncated_text = truncate_text(normalized_text, max_tokens)
            if truncated_text is None:
                stats["skipped_no_period_boundary_within_limit"] += 1
                continue

            if count_words(truncated_text) < min_words:
                stats["skipped_min_words"] += 1
                continue
            if EMAIL_RE.search(truncated_text):
                stats["skipped_email"] += 1
                continue
            if looks_like_code(truncated_text):
                stats["skipped_code_like"] += 1
                continue
            if has_too_many_numbers(truncated_text):
                stats["skipped_number_heavy"] += 1
                continue
            if not has_enough_letters(truncated_text):
                stats["skipped_low_letter_ratio"] += 1
                continue

            clean_meta = dict(meta)
            clean_meta["prepared_from"] = source_path.name
            clean_meta["source_line_index"] = line_index

            output_record = {
                "text": truncated_text,
                "meta": clean_meta,
            }
            output_handle.write(json.dumps(output_record, ensure_ascii=False))
            output_handle.write("\n")
            stats["written"] += 1

    tmp_path.replace(output_path)
    return stats


def print_stats(name: str, stats: Counter) -> None:
    print(f"\n{name}:")
    for key in sorted(stats):
        print(f"  {key}: {stats[key]}")


def main() -> None:
    args = parse_args()

    for path in (args.seen_source, args.unseen_source):
        if not path.exists():
            raise FileNotFoundError(f"Input file does not exist: {path}")
        if not path.is_file():
            raise ValueError(f"Input path is not a file: {path}")

    _count_tokens, truncate_text = build_token_ops(args)

    seen_stats = rebuild_file(
        args.seen_source,
        args.seen_output,
        max_tokens=args.max_tokens,
        min_words=args.min_words,
        truncate_text=truncate_text,
    )
    unseen_stats = rebuild_file(
        args.unseen_source,
        args.unseen_output,
        max_tokens=args.max_tokens,
        min_words=args.min_words,
        truncate_text=truncate_text,
    )

    print(f"Tokenizer mode: {args.tokenizer_mode}")
    if args.tokenizer_mode == "pythia":
        print(f"Tokenizer name: {args.tokenizer_name}")
        print(f"Tokenizer revision: {args.tokenizer_revision}")

    print_stats("Seen rebuild stats", seen_stats)
    print_stats("Unseen rebuild stats", unseen_stats)
    print(f"\nSeen output: {args.seen_output}")
    print(f"Unseen output: {args.unseen_output}")


if __name__ == "__main__":
    main()

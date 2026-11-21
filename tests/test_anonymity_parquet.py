"""The anonymity scan must inspect decoded Parquet content."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_anonymity import EMAIL_RE, scan_payload


def test_compressed_strings_and_metadata_are_scanned(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    address = "test" + "@" + "example.invalid"
    table = pa.table({"label": [address], "value": [0.4]})
    table = table.replace_schema_metadata({b"owner": address.encode()})
    path = tmp_path / "compressed.parquet"
    pq.write_table(table, path, compression="gzip")
    assert address.encode() in EMAIL_RE.findall(scan_payload(path))
    assert b"owner" in scan_payload(path)


def test_numeric_compression_matches_are_not_treated_as_emails():
    root = Path(__file__).resolve().parents[1]
    path = root / "data/derived/neighbourhood_locality_metrics.parquet"
    assert not EMAIL_RE.findall(scan_payload(path))
    frame = pd.read_parquet(path)
    assert {"query_source", "model", "radius_ratio"}.issubset(frame.columns)

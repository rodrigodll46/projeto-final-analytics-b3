import hashlib
import json

from src.config import DATA_PATH, MANIFEST_PATH
from src.database import read_csv


def test_delivered_snapshot_matches_manifest_and_contract():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() == manifest["sha256"]
    frame = read_csv(str(DATA_PATH))
    assert len(frame) == manifest["rows"]
    assert frame["Data"].min().date().isoformat() == manifest["first_session"]
    assert frame["Data"].max().date().isoformat() == manifest["last_session"]
    assert frame["Ativo"].nunique() == 12

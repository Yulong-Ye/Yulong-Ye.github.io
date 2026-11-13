import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from update_scholar import build_snapshot, write_snapshot


class ScholarSnapshotTests(unittest.TestCase):
    def test_scholar_dependencies_pin_legacy_bibtexparser_api(self):
        requirements_path = Path(__file__).resolve().parents[1] / "requirements-scholar.txt"
        requirements = requirements_path.read_text(encoding="utf-8").splitlines()

        self.assertIn("bibtexparser<2", requirements)

    def test_build_snapshot_extracts_all_time_metrics(self):
        author = {
            "scholar_id": "ignored-by-explicit-profile-id",
            "citedby": 448,
            "hindex": 11,
            "i10index": 11,
        }

        snapshot = build_snapshot(author, "dRAn7W4AAAAJ", "2026-11-13")

        self.assertEqual(
            snapshot,
            {
                "profileId": "dRAn7W4AAAAJ",
                "citations": 448,
                "hIndex": 11,
                "i10Index": 11,
                "updatedAt": "2026-11-13",
            },
        )

    def test_build_snapshot_accepts_zero_metrics(self):
        author = {"citedby": 0, "hindex": 0, "i10index": 0}

        snapshot = build_snapshot(author, "profile", "2026-11-13")

        self.assertEqual(snapshot["citations"], 0)
        self.assertEqual(snapshot["hIndex"], 0)
        self.assertEqual(snapshot["i10Index"], 0)

    def test_build_snapshot_rejects_missing_metrics(self):
        with self.assertRaises(ValueError):
            build_snapshot({"citedby": 448, "hindex": 11}, "profile", "2026-11-13")

    def test_write_snapshot_creates_valid_json_atomically(self):
        snapshot = {
            "profileId": "profile",
            "citations": 1,
            "hIndex": 2,
            "i10Index": 3,
            "updatedAt": "2026-11-13",
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "data" / "scholar.json"
            write_snapshot(snapshot, output_path)

            self.assertEqual(json.loads(output_path.read_text()), snapshot)
            self.assertFalse(output_path.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()

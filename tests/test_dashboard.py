"""Tests for the interactive web dashboard export (export_dashboard)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hbf_atlas.dashboard import export_dashboard
from hbf_atlas.io import load_corpus


def _corpus():
    return load_corpus(Path("data/corpus"))


class TestDashboardExport(unittest.TestCase):
    def test_export_dashboard_writes_files(self):
        corpus = _corpus()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dashboard"
            export_dashboard(corpus, out)
            self.assertTrue((out / "index.html").is_file())
            self.assertTrue((out / "dashboard.js").is_file())
            self.assertTrue((out / "style.css").is_file())
            self.assertTrue((out / "atlas-data.json").is_file())
            self.assertTrue((out / "vendor" / "three.min.js").is_file())
            self.assertTrue((out / "vendor" / "gsap.min.js").is_file())

    def test_dashboard_page_embeds_data(self):
        corpus = _corpus()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dashboard"
            export_dashboard(corpus, out)
            page = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("window.ATLAS_DATA", page)
            self.assertIn('<script type="module" src="dashboard.js"></script>', page)

    def test_atlas_data_structure(self):
        corpus = _corpus()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dashboard"
            export_dashboard(corpus, out)
            data = json.loads((out / "atlas-data.json").read_text(encoding="utf-8"))
            self.assertEqual(data["data_version"], corpus.data_version)
            # 2 claims (BC-01, BC-02) x 12 observations = 24 rows.
            self.assertEqual(len(data["rows"]), 2 * len(corpus.observations))
            self.assertEqual(len(data["observations"]), len(corpus.observations))
            self.assertEqual(len(data["claims"]), len(corpus.claims))
            for row in data["rows"]:
                self.assertIn(row["assessment"]["support"], ("supported", "contradicted", "insufficient"))

    def test_dashboard_export_is_deterministic(self):
        corpus = _corpus()
        with tempfile.TemporaryDirectory() as d:
            out1 = Path(d) / "d1"
            out2 = Path(d) / "d2"
            export_dashboard(corpus, out1)
            export_dashboard(corpus, out2)
            self.assertEqual((out1 / "index.html").read_bytes(), (out2 / "index.html").read_bytes())
            self.assertEqual((out1 / "atlas-data.json").read_bytes(), (out2 / "atlas-data.json").read_bytes())
            self.assertEqual((out1 / "vendor" / "three.min.js").read_bytes(), (out2 / "vendor" / "three.min.js").read_bytes())

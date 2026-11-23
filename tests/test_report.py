"""Report export tests: deterministic output, escaped text, link safety."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hbf_atlas.models import Claim, Context, Corpus, Observation, Review, Source
from hbf_atlas.report import export_corpus


def make_corpus() -> Corpus:
    """Small corpus with a safe and an unsafe source; escaped locator text."""
    source_bad = Source(source_id="src-bad", version="1", url="javascript:alert(1)")
    source_good = Source(
        source_id="src-good", version="1", url="https://example.org/source", figure_table="Table 2"
    )
    observation = Observation(
        obs_id="obs-1",
        source_id="src-bad",
        context=Context(study_group_id="grp-A", species="Homo sapiens", model="mouse-model"),
        readout_kind="gamma-globin-rna",
        assay={"name": "qRT-PCR", "definition": "gamma-globin mRNA / beta-actin normalized"},
        value=0.42,
        unit="%",
        denominator=30,
        time_point="post-Tx",
        sample_linkage="linked to unit 1",
        uncertainty=0.05,
        evidence_locator="<script>alert('x')</script>",
    )
    claim = Claim(
        claim_id="claim-1", text="Fetal hemoglobin rises after transfusion.", claim_type="quantitative"
    )
    review = Review(review_id="rev-1", curator_id="cur-1", reviewer_ids=["rev-a"])
    return Corpus(
        data_version="v0.2",
        sources=[source_bad, source_good],
        observations=[observation],
        claims=[claim],
        reviews=[review],
    )


def make_endpoint_corpus() -> Corpus:
    """Corpus where the 29/30 and 30/30 endpoint rows must both be visible."""
    source = Source(source_id="src-e", version="1", url="https://example.org/endpoints")
    obs_a = Observation(
        obs_id="obs-a",
        source_id="src-e",
        context=Context(study_group_id="grp-A", species="Homo sapiens"),
        readout_kind="gamma-globin-rna",
        value=29,
        unit="%",
        denominator=30,
        time_point="T0",
        evidence_locator="Table 1a",
    )
    obs_b = Observation(
        obs_id="obs-b",
        source_id="src-e",
        context=Context(study_group_id="grp-A", species="Homo sapiens"),
        readout_kind="gamma-globin-rna",
        value=30,
        unit="%",
        denominator=30,
        time_point="T0",
        evidence_locator="Table 1b",
    )
    claim = Claim(
        claim_id="claim-e",
        text="The 30/30 endpoint differs from the 29/30 event rule.",
        claim_type="comparative",
    )
    return Corpus(
        data_version="v0.3",
        sources=[source],
        observations=[obs_a, obs_b],
        claims=[claim],
        reviews=[],
    )


class TestReportExport(unittest.TestCase):
    def test_export_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            out1 = Path(tmp) / "r1"
            out2 = Path(tmp) / "r2"
            export_corpus(make_corpus(), out1)
            export_corpus(make_corpus(), out2)
            self.assertEqual((out1 / "index.html").read_bytes(), (out2 / "index.html").read_bytes())
            self.assertEqual((out1 / "data.json").read_bytes(), (out2 / "data.json").read_bytes())
            vendor1 = sorted(p.name for p in (out1 / "vendor").iterdir())
            vendor2 = sorted(p.name for p in (out2 / "vendor").iterdir())
            self.assertEqual(vendor1, vendor2)

    def test_endpoint_display_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report"
            export_corpus(make_endpoint_corpus(), output)
            data = json.loads((output / "data.json").read_text(encoding="utf-8"))
            pairs = {(row["obs"]["value"], row["obs"]["denominator"]) for row in data["rows"]}
            self.assertIn((29, 30), pairs)
            self.assertIn((30, 30), pairs)

    def test_imported_text_escaped_in_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report"
            export_corpus(make_corpus(), output)
            html = (output / "index.html").read_text(encoding="utf-8")
            data_json = (output / "data.json").read_text(encoding="utf-8")
            self.assertNotIn("<script>alert('x')", html)
            expected = "".join(
                [
                    chr(92) + "u003c",
                    "script",
                    chr(92) + "u003e",
                    "alert('x')",
                    chr(92) + "u003c",
                    "/script",
                    chr(92) + "u003e",
                ]
            )
            self.assertIn(expected, html)
            self.assertIn("<script>alert('x')</script>", data_json)

    def test_unsafe_links_not_clickable(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report"
            export_corpus(make_corpus(), output)
            html = (output / "index.html").read_text(encoding="utf-8")
            js = (output / "atlas.js").read_text(encoding="utf-8")
            self.assertNotIn('href="javascript:', html)
            self.assertIn("isSafeLink", js)
            self.assertIn("unsafe-link", js)
            self._check_is_safe_link_node(output / "atlas.js")

    def _check_is_safe_link_node(self, atlas_js: Path) -> None:
        """Run a generated node script that extracts and calls isSafeLink."""
        node = shutil.which("node")
        if node is None:
            self.skipTest("node not available")
        check_script = (
            "const fs = require('fs');\n"
            f"const src = fs.readFileSync({str(atlas_js)!r}, 'utf8');\n"
            "const m = src.match(/function isSafeLink\\s*\\(url\\)\\s*\\{[\\s\\S]*?\\n\\}/);\n"
            "if (!m) { console.log(JSON.stringify({missing: true})); process.exit(1); }\n"
            "const isSafeLink = new Function(m[0] + '\\nreturn isSafeLink;')();\n"
            "console.log(JSON.stringify({\n"
            "  https_ok: isSafeLink('https://example.org/x') === true,\n"
            "  js_blocked: isSafeLink('javascript:alert(1)') === false\n"
            "}));\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
            handle.write(check_script)
            script_path = handle.name
        try:
            result = subprocess.run(
                [node, script_path], capture_output=True, text=True, timeout=30, check=False
            )
        finally:
            os.unlink(script_path)
        self.assertEqual(result.returncode, 0, f"node check failed: {result.stdout}{result.stderr}")
        parsed = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertTrue(parsed.get("https_ok"), f"isSafeLink('https://example.org/x') should be true: {parsed}")
        self.assertTrue(
            parsed.get("js_blocked"), f"isSafeLink('javascript:alert(1)') should be false: {parsed}"
        )


if __name__ == "__main__":
    unittest.main()

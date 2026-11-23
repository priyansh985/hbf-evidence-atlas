"""Interactive web dashboard export for the HbF evidence atlas.

``export_dashboard`` writes the dashboard into ``output_dir``:

- ``index.html`` — the static shell from ``static/dashboard/index.html`` with
  the export embedded as ``window.ATLAS_DATA`` (escaped so ``&``, ``<`` and
  ``>`` become ``\\u0026``, ``\\u003c`` and ``\\u003e``; the page runs fully
  offline).
- ``atlas-data.json`` — the same export (``sort_keys=True, indent=2`` plus a
  trailing newline).
- ``dashboard.js`` and ``style.css`` — static assets from
  ``static/dashboard/``.
- ``vendor/`` — a copy of ``static/vendor/``.

The dashboard provides a search box, four filters (readout, study type,
intervention, evidence status), a case table with an evidence panel, and a
Three.js map of the observations (points placed by time point and support
level, colored by readout kind, sized by denominator).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from hbf_atlas.models import Corpus
from hbf_atlas.report import STATIC_DIR, build_export

DASHBOARD_STATIC = STATIC_DIR / "dashboard"


def export_dashboard(corpus: Corpus, output_dir: Path) -> None:
    """Write the interactive dashboard into ``output_dir`` (created if needed)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    export = build_export(corpus)

    embedded = json.dumps(export, sort_keys=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = (DASHBOARD_STATIC / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(template.replace("__ATLAS_DATA__", embedded), encoding="utf-8")

    (output_dir / "atlas-data.json").write_text(json.dumps(export, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    for name in ("dashboard.js", "style.css"):
        shutil.copy2(DASHBOARD_STATIC / name, output_dir / name)

    vendor_dst = output_dir / "vendor"
    if vendor_dst.exists():
        shutil.rmtree(vendor_dst)
    shutil.copytree(STATIC_DIR / "vendor", vendor_dst)

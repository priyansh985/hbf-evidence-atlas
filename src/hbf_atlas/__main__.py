"""Command-line interface for the HbF evidence atlas build tools.

Usage:

    py -m hbf_atlas validate <corpus_dir>
    py -m hbf_atlas build-report <corpus_dir> <output_dir>

``validate`` prints validation issues for a corpus directory and exits with
status 1 when any issue has ERROR severity.  ``build-report`` validates the
corpus (exiting 1 on ERRORs) and then exports the static atlas report into
``output_dir``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hbf_atlas.dashboard import export_dashboard
from hbf_atlas.io import load_corpus, validate_corpus
from hbf_atlas.models import Corpus, Issue, Severity
from hbf_atlas.report import export_corpus


def _print_issues(issues: list[Issue]) -> None:
    for issue in issues:
        print(f"{issue.severity.value}: {issue.record_id}: {issue.field}: {issue.message}")


def _has_errors(issues: list[Issue]) -> bool:
    return any(issue.severity is Severity.ERROR for issue in issues)


def _load_and_validate(corpus_dir: Path) -> tuple[Corpus, list[Issue]] | None:
    """Load and validate a corpus directory.

    Returns ``None`` after printing the load error to stderr.
    """
    try:
        corpus = load_corpus(corpus_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return None
    return corpus, validate_corpus(corpus)


def cmd_validate(corpus_dir: Path) -> int:
    loaded = _load_and_validate(corpus_dir)
    if loaded is None:
        return 1
    _, issues = loaded
    _print_issues(issues)
    if not issues:
        print("valid")
    return 1 if _has_errors(issues) else 0


def cmd_build_report(corpus_dir: Path, output_dir: Path) -> int:
    loaded = _load_and_validate(corpus_dir)
    if loaded is None:
        return 1
    corpus, issues = loaded
    _print_issues(issues)
    if _has_errors(issues):
        print("error: validation failed; report not written", file=sys.stderr)
        return 1
    export_corpus(corpus, output_dir)
    for written in (
        output_dir / "index.html",
        output_dir / "data.json",
        output_dir / "vendor",
        output_dir / "atlas.js",
        output_dir / "style.css",
    ):
        print(f"wrote {written}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hbf_atlas",
        description="HbF Evidence Atlas build tools.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a corpus directory")
    validate_parser.add_argument("directory", type=Path, help="corpus directory to validate")

    report_parser = subparsers.add_parser("build-report", help="export the local atlas report")
    report_parser.add_argument("corpus_dir", type=Path, help="corpus directory to report on")
    report_parser.add_argument("output_dir", type=Path, help="directory to write the report into")

    dashboard_parser = subparsers.add_parser("build-dashboard", help="export the interactive web dashboard")
    dashboard_parser.add_argument("corpus_dir", type=Path, help="corpus directory for the dashboard data")
    dashboard_parser.add_argument("output_dir", type=Path, help="directory to write the dashboard into")
    return parser


def cmd_build_dashboard(corpus_dir: Path, output_dir: Path) -> int:
    loaded = _load_and_validate(corpus_dir)
    if loaded is None:
        return 1
    corpus, issues = loaded
    _print_issues(issues)
    if _has_errors(issues):
        print("error: validation failed; dashboard not written", file=sys.stderr)
        return 1
    export_dashboard(corpus, output_dir)
    print(f"wrote {output_dir}/index.html, dashboard.js, style.css, atlas-data.json, vendor/")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args.directory)
    if args.command == "build-report":
        return cmd_build_report(args.corpus_dir, args.output_dir)
    return cmd_build_dashboard(args.corpus_dir, args.output_dir)


if __name__ == "__main__":
    sys.exit(main())

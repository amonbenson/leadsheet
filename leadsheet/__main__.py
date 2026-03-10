"""Command-line interface for the leadsheet package.

Usage:
    python -m leadsheet <input.tex> [output] [--format pdf|png ...] [--engine ENGINE] [-v]
"""

import argparse
import sys
from pathlib import Path

from leadsheet.compiler import CompilationError, compile_latex


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m leadsheet",
        description="Compile LaTeX leadsheet documents to PDF and/or PNG using latexmk.",
    )
    parser.add_argument("input", type=Path, help="Input .tex file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output path (extension is replaced per format; default: same stem as input)",
    )
    parser.add_argument(
        "--format",
        dest="formats",
        nargs="+",
        choices=["pdf", "png"],
        default=["pdf"],
        metavar="FORMAT",
        help="Output format(s): pdf, png (default: pdf). Can be repeated: --format pdf png",
    )
    parser.add_argument(
        "--engine",
        choices=["lualatex", "xelatex", "pdflatex"],
        default="lualatex",
        help="LaTeX engine to use (default: lualatex)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Forward latexmk output to stdout/stderr",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        outputs = compile_latex(args.input, args.output, formats=args.formats, engine=args.engine, verbose=args.verbose)
        for fmt, path in outputs.items():
            print(f"Successfully compiled [{fmt}]: {path}")
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except CompilationError as exc:
        print(f"Compilation error: {exc}", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

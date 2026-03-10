"""LaTeX compilation engine for leadsheet documents."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from leadsheet.converter import pdf_to_png

SUPPORTED_FORMATS = ("pdf", "png")


class CompilationError(Exception):
    """Raised when LaTeX compilation fails."""

    def __init__(self, message: str, stdout: str = "", stderr: str = "") -> None:
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr


def _find_latex_dir() -> Path:
    """Return the directory containing the leadsheet LaTeX class files."""
    latex_dir = Path(__file__).parent / "latex"
    if not (latex_dir / "leadsheet.cls").exists():
        raise FileNotFoundError(f"Could not find leadsheet LaTeX class files in {latex_dir}")
    return latex_dir


def compile_latex(
    input_file: Path | str,
    output_file: Path | str | None = None,
    *,
    formats: str | list[str] = "pdf",
    engine: str = "lualatex",
    verbose: bool = False,
) -> dict[str, Path]:
    """Compile a LaTeX file and produce PDF and/or PNG output.

    Args:
        input_file: Path to the input .tex file.
        output_file: Base output path. The file extension is ignored — it is
            replaced by the appropriate extension for each requested format.
            Defaults to the input file path with the suffix swapped.
        formats: One or more output formats: ``"pdf"``, ``"png"``, or a list
            containing both. Default: ``"pdf"``.
        engine: LaTeX engine to use (``'lualatex'``, ``'xelatex'``,
            ``'pdflatex'``). Default: ``'lualatex'``.
        verbose: If True, forward latexmk output to stdout/stderr.

    Returns:
        A dict mapping each requested format name to its output ``Path``.
        E.g. ``{"pdf": Path("song.pdf")}`` or
        ``{"pdf": Path("song.pdf"), "png": Path("song.png")}``.

    Raises:
        ValueError: If an unsupported format is requested.
        FileNotFoundError: If the input file or LaTeX class files cannot be found.
        CompilationError: If latexmk exits with a non-zero return code.
    """
    requested = _normalise_formats(formats)
    input_path = Path(input_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    base = Path(output_file).resolve().with_suffix("") if output_file is not None else input_path.with_suffix("")
    latex_dir = _find_latex_dir()
    outputs: dict[str, Path] = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        env = _build_env(latex_dir)
        cmd = _build_cmd(engine, input_path)

        result = subprocess.run(
            cmd,
            capture_output=not verbose,
            text=True,
            env=env,
            cwd=tmpdir,
            check=False,
        )

        if result.returncode != 0:
            stdout = result.stdout if not verbose else ""
            stderr = result.stderr if not verbose else ""
            raise CompilationError(
                f"LaTeX compilation failed (exit code {result.returncode})",
                stdout=stdout,
                stderr=stderr,
            )

        tmp_pdf = Path(tmpdir) / input_path.with_suffix(".pdf").name
        if not tmp_pdf.exists():
            raise CompilationError(f"Expected PDF was not produced at {tmp_pdf}")

        if "pdf" in requested:
            pdf_out = base.with_suffix(".pdf")
            pdf_out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tmp_pdf, pdf_out)
            outputs["pdf"] = pdf_out

        if "png" in requested:
            png_out = base.with_suffix(".png")
            pdf_to_png(tmp_pdf, png_out)
            outputs["png"] = png_out

    return outputs


def _normalise_formats(formats: str | list[str]) -> list[str]:
    """Validate and normalise the formats argument to a deduplicated list."""
    items = [formats] if isinstance(formats, str) else list(formats)
    unknown = [f for f in items if f not in SUPPORTED_FORMATS]
    if unknown:
        raise ValueError(f"Unsupported format(s): {unknown}. Choose from: {SUPPORTED_FORMATS}")
    return list(dict.fromkeys(items))  # deduplicate, preserve order


def _build_env(latex_dir: Path) -> dict[str, str]:
    """Build the environment dict with TEXINPUTS pointing to the leadsheet latex dir."""
    env = os.environ.copy()
    sep = ";" if os.name == "nt" else ":"
    existing = env.get("TEXINPUTS", "")
    env["TEXINPUTS"] = f"{latex_dir}{sep}{existing}" if existing else f"{latex_dir}{sep}"
    return env


def _build_cmd(engine: str, input_path: Path) -> list[str]:
    """Build the latexmk command list.

    latexmk is run with cwd=tmpdir so all auxiliary and output files land in
    the temp directory. The input path is passed as an absolute path.
    """
    return [
        "latexmk",
        f"-{engine}",
        "-interaction=nonstopmode",
        str(input_path),
    ]

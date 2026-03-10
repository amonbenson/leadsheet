"""Shared test fixtures and utilities for the leadsheet test suite."""

import subprocess
import sys
from pathlib import Path

import pypdf
import pytest

REPO_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract and concatenate all text from every page of a PDF."""
    reader = pypdf.PdfReader(str(pdf_path))
    return "".join(page.extract_text() or "" for page in reader.pages)


def extract_pdf_pages(pdf_path: Path) -> list[str]:
    """Return a list of extracted text strings, one entry per page."""
    reader = pypdf.PdfReader(str(pdf_path))
    return [page.extract_text() or "" for page in reader.pages]


def pdf_page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF."""
    return len(pypdf.PdfReader(str(pdf_path)).pages)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run 'python -m leadsheet' with the given arguments and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "leadsheet", *args],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="session")
def maniac_pdf(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Compile examples/maniac.tex once per test session and return the PDF path."""
    out = tmp_path_factory.mktemp("output") / "maniac.pdf"
    result = run_cli(str(EXAMPLES_DIR / "maniac.tex"), str(out))
    assert result.returncode == 0, f"Compilation failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert out.exists()
    return out

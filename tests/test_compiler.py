"""Integration tests for the leadsheet LaTeX compiler."""

import shutil
from pathlib import Path

import pytest

from leadsheet.compiler import CompilationError, compile_latex
from leadsheet.converter import pdf_to_png
from tests.conftest import EXAMPLES_DIR, extract_pdf_pages, extract_pdf_text, pdf_page_count, run_cli


class TestPDFOutput:
    """Verify that the compiled PDF has the expected content."""

    def test_pdf_exists_and_nonempty(self, maniac_pdf: Path) -> None:
        assert maniac_pdf.exists()
        assert maniac_pdf.stat().st_size > 0

    def test_pdf_contains_title(self, maniac_pdf: Path) -> None:
        assert "Maniac" in extract_pdf_text(maniac_pdf)

    def test_pdf_contains_section_heading(self, maniac_pdf: Path) -> None:
        assert "Verse 1" in extract_pdf_text(maniac_pdf)

    def test_pdf_contains_lyrics(self, maniac_pdf: Path) -> None:
        assert "steel town girl" in extract_pdf_text(maniac_pdf)

    def test_pdf_contains_more_lyrics(self, maniac_pdf: Path) -> None:
        assert "danger zone" in extract_pdf_text(maniac_pdf)


class TestCompilerAPI:
    """Test the compile_latex Python API directly."""

    def test_returns_dict(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out.pdf")
        assert isinstance(result, dict)
        assert set(result.keys()) == {"pdf"}

    def test_default_format_is_pdf(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out.pdf")
        assert "pdf" in result
        assert "png" not in result

    def test_default_output_path(self, tmp_path: Path) -> None:
        input_copy = tmp_path / "maniac.tex"
        shutil.copy(EXAMPLES_DIR / "maniac.tex", input_copy)
        result = compile_latex(input_copy)
        assert result["pdf"] == input_copy.with_suffix(".pdf")
        assert result["pdf"].exists()

    def test_explicit_output_path(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "custom.pdf")
        assert result["pdf"] == tmp_path / "custom.pdf"
        assert result["pdf"].exists()

    def test_output_directory_created_if_missing(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "nested" / "deep" / "out.pdf")
        assert result["pdf"].exists()

    def test_missing_input_raises_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            compile_latex(tmp_path / "nonexistent.tex")

    def test_invalid_latex_raises_compilation_error(self, tmp_path: Path) -> None:
        bad_tex = tmp_path / "bad.tex"
        bad_tex.write_text(r"\documentclass{leadsheet}" "\n" r"\begin{document}" "\n" r"\InvalidCommand" "\n" r"\end{document}")
        with pytest.raises(CompilationError):
            compile_latex(bad_tex, tmp_path / "bad.pdf")

    def test_compilation_error_captures_output(self, tmp_path: Path) -> None:
        bad_tex = tmp_path / "bad.tex"
        bad_tex.write_text(r"\documentclass{leadsheet}" "\n" r"\begin{document}" "\n" r"\InvalidCommand" "\n" r"\end{document}")
        with pytest.raises(CompilationError) as exc_info:
            compile_latex(bad_tex, tmp_path / "bad.pdf")
        err = exc_info.value
        assert isinstance(err.stdout, str)
        assert isinstance(err.stderr, str)

    def test_unsupported_format_raises_value_error(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Unsupported format"):
            compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out", formats="svg")


class TestPNGFormat:
    """Test PNG output via compile_latex and pdf_to_png."""

    def test_png_format_produces_png(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out", formats="png")
        assert set(result.keys()) == {"png"}
        assert result["png"].exists()
        assert result["png"].suffix == ".png"

    def test_png_file_is_valid_image(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out", formats="png")
        # PNG magic bytes: \x89PNG
        assert result["png"].read_bytes()[:4] == b"\x89PNG"

    def test_png_format_does_not_produce_pdf(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out", formats="png")
        assert "pdf" not in result
        assert not (tmp_path / "out.pdf").exists()

    def test_both_formats_produces_pdf_and_png(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out", formats=["pdf", "png"])
        assert set(result.keys()) == {"pdf", "png"}
        assert result["pdf"].exists()
        assert result["png"].exists()

    def test_both_formats_share_stem(self, tmp_path: Path) -> None:
        result = compile_latex(EXAMPLES_DIR / "maniac.tex", tmp_path / "out", formats=["pdf", "png"])
        assert result["pdf"].stem == result["png"].stem

    def test_pdf_to_png_standalone(self, maniac_pdf: Path, tmp_path: Path) -> None:
        png_out = tmp_path / "out.png"
        returned = pdf_to_png(maniac_pdf, png_out)
        assert returned == png_out
        assert png_out.exists()
        assert png_out.read_bytes()[:4] == b"\x89PNG"

    def test_pdf_to_png_missing_pdf_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            pdf_to_png(tmp_path / "nonexistent.pdf", tmp_path / "out.png")


_SINGLE_PAGE_TEX = r"""
\documentclass{leadsheet}
\title{Short Song}
\begin{document}
\maketitle
Just one line of content.
\end{document}
"""

# Repeat enough sections to guarantee a page break on A4
_MULTI_PAGE_TEX = (
    r"""
\documentclass{leadsheet}
\title{Long Song}
\begin{document}
\maketitle
"""
    + (
        r"""
\begin{songsection}{Section}
Just on the street of chance \\
Just on the street of chance \\
Just on the street of chance \\
Just on the street of chance \\
\end{songsection}
"""
        * 20
    )
    + r"\end{document}"
)


class TestPageNumbers:
    """Verify that page numbers appear only on multi-page documents."""

    @pytest.fixture(scope="class")
    def single_page_pdf(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        d = tmp_path_factory.mktemp("single")
        tex = d / "single.tex"
        tex.write_text(_SINGLE_PAGE_TEX)
        result = compile_latex(tex, d / "single.pdf")
        return result["pdf"]

    @pytest.fixture(scope="class")
    def multi_page_pdf(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        d = tmp_path_factory.mktemp("multi")
        tex = d / "multi.tex"
        tex.write_text(_MULTI_PAGE_TEX)
        result = compile_latex(tex, d / "multi.pdf")
        return result["pdf"]

    def test_single_page_document_has_one_page(self, single_page_pdf: Path) -> None:
        assert pdf_page_count(single_page_pdf) == 1

    def test_multi_page_document_has_multiple_pages(self, multi_page_pdf: Path) -> None:
        assert pdf_page_count(multi_page_pdf) > 1

    def test_single_page_has_no_page_number(self, single_page_pdf: Path) -> None:
        pages = extract_pdf_pages(single_page_pdf)
        # The only page should contain no isolated digit that could be a page number
        lines = [line.strip() for line in pages[0].splitlines()]
        assert "1" not in lines

    def test_multi_page_has_page_numbers(self, multi_page_pdf: Path) -> None:
        pages = extract_pdf_pages(multi_page_pdf)
        for i, page_text in enumerate(pages, start=1):
            lines = [line.strip() for line in page_text.splitlines()]
            assert str(i) in lines, f"Expected page number {i} on page {i}"


class TestCLI:
    """Test the command-line interface via subprocess."""

    def test_cli_compiles_to_explicit_output(self, tmp_path: Path) -> None:
        result = run_cli(str(EXAMPLES_DIR / "maniac.tex"), str(tmp_path / "out.pdf"))
        assert result.returncode == 0
        assert (tmp_path / "out.pdf").exists()

    def test_cli_prints_success_message(self, tmp_path: Path) -> None:
        result = run_cli(str(EXAMPLES_DIR / "maniac.tex"), str(tmp_path / "out.pdf"))
        assert "Successfully compiled [pdf]" in result.stdout

    def test_cli_missing_file_exits_with_error(self) -> None:
        result = run_cli("nonexistent.tex")
        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_cli_default_output_path(self, tmp_path: Path) -> None:
        input_copy = tmp_path / "maniac.tex"
        shutil.copy(EXAMPLES_DIR / "maniac.tex", input_copy)
        result = run_cli(str(input_copy))
        assert result.returncode == 0
        assert (tmp_path / "maniac.pdf").exists()

    def test_cli_engine_flag(self, tmp_path: Path) -> None:
        result = run_cli(str(EXAMPLES_DIR / "maniac.tex"), str(tmp_path / "out.pdf"), "--engine", "lualatex")
        assert result.returncode == 0
        assert (tmp_path / "out.pdf").exists()

    def test_cli_png_format(self, tmp_path: Path) -> None:
        result = run_cli(str(EXAMPLES_DIR / "maniac.tex"), str(tmp_path / "out"), "--format", "png")
        assert result.returncode == 0
        assert (tmp_path / "out.png").exists()
        assert "Successfully compiled [png]" in result.stdout

    def test_cli_both_formats(self, tmp_path: Path) -> None:
        result = run_cli(str(EXAMPLES_DIR / "maniac.tex"), str(tmp_path / "out"), "--format", "pdf", "png")
        assert result.returncode == 0
        assert (tmp_path / "out.pdf").exists()
        assert (tmp_path / "out.png").exists()
        assert "Successfully compiled [pdf]" in result.stdout
        assert "Successfully compiled [png]" in result.stdout

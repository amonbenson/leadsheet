"""PDF-to-PNG conversion using pymupdf."""

from pathlib import Path


def pdf_to_png(pdf_path: Path | str, png_path: Path | str, *, dpi: int = 150) -> Path:
    """Convert the first page of a PDF to a PNG image.

    Args:
        pdf_path: Path to the source PDF file.
        png_path: Path for the output PNG file.
        dpi: Resolution in dots per inch (default: 150).

    Returns:
        Path to the generated PNG file.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
    """
    import fitz  # pymupdf

    pdf_path = Path(pdf_path)
    png_path = Path(png_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    png_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    try:
        page = doc[0]
        page.get_pixmap(dpi=dpi).save(str(png_path))
    finally:
        doc.close()

    return png_path

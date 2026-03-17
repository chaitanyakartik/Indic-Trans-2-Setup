import fitz  # pymupdf


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF, joining pages with double newlines."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = [page.get_text() for page in doc]
    return "\n\n".join(pages).strip()

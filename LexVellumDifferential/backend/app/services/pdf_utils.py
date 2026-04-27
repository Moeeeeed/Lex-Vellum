import fitz  # PyMuPDF
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts all text from a PDF file given its raw bytes.
    Returns the full text as a single string with paragraphs separated by double newlines.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            full_text.append(text.strip())

    doc.close()
    return "\n\n".join(full_text)

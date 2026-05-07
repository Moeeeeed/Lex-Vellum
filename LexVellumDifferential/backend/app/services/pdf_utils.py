import fitz  
import io
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import os
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            full_text.append(text.strip())
    doc.close()
    return "\n\n".join(full_text)
def render_template_to_pdf(template_name: str, context: dict) -> bytes:
    template = env.get_template(template_name)
    html_out = template.render(context)
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.BytesIO(html_out.encode("UTF-8")), dest=pdf_buffer)
    if pisa_status.err:
        raise Exception(f"Error generating PDF from template {template_name}: {pisa_status.err}")
    return pdf_buffer.getvalue()

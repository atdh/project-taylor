from docxtpl import DocxTemplate
from pathlib import Path

def render_docx(data: dict, template_path: Path, output_path: Path) -> Path:
    """
    Renders a tailored resume into a .docx file using the provided template and data.
    """
    doc = DocxTemplate(template_path)
    doc.render(data)
    doc.save(output_path)
    return output_path

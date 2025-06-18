from pathlib import Path
from src.generator.renderer import render_docx

def test_render_docx_creates_file(tmp_path):
    data = {
        "summary": "Test summary",
        "skills": ["Python", "Docker"],
        "experiences": [
            {
                "title": "Engineer",
                "company": "TestCorp",
                "duration": "2022–2023",
                "bullets": ["Did cool things.", "Launched features."]
            }
        ],
        "extra_context": "Open to backend roles."
    }

    template_path = Path("src/templates/base_resume_template.docx")
    output_path = tmp_path / "resume.docx"
    rendered = render_docx(data, template_path, output_path)

    assert rendered.exists()

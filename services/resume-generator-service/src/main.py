from dotenv import load_dotenv
from generator.tailoring import tailor_resume
from generator.renderer import render_docx
from pathlib import Path

def main():
    print("🚀 Starting resume generation...")

    # Dummy input data
    profile = {"name": "Atul", "skills": ["Python", "React", "Docker"]}
    job_description = "Looking for a backend engineer with experience in Python, FastAPI, and Supabase."
    diary = "Took a year to work on personal startups and automate resume tailoring."

    # Tailor the resume
    tailored_data = tailor_resume(profile, job_description, diary)
    print("✅ Resume tailored.")

    # Render the resume
    template_path = Path("src/templates/base_resume_template.docx")
    output_path = Path("generated_resume.docx")
    render_docx(tailored_data, template_path, output_path)
    print(f"📄 Resume saved to {output_path.resolve()}")

if __name__ == "__main__":
    load_dotenv()
    main()

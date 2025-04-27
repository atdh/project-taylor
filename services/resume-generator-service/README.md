# Resume Generator Service

This service is responsible for automatically tailoring resumes based on job descriptions using LLM technology.

## Features
- Customizes resumes based on job requirements
- Uses LLM for intelligent content adaptation
- Formats output documents using templates
- Supports multiple output formats (DOCX, PDF)

## Setup
1. Copy `.env.example` to `.env` and fill in required values
2. Install dependencies: `pip install -r requirements.txt`
3. Run the service: `python src/main.py`

## Testing
Run tests with: `pytest tests/`

## Docker
Build: `docker build -t resume-generator-service .`
Run: `docker run -p 8001:8001 resume-generator-service`

## Template Customization
Place custom DOCX templates in the `src/generator/template.docx` file. The template should include placeholders that will be replaced with generated content.

# Resume Generator Service

AI-powered resume generation service that creates tailored resumes for specific job opportunities using multiple professional themes.

## Features

- **Multiple Themes** - Professional resume themes (elegant, modern, etc.)
- **Job-Tailored** - AI customizes resumes for specific job requirements
- **Multiple Formats** - HTML, PDF, and JSON output
- **Flexible Architecture** - Modular engine system for different generators
- **Fast Generation** - Quick resume creation and formatting

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js and npm (for JSON Resume CLI)

### 1. Install Dependencies

**Python Dependencies:**
```bash
cd services/resume-generator-service
pip install -r requirements.txt
```

**JSON Resume CLI:**
```bash
npm install -g resume-cli
npm install -g jsonresume-theme-elegant jsonresume-theme-modern
```

### 2. Run the Service
```bash
python run.py
# Service starts on http://localhost:8003
```

## API Endpoints

### Health Check
```
GET /health
```

### Generate Resume
```
POST /generate
```
Generate a tailored resume for a specific job opportunity.

**Request Body:**
```json
{
  "engine": "jsonresume",
  "theme": "elegant", 
  "format": "pdf",
  "job_description": "Software Engineer position...",
  "data": {
    // JSON Resume format data
  }
}
```

### Available Themes
```
GET /themes
```
Get list of available resume themes.

### Sample Data
```
GET /sample-data
```
Get sample resume data in JSON Resume format.

## Available Themes

- **elegant** - Clean, professional design
- **modern** - Contemporary styling
- **classic** - Traditional format
- **minimal** - Simple, clean layout

## Resume Engines

### JSON Resume Engine (Current)
- Uses the [JSON Resume](https://jsonresume.org/) ecosystem
- Multiple professional themes available
- HTML and PDF output support
- Industry-standard format

### Future Engines (Planned)
- **Reactive Resume** - Modern, customizable templates
- **LaTeX Engine** - Academic and technical resumes
- **Custom Templates** - Branded company templates

## Data Format

The service uses the [JSON Resume schema](https://jsonresume.org/schema/) as its standard format:

```json
{
  "basics": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "(555) 123-4567",
    "summary": "Experienced software engineer..."
  },
  "work": [...],
  "education": [...],
  "skills": [...],
  "projects": [...]
}
```

## AI Customization

The service can tailor resumes by:
- **Keyword Optimization** - Matches job description keywords
- **Skill Highlighting** - Emphasizes relevant skills
- **Experience Prioritization** - Reorders experience by relevance
- **Summary Customization** - Writes targeted professional summaries

## Troubleshooting

**Service won't start?**
- Verify Python 3.10+ is installed
- Check that Node.js and npm are available
- Ensure JSON Resume CLI is installed globally

**Resume generation failing?**
- Verify JSON Resume CLI is working: `resume --version`
- Check that themes are installed
- Review logs for specific error messages

**PDF generation issues?**
- Ensure system has PDF generation capabilities
- Try HTML format first to isolate issues
- Check theme compatibility

## Contributing

This service needs help with:
- **New Themes** - Additional professional resume themes
- **AI Enhancement** - Better job-specific customization
- **Mobile Optimization** - Mobile-friendly resume formats
- **New Engines** - Integration with other resume builders
- **Testing** - More comprehensive test coverage

### Adding New Engines

1. Create adapter in `src/engine_registry.py`
2. Implement the `ResumeEngineAdapter` interface
3. Add format conversion in `src/data_converter.py`
4. Register the engine in `EngineRegistry`

## Directory Structure

```
resume-generator-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── engine_registry.py   # Engine management
│   └── data_converter.py    # Format conversions
├── data/                    # Sample resume data
├── output/                  # Generated resumes
├── engines/                 # Engine-specific files
└── run.py                   # Service launcher
```

## License

MIT License - see [LICENSE](../../LICENSE) for details.

# Resume Generator Service

A flexible resume generation service that supports multiple resume generation engines while maintaining a consistent API interface.

## Architecture

This service follows a modular architecture that allows integration with different resume generation tools:

1. **JSON Resume Engine**
   - Uses the JSON Resume ecosystem
   - Access to multiple professional themes
   - HTML and PDF output

2. **Reactive Resume Engine** (Planned)
   - Modern, customizable templates
   - Docker-based integration
   - PDF and JSON export

3. **Future Engines**
   - LaTeX-based generators
   - Other resume builders
   - Custom template engines

See [architecture.md](architecture.md) for detailed design documentation.

## Setup

1. **Install Python Dependencies**
```bash
pip install fastapi uvicorn pydantic
```

2. **Install JSON Resume CLI** (for JSON Resume engine)
```bash
npm install -g resume-cli
npm install -g jsonresume-theme-elegant jsonresume-theme-modern
```

3. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### 1. Start the Service
```bash
uvicorn src.main:app --reload --port 8003
```

### 2. API Endpoints

#### Generate Resume
```bash
POST /api/generate
{
    "engine": "jsonresume",
    "theme": "elegant",
    "format": "pdf",
    "data": {
        # JSON Resume format data
    }
}
```

#### List Available Engines
```bash
GET /api/engines
```

#### Get Sample Data
```bash
GET /api/sample-data
```

## Resume Data

The service uses the [JSON Resume schema](https://jsonresume.org/schema/) as its base format. Your resume data is stored in:

- `resume_atul_dhungel.json` - Your personal resume data

## Adding New Engines

1. Create a new adapter in `src/engine_registry.py`
2. Implement the `ResumeEngineAdapter` interface
3. Add format conversion in `src/data_converter.py`
4. Register the engine in `EngineRegistry`

## Testing

```bash
pytest tests/
```

## Future Enhancements

- [ ] Add Reactive Resume integration
- [ ] Support LaTeX templates
- [ ] Add template customization
- [ ] Implement caching
- [ ] Add batch generation
- [ ] Support more output formats

## Directory Structure

```
resume-generator-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── engine_registry.py   # Engine management
│   └── data_converter.py    # Format conversions
├── data/
│   └── resume_atul_dhungel.json
├── engines/                 # Engine-specific files
│   └── jsonresume/
├── tests/
├── README.md
└── architecture.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

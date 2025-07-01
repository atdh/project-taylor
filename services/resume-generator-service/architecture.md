# Resume Generator Service Architecture

## Overview
A unified service that can generate resumes using multiple third-party engines while maintaining a consistent API interface.

## Supported Engines

### 1. JSON Resume (Node.js)
- **Technology**: Node.js + npm themes
- **Themes**: elegant, modern, professional, etc.
- **Formats**: HTML, PDF
- **Data Format**: JSON Resume schema

### 2. Reactive Resume (Python/Docker)
- **Technology**: React frontend + API
- **Themes**: Modern, customizable templates
- **Formats**: PDF, JSON export
- **Data Format**: Custom schema (can convert from JSON Resume)

### 3. LaTeX Resume (Python)
- **Technology**: Python + LaTeX
- **Themes**: Academic, professional LaTeX templates
- **Formats**: PDF
- **Data Format**: JSON Resume schema

## Architecture Pattern

```
┌─────────────────────────────────────────┐
│           Resume Generator API          │
│              (FastAPI/Python)           │
├─────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────────────┐ │
│  │   Engine    │ │    Data Converter   │ │
│  │  Registry   │ │   (JSON Resume →    │ │
│  │             │ │   Engine Format)    │ │
│  └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────┤
│           Engine Adapters               │
│  ┌─────────────┐ ┌─────────────────────┐ │
│  │ JSON Resume │ │ Reactive Resume     │ │
│  │  Adapter    │ │     Adapter         │ │
│  │ (Node.js)   │ │   (Docker API)      │ │
│  └─────────────┘ └─────────────────────┘ │
│  ┌─────────────┐ ┌─────────────────────┐ │
│  │   LaTeX     │ │    Future Engine    │ │
│  │  Adapter    │ │     Adapter         │ │
│  │ (Python)    │ │       (TBD)         │ │
│  └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────┘
```

## API Design

### Generate Resume Endpoint
```python
POST /api/generate
{
  "engine": "jsonresume",  # or "reactive", "latex"
  "theme": "elegant",
  "format": "pdf",         # or "html", "docx"
  "data": {
    # JSON Resume format data
  }
}
```

### List Available Options
```python
GET /api/engines
{
  "jsonresume": {
    "themes": ["elegant", "modern", "professional"],
    "formats": ["html", "pdf"]
  },
  "reactive": {
    "themes": ["minimal", "modern", "creative"],
    "formats": ["pdf", "json"]
  }
}
```

## Implementation Strategy

### Phase 1: Core Framework
1. FastAPI service with engine registry
2. JSON Resume adapter (Node.js subprocess)
3. Data validation and conversion utilities

### Phase 2: Additional Engines
1. Reactive Resume adapter (Docker API calls)
2. LaTeX adapter (Python-based)

### Phase 3: Advanced Features
1. Template customization
2. Batch generation
3. Version control for resume data
4. A/B testing for different formats

## Benefits

1. **Flexibility**: Can switch between engines based on needs
2. **Scalability**: Add new engines without changing core API
3. **Technology Agnostic**: Each engine uses its optimal technology
4. **Fallback**: If one engine fails, can try another
5. **Comparison**: Generate same resume with different engines
6. **Future-Proof**: Easy to add new resume generation tools

## File Structure
```
resume-generator-service/
├── src/
│   ├── main.py              # FastAPI app
│   ├── engine_registry.py   # Engine management
│   ├── data_converter.py    # Format conversions
│   └── adapters/
│       ├── jsonresume_adapter.py
│       ├── reactive_adapter.py
│       └── latex_adapter.py
├── engines/
│   ├── jsonresume/          # Node.js setup
│   ├── reactive/            # Docker setup
│   └── latex/               # Python templates
├── data/
│   └── resume_atul_dhungel.json
└── README.md

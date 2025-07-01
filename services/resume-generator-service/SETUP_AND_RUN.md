# Resume Generator Service Setup Guide

## Prerequisites

1. **Node.js and npm**
   - Required for JSON Resume CLI and themes
   - Download from: https://nodejs.org/
   - Verify installation:
     ```bash
     node --version
     npm --version
     ```

2. **Python 3.10+**
   - Required for the FastAPI service
   - Verify installation:
     ```bash
     python --version
     ```

## Setup Steps

1. **Create Python Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install JSON Resume Tools**
   ```bash
   # Install resume-cli globally
   npm install -g resume-cli

   # Install popular themes
   npm install -g jsonresume-theme-elegant
   npm install -g jsonresume-theme-modern
   npm install -g jsonresume-theme-stackoverflow
   ```

4. **Verify JSON Resume Installation**
   ```bash
   # Check resume-cli version
   resume --version

   # List installed themes
   npm list -g | grep jsonresume-theme
   ```

5. **Setup Output Directory**
   ```bash
   mkdir output
   ```

## Running the Service

1. **Start the FastAPI Server**
   ```bash
   uvicorn src.main:app --reload --port 8003
   ```

2. **Test the Service**
   ```bash
   # Run the test script
   python test_new_service.py
   ```

3. **Generate Sample Resume**
   ```bash
   # Using curl or any HTTP client
   curl -X POST "http://localhost:8003/api/generate" \
        -H "Content-Type: application/json" \
        -d '{"theme": "elegant", "format": "html"}'
   ```

## API Endpoints

- `GET /health` - Check service health
- `GET /api/engines` - List available engines and themes
- `POST /api/setup/{engine_name}` - Set up an engine
- `POST /api/generate` - Generate a resume
- `GET /api/download/{filename}` - Download generated file
- `GET /api/sample-data` - Get sample resume data
- `DELETE /api/cleanup` - Clean up generated files

## Troubleshooting

1. **JSON Resume CLI Not Found**
   - Ensure Node.js and npm are installed
   - Try reinstalling resume-cli:
     ```bash
     npm uninstall -g resume-cli
     npm install -g resume-cli
     ```

2. **Theme Not Found**
   - Install the theme manually:
     ```bash
     npm install -g jsonresume-theme-<theme-name>
     ```

3. **PDF Generation Issues**
   - Install Chrome/Chromium for PDF generation
   - Or use HTML format initially

## Development

1. **Adding New Themes**
   ```bash
   npm install -g jsonresume-theme-<theme-name>
   ```

2. **Testing Changes**
   ```bash
   # Run test script
   python test_new_service.py

   # Run specific engine test
   python -c "import asyncio; from src.engines import JSONResumeEngine; asyncio.run(JSONResumeEngine().setup())"
   ```

3. **Code Style**
   ```bash
   # Install development dependencies
   pip install black isort mypy

   # Format code
   black .
   isort .
   ```

## Next Steps

1. **Engine Integration**
   - [x] JSON Resume setup
   - [ ] PDF generation support
   - [ ] Additional themes

2. **Features**
   - [ ] Theme customization
   - [ ] Batch generation
   - [ ] Resume versioning

3. **Documentation**
   - [ ] API documentation
   - [ ] Theme gallery
   - [ ] Integration guide

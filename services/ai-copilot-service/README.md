# AI Copilot Service

AI-powered career analysis service that provides personalized career path suggestions and job search strategies using Google Gemini AI.

## Features

- **Career Analysis** - Analyzes LinkedIn profiles and personal stories
- **Path Suggestions** - AI-generated career path recommendations
- **Strategy Refinement** - Personalized job search strategies
- **Keyword Optimization** - Relevant keywords for each career path
- **Gemini AI Integration** - Powered by Google's advanced AI

## Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment activated
- Gemini API key configured

### 1. Setup Environment
```bash
cd services/ai-copilot-service
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Add to your `.env` file in project root:
```bash
GEMINI_API_KEY="your_gemini_api_key_here"
```

### 4. Run the Service
```bash
python run.py
# Service starts on http://localhost:8002
```

## API Endpoints

### Health Check
```
GET /health
```

### Career Analysis
```
POST /analyze-career
```
Analyze career profile and get AI-powered path suggestions.

**Request Body:**
```json
{
  "linkedin_url": "https://linkedin.com/in/yourprofile",
  "personal_story": "Your career background and goals...",
  "sample_resume": "Your current resume content..."
}
```

**Response:**
```json
{
  "career_paths": [
    {
      "title": "Technical Project Manager",
      "description": "Strong leadership and technical background",
      "keywords": ["Agile", "Team Leadership", "Scrum", "MERN Stack"],
      "match_score": 0.95
    }
  ],
  "analysis": "Based on your background..."
}
```

### Strategy Refinement
```
POST /refine-strategy
```
Refine job search strategy based on user preferences.

## How It Works

1. **Profile Analysis** - AI analyzes LinkedIn profile and personal story
2. **Pattern Recognition** - Identifies skills, experience, and career patterns
3. **Path Generation** - Creates personalized career path suggestions
4. **Keyword Extraction** - Generates relevant keywords for each path
5. **Strategy Creation** - Develops targeted job search strategies

## AI Capabilities

- **Natural Language Processing** - Understands career narratives
- **Skill Extraction** - Identifies technical and soft skills
- **Market Analysis** - Considers current job market trends
- **Personalization** - Tailors suggestions to individual profiles
- **Strategy Optimization** - Creates effective search strategies

## Troubleshooting

**Service won't start?**
- Check virtual environment is activated
- Verify Python 3.10+ is installed
- Ensure GEMINI_API_KEY is configured

**Career analysis failing?**
- Confirm Gemini API key is valid
- Check API quota and billing status
- Verify network connectivity
- Try with simpler input data

**No career suggestions?**
- Provide more detailed personal story
- Include relevant work experience
- Check that input fields are not empty

## Contributing

This service needs help with:
- **AI Prompt Engineering** - Better career analysis prompts
- **Market Data Integration** - Real-time job market insights
- **Personalization** - More targeted recommendations
- **Skill Mapping** - Better skill extraction and categorization
- **Testing** - Comprehensive test coverage

## Directory Structure

```
ai-copilot-service/
├── src/
│   ├── main.py           # FastAPI application
│   └── gemini_client.py  # Gemini AI integration
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── run.py               # Service launcher
```

## License

MIT License - see [LICENSE](../../LICENSE) for details.

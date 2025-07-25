# Frontend Dashboard

A clean, responsive web interface for Project Taylor's AI-powered job application system.

## Features

- **AI Career Analysis** - Analyze your profile and get personalized career path suggestions
- **Smart Job Search** - AI-powered job discovery with match scoring
- **Resume Generation** - Create tailored resumes for specific opportunities
- **Match Insights** - Detailed AI analysis of job compatibility

## Quick Start

### 1. Start Backend Services
Make sure these services are running (see main README):
- Job Scraper Service (Port 8001)
- AI Copilot Service (Port 8002)
- Resume Generator Service (Port 8003)

### 2. Open the Dashboard

**Option A - Direct File Access:**
```bash
# Open directly in your browser
open frontend/dashboard.html  # macOS
start frontend/dashboard.html # Windows
```

**Option B - Local Server (Recommended):**
```bash
cd frontend
python -m http.server 8080
# Visit http://localhost:8080/dashboard.html
```

## How to Use

1. **Career Analysis**
   - Enter LinkedIn profile URL (optional)
   - Add your personal story/biography (optional)
   - Click "Analyze My Career" to get AI suggestions

2. **Select Career Paths**
   - Choose from AI-suggested career paths
   - Multiple selections allowed

3. **Find Jobs**
   - Click "Find Relevant Jobs"
   - AI will search multiple job sources
   - View results with match scores and insights

4. **Generate Resume**
   - Click "Generate Tailored Resume" for specific jobs
   - AI customizes resume for job requirements

## API Endpoints Used

- `POST /analyze-career` - Career analysis (Port 8002)
- `POST /api/search-jobs-ai` - AI job search (Port 8001)
- `POST /generate` - Resume generation (Port 8003)

## Technology Stack

- **HTML5** - Semantic structure
- **JavaScript (ES6+)** - Modern async/await API calls
- **Tailwind CSS** - Responsive styling
- **Heroicons** - Clean iconography

## Troubleshooting

**Dashboard not working?**
- Ensure backend services are running
- Check browser console for errors
- Use local HTTP server instead of file:// protocol

**No job results?**
- Verify Job Scraper service is running (Port 8001)
- Check API keys are configured in backend
- Try different career path selections

**Career analysis failing?**
- Confirm AI Copilot service is running (Port 8002)
- Verify Gemini API key is configured
- Fields are optional - try with minimal input

## Contributing

The frontend needs help with:
- Mobile responsiveness improvements
- Accessibility enhancements
- UI/UX polish
- Better loading states
- Job results visualization

1. Fork the repository
2. Make your changes to `dashboard.html` and `dashboard.js`
3. Test across browsers
4. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) for details.

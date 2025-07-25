# Project Taylor: AI-Powered Job Application System

An intelligent microservices platform that automates the entire job application process using AI - from discovering opportunities to sending personalized applications.

## What's Working Right Now

**Core Features:**
- **AI-Powered Job Search**: Uses Gemini AI to create personalized search strategies
- **Smart Job Matching**: AI analyzes job descriptions and matches them to your profile
- **Resume Generation**: AI-tailored resumes for specific job opportunities
- **Web Dashboard**: Clean, responsive UI for managing your job search
- **Multi-Source Search**: Searches USAJobs, JSearch, Adzuna, and more
- **Fallback Systems**: Graceful handling when APIs are unavailable

**Live Demo Status:**
- **Job Scraper Service**: Running (Port 8001)
- **AI Copilot Service**: Running (Port 8002) 
- **Resume Generator**: Running (Port 8003)
- **Frontend Dashboard**: Working with real backend integration
- **Database**: Supabase integration working
- **AI Integration**: Gemini AI successfully planning job searches

## Architecture

### Core Services
1. **Job Scraper Service** - AI-driven job discovery across multiple platforms
2. **AI Copilot Service** - Career analysis and strategy recommendations
3. **Resume Generator Service** - AI-powered resume customization
4. **Filter Service** - Smart job filtering and ranking
5. **Email Delivery Service** - Automated application sending

### Technology Stack
- **Backend**: Python 3.10+, FastAPI, AsyncIO
- **Frontend**: HTML5, JavaScript, Tailwind CSS
- **AI**: Google Gemini API for intelligent planning
- **Database**: Supabase (PostgreSQL)
- **Infrastructure**: Docker, Docker Compose

## Quick Start

### Prerequisites
- Python 3.10+
- Git
- API Keys (see Environment Setup below)

### 1. Clone and Setup
```bash
git clone https://github.com/atdh/project-taylor.git
cd project-taylor
```

### 2. Environment Setup
Create a `.env` file in the root directory with your API keys:
```bash
GEMINI_API_KEY="your_gemini_api_key_here"
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_key"

# Optional job source APIs
USAJOBS_API_KEY="your_usajobs_key"
JSEARCH_API_KEY="your_jsearch_key"
ADZUNA_APP_ID="your_adzuna_app_id"
ADZUNA_APP_KEY="your_adzuna_app_key"
```

### 3. Start Services
Each service has its own virtual environment. Open 3 terminals:

**Terminal 1 - Job Scraper Service:**
```bash
cd services/job-scraper-service
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
python run.py
```

**Terminal 2 - AI Copilot Service:**
```bash
cd services/ai-copilot-service
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
python run.py
```

**Terminal 3 - Resume Generator Service:**
```bash
cd services/resume-generator-service
python run.py  # No venv needed for this service
```

### 4. Open the Dashboard
Open `frontend/dashboard.html` in your browser or serve it locally:
```bash
# Simple HTTP server
cd frontend
python -m http.server 8080
# Then visit http://localhost:8080/dashboard.html
```

## How to Use

1. **Open the Dashboard** - Load the frontend in your browser
2. **Select Career Paths** - Choose from AI-suggested career paths
3. **Find Jobs** - Click "Find Relevant Jobs" to start AI-powered search
4. **Generate Resume** - Create tailored resumes for specific opportunities
5. **Apply** - Send personalized applications (coming soon)

## API Endpoints

### Job Scraper Service (Port 8001)
- `GET /health` - Service health check
- `POST /api/search-jobs-ai` - AI-powered personalized job search
- `POST /api/search-jobs` - Standard job search
- `POST /webhook/new-job` - Receive job data from external sources

### AI Copilot Service (Port 8002)
- `GET /health` - Service health check
- `POST /analyze-career` - Analyze career profile and suggest paths
- `POST /refine-strategy` - Refine job search strategy

### Resume Generator Service (Port 8003)
- `GET /health` - Service health check
- `POST /generate` - Generate tailored resume
- `GET /themes` - Available resume themes

## Contributing

This project is ready for community contributions! Here's how you can help:

### Known Issues to Fix
1. **API Integration**: JSearch and Adzuna APIs need query format fixes
2. **Error Handling**: Improve error messages and recovery
3. **Performance**: Optimize AI processing speed
4. **UI/UX**: Enhance frontend responsiveness and accessibility

### Feature Ideas
1. **Email Integration**: Complete the email delivery service
2. **Job Tracking**: Track application status and responses
3. **Analytics**: Job market insights and trends
4. **Mobile App**: React Native or Flutter mobile app
5. **Browser Extension**: Chrome extension for one-click applications

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Documentation

- [Job Scraper Service](services/job-scraper-service/README.md) - AI-powered job discovery
- [AI Copilot Service](services/ai-copilot-service/) - Career analysis and strategy
- [Resume Generator Service](services/resume-generator-service/README.md) - AI resume customization
- [Frontend Dashboard](frontend/README.md) - Web interface documentation

## Roadmap

### Phase 1: Core Stability (Current)
- Basic AI job search working
- Frontend-backend integration
- API integration fixes
- Error handling improvements

### Phase 2: Enhanced Features
- Email delivery service completion
- Job tracking and analytics
- UI/UX improvements
- Mobile responsiveness

### Phase 3: Advanced AI
- Machine learning for job matching
- Market trend analysis
- Predictive job recommendations
- Automated application optimization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About the Creator

This project was built by **Atul Dhungel**, a software engineer passionate about AI and automation. 

**Currently seeking new opportunities** in:
- Software Engineering (Full-stack, Backend, AI/ML)
- Technical Project Management
- DevOps/Platform Engineering
- Remote or hybrid positions

**Skills demonstrated in this project:**
- Python (FastAPI, AsyncIO, AI integration)
- JavaScript (ES6+, Frontend development)
- AI/ML (Google Gemini API, prompt engineering)
- Microservices architecture
- Database design (Supabase/PostgreSQL)
- Docker containerization
- API design and integration

**Contact:**
- GitHub: [@atdh](https://github.com/atdh)
- LinkedIn: [Connect with Atul](https://linkedin.com/in/atul-dhungel)
- Email: Available in GitHub profile

*If you're interested in hiring or collaborating, feel free to reach out!*

## Acknowledgments

- Google Gemini AI for intelligent job search planning
- Supabase for database infrastructure
- The open-source community for inspiration and tools

---

**Ready to revolutionize job searching with AI? Join us!**

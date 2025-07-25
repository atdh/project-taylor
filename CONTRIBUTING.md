# Contributing to Project Taylor

Thank you for your interest in contributing to Project Taylor! This guide will help you get started.

## Quick Start for Contributors

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/project-taylor.git
cd project-taylor
```

### 2. Set Up Environment
```bash
# Add your API keys to .env file
GEMINI_API_KEY="your_gemini_api_key"
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_key"
```

### 3. Start Services
```bash
# Terminal 1 - Job Scraper
cd services/job-scraper-service
.\venv\Scripts\activate && python run.py

# Terminal 2 - AI Copilot  
cd services/ai-copilot-service
.\venv\Scripts\activate && python run.py

# Terminal 3 - Resume Generator
cd services/resume-generator-service
python run.py
```

### 4. Test Your Changes
Open `frontend/dashboard.html` in your browser and test the functionality.

## Priority Areas for Contribution

### Critical Fixes Needed
1. **API Integration Issues**
   - Fix JSearch API 400 errors (`services/job-scraper-service/src/job_clients.py`)
   - Fix Adzuna API query format issues
   - Improve error handling and recovery

2. **Performance Optimization**
   - Reduce AI processing time in job search
   - Optimize database queries
   - Implement caching for repeated searches

### Feature Enhancements
1. **Frontend Improvements**
   - Mobile responsiveness (`frontend/dashboard.html`)
   - Better loading states and user feedback
   - Job results visualization and filtering

2. **AI Enhancements**
   - Better job matching algorithms
   - Improved resume customization
   - Market trend analysis

3. **New Integrations**
   - Additional job board APIs
   - Email delivery service completion
   - Social media job discovery

## Project Structure

```
project-taylor/
├── frontend/              # Web dashboard
├── services/
│   ├── job-scraper-service/    # AI job discovery
│   ├── ai-copilot-service/     # Career analysis
│   ├── resume-generator-service/ # Resume creation
│   ├── filter-service/         # Job filtering
│   └── email-delivery-service/ # Email automation
├── supabase/             # Database migrations
└── docs/                 # Documentation
```

## Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Use modern ES6+ syntax
- **HTML/CSS**: Use Tailwind CSS classes

### Testing
- Add tests for new features
- Ensure existing tests pass
- Test across different browsers (frontend)

### Documentation
- Update README files for affected services
- Add inline code comments for complex logic
- Update API documentation for new endpoints

## Bug Reports

When reporting bugs, please include:
- Steps to reproduce
- Expected vs actual behavior
- Browser/OS information (for frontend issues)
- Service logs (for backend issues)

## Feature Requests

For new features, please:
- Check existing issues first
- Describe the use case and benefit
- Consider implementation complexity
- Discuss with maintainers before large changes

## Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests if applicable
   - Update documentation

3. **Test Thoroughly**
   - Test your changes locally
   - Ensure all services still work
   - Check frontend functionality

4. **Submit PR**
   - Clear description of changes
   - Reference related issues
   - Include screenshots for UI changes

## Getting Help

- **Discord**: [Join our community](https://discord.gg/project-taylor) (coming soon)
- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: Use GitHub discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Ready to contribute? Pick an issue and let's build the future of job searching together!**

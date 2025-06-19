# Frontend for Project Taylor

## Overview
This frontend provides a dashboard for users to input their LinkedIn profile URL, personal story, and a sample resume. It interacts with backend AI services to analyze career paths, generate tailored resumes, and find relevant jobs.

## How to Run Locally

1. Navigate to the `frontend` directory:
```bash
cd frontend
```

2. Start a simple HTTP server (requires Python 3):
```bash
python3 -m http.server 8000
```

3. Open your web browser and go to:
```
http://localhost:8000/dashboard.html
```

## Next Steps

- Connect the frontend to backend APIs for real AI analysis and job scraping.
- Implement enhancements as listed in `TODO.md`.

## Dependencies

- Tailwind CSS (included via CDN)
- Google Fonts (Inter font included via CDN)

## Notes

- This is a static frontend and requires backend services to be running and accessible for full functionality.
- For development, you can modify `dashboard.html` and refresh the browser to see changes.

import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_gpt_for_resume(profile: dict, job_description: str, diary: str = "") -> dict:
    prompt = build_prompt(profile, job_description, diary)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-4",  # or mistral, anthropic/claude-3-opus, etc.
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]

    return parse_gpt_response(content)

def build_prompt(profile: dict, job_description: str, diary: str) -> str:
    return f"""
You are a resume tailoring assistant. Given a candidate's profile, job description, and optional diary notes, return a JSON with the following keys:

- summary: a short personal summary
- skills: list of relevant skills
- experiences: list of relevant experiences, each with title, company, duration, bullets
- extra_context: any personal notes or transitions (e.g., career pivots)

### Profile:
{profile}

### Job Description:
{job_description}

### Diary:
{diary}

Return only valid JSON. Do not include explanations.
"""

def parse_gpt_response(response_str: str) -> dict:
    import json
    try:
        return json.loads(response_str)
    except json.JSONDecodeError:
        # Optionally add logging or fallback
        raise ValueError("Failed to parse GPT output as JSON")

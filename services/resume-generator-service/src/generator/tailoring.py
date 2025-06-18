from typing import Optional, Dict

def tailor_resume(profile: Dict, job_description: str, diary: Optional[str] = None) -> Dict:
    """
    Tailors a resume based on a user's profile, a job description, and optional diary context.

    Returns structured content ready for template rendering.
    """
    # TODO: Replace with OpenRouter GPT logic
    # return {
    #     "summary": "Experienced software engineer with a strong background in Python and backend systems...",
    #     "skills": ["Python", "FastAPI", "Supabase", "Docker"],
    #     "experiences": [
    #         {
    #             "title": "Software Engineer",
    #             "company": "Tata Consultancy Services",
    #             "duration": "2021–2023",
    #             "bullets": [
    #                 "Developed microservices using Java and Angular for banking and insurance clients.",
    #                 "Collaborated in an Agile team; handled production issues and feature rollouts."
    #             ]
    #         },
    #         {
    #             "title": "Technical Project Manager",
    #             "company": "World Leaves",
    #             "duration": "2024–Present",
    #             "bullets": [
    #                 "Led a team of 3 to build a financial automation tool with Playwright and Selenium.",
    #                 "Managed feature development using Trello and ensured test automation coverage."
    #             ]
    #         }
    #     ],
    #     "extra_context": "After co-founding startups, I’m seeking a return to hands-on technical roles with product impact."
    # }
    return call_gpt_for_resume(profile,job_description,diary or "")
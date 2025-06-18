from src.generator.tailoring import tailor_resume

def test_tailor_resume_mock_output():
    profile = {"name": "Atul", "skills": ["Python", "React", "Docker"]}
    job_description = "Looking for a backend engineer with experience in Python, FastAPI, and Supabase."
    diary = "Took a year to work on personal startups and automate resume tailoring."

    result = tailor_resume(profile, job_description, diary)

    assert "summary" in result
    assert "skills" in result
    assert isinstance(result["experiences"], list)
    assert "extra_context" in result

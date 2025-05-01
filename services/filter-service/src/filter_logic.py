# services/filter-service/src/filter_logic.py

import logging
import os
from typing import Dict, Any, List, Optional
import re # Import regular expressions for more advanced matching

# Import shared logger setup
# This import relies on common_utils being findable via editable install (for runtime)
# or conftest.py (for pytest)
from common_utils.logging import get_logger

# Initialize logger for this module
logger = get_logger("filter-service.filter_logic")

# --- Helper Functions ---

def _validate_job_details(job_details: Dict[str, Any]) -> bool:
    """
    Validate that job_details contains minimum required fields for filtering.
    """
    required_fields = ['id', 'title', 'description', 'company']
    if not all(field in job_details and job_details[field] is not None for field in required_fields):
        logger.warning(f"Job details missing required fields for filtering: {job_details.get('id')}")
        return False
    return True

def _validate_criteria(criteria: Dict[str, Any]) -> bool:
    """
    Validate that the criteria dictionary contains expected fields.
    """
    required_fields = ['required_skills', 'experience_level']
    if not all(field in criteria for field in required_fields):
         logger.error(f"Filtering criteria dictionary is missing required fields: {required_fields}")
         return False
    return True

def _normalize_text(text: Optional[str]) -> str:
    """
    Normalize text for consistent matching by converting to lowercase
    and removing extra whitespace. Handles None input.
    """
    if text is None:
        return ""
    return ' '.join(text.lower().split())

def _matches_skills(job_details: Dict[str, Any], required_skills: List[str]) -> bool:
    """
    Check if job mentions ALL required skills (using regex for whole words).
    Handles different input types for skills from parametrize.
    (Corrected logic to ensure ALL skills must match)
    """
    search_text = _normalize_text(f"{job_details.get('title', '')} {job_details.get('description', '')}")

    # Standardize skills input to a list of strings
    if isinstance(required_skills, str):
        # Handle case where skills might be space-separated in a single string from parametrize
        skills_list = [s for s in required_skills.split(' ') if s]
    elif isinstance(required_skills, (list, tuple)):
        skills_list = [str(s) for s in required_skills if isinstance(s, str) and s] # Ensure list of non-empty strings
    else:
        skills_list = [] # Default to empty list if input is unexpected

    if not skills_list:
        logger.debug(f"Job ID {job_details.get('id')} passes skill check (no skills required).")
        return True # If no skills are required, it's a match

    logger.debug(f"Job ID {job_details.get('id')} checking skills: {skills_list}")

    # --- Corrected Logic ---
    # Check if *every* required skill is found
    all_skills_found = True # Assume true initially
    for skill in skills_list:
        skill_pattern = _normalize_text(skill)
        if not skill_pattern: continue

        pattern = rf'\b{re.escape(skill_pattern)}(?:[\s\d\.+-]*)?\b'
        try:
            if not re.search(pattern, search_text):
                logger.debug(f"Job ID {job_details.get('id')} missing required skill: {skill}")
                all_skills_found = False # Mark as false if any skill is missing
                break # No need to check further skills if one is missing
        except re.error as e:
            logger.warning(f"Regex error for skill '{skill}' with pattern '{pattern}': {e}")
            all_skills_found = False # Treat regex error as non-match
            break

    # Log the outcome accurately
    if all_skills_found:
         logger.debug(f"Job ID {job_details.get('id')} matches all required skills.")
    # else: # No need for else log here, already logged missing skill inside loop
    #      logger.debug(f"Job ID {job_details.get('id')} does NOT match all required skills.")

    return all_skills_found # Return the final result (True only if loop completed without finding a missing skill)


def _matches_experience(job_details: Dict[str, Any], required_level: str) -> bool:
    """
    Check if job description mentions keywords indicating an acceptable experience level.
    Uses lenient matching: higher level positions can match lower level requirements.
    (Reflects Blackbox fixes for matching logic)
    """
    level_keywords = {
        'junior': ['junior', 'entry', 'entry-level', 'entry level', 'graduate', 'intern', 'associate'],
        'mid': ['mid', 'intermediate', 'mid-level', 'mid level', 'software engineer ii', 'software engineer 2'],
        'senior': ['senior', 'lead', 'principal', 'staff', 'architect', 'expert', 'sr.', 'manager']
    }
    required_level_norm = required_level.lower()
    if required_level_norm not in level_keywords:
        logger.warning(f"Invalid required experience level: {required_level}. Skipping level check.")
        return True

    search_text = _normalize_text(f"{job_details.get('title', '')} {job_details.get('description', '')}")
    has_junior = any(re.search(rf'\b{re.escape(keyword)}\b', search_text) for keyword in level_keywords['junior'])
    has_mid = any(re.search(rf'\b{re.escape(keyword)}\b', search_text) for keyword in level_keywords['mid'])
    has_senior = any(re.search(rf'\b{re.escape(keyword)}\b', search_text) for keyword in level_keywords['senior'])

    job_level_detected = None
    if has_senior: job_level_detected = 'senior'
    elif has_mid: job_level_detected = 'mid'
    elif has_junior: job_level_detected = 'junior'
    else:
        logger.debug(f"Job ID {job_details.get('id')} has no specific level mentioned, considered relevant.")
        return True # Assume relevant if no level mentioned

    # Check if the detected job level can fulfill the requirement (Lenient: higher can fill lower)
    if required_level_norm == 'junior':
        match = True # Any detected level can fill junior
    elif required_level_norm == 'mid':
        match = job_level_detected in ['mid', 'senior'] # Mid or Senior can fill Mid
    elif required_level_norm == 'senior':
        match = job_level_detected == 'senior' # Only Senior can fill Senior
    else:
        match = False # Should not happen

    if match:
        logger.debug(f"Job ID {job_details.get('id')} level '{job_level_detected}' matches required level '{required_level_norm}'")
    else:
        logger.debug(f"Job ID {job_details.get('id')} level '{job_level_detected}' does NOT match required level '{required_level_norm}'")

    return match


def _matches_company_preferences(job_details: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
    """ Check company preferences """
    company = _normalize_text(job_details.get('company', ''))
    if not company: return True

    excluded_companies = [_normalize_text(c) for c in criteria.get('exclude_companies', []) if c]
    if any(exc_company in company for exc_company in excluded_companies):
        logger.info(f"Job ID {job_details.get('id')} excluded based on company: {company}")
        return False

    preferred_companies = [_normalize_text(c) for c in criteria.get('preferred_companies', []) if c]
    if preferred_companies and not any(pref_company in company for pref_company in preferred_companies):
        logger.info(f"Job ID {job_details.get('id')} excluded, company not in preferred list: {company}")
        return False

    logger.debug(f"Job ID {job_details.get('id')} matches company preferences.")
    return True

# --- Main Filtering Function ---
DEFAULT_CRITERIA = {
    "required_skills": ["python", "api"],
    "experience_level": "mid",
    "exclude_companies": ["recruiting agency", "staffing firm"],
    "preferred_companies": []
}

def is_relevant(job_details: Dict[str, Any], criteria: Optional[Dict[str, Any]] = None) -> bool:
    """ Determine if a job is relevant based on criteria """
    current_criteria = {**DEFAULT_CRITERIA, **(criteria or {})}
    logger.debug(f"Applying filter criteria to job ID {job_details.get('id')}")

    if not _validate_job_details(job_details): return False
    # if not _validate_criteria(current_criteria): return False # Optional validation

    if not _matches_company_preferences(job_details, current_criteria): return False
    if not _matches_skills(job_details, current_criteria.get('required_skills', [])): return False
    if not _matches_experience(job_details, current_criteria.get('experience_level', 'junior')): return False

    logger.info(f"Job ID {job_details.get('id')} considered RELEVANT.")
    return True

# --- Main execution block (for testing this module directly if needed) ---
if __name__ == '__main__':
    # Example usage for direct testing
    TEST_CRITERIA = {
        "required_skills": ["python", "api", "sql"],
        "experience_level": "mid",
        "exclude_companies": ["bad company", "recruiting agency"],
        "preferred_companies": ["good company", "great tech inc"]
    }
    test_job_relevant = {"id": 1,"title": "Mid-Level Python API Developer","company": "Good Company","description": "Build amazing APIs using Python and SQL."}
    test_job_wrong_skill = {"id": 2,"title": "Mid-Level Java API Developer","company": "Good Company","description": "Build amazing APIs using Java and SQL."}
    test_job_wrong_level = {"id": 3,"title": "Senior Python API Developer","company": "Good Company","description": "Lead API development in Python and SQL."}
    test_job_excluded_company = {"id": 4,"title": "Python API Developer","company": "Bad Company","description": "Develop APIs with Python and SQL."}
    test_job_not_preferred = {"id": 5,"title": "Python API Developer","company": "Okay Company","description": "Develop APIs with Python and SQL."}

    print(f"Job 1 Relevant: {is_relevant(test_job_relevant, TEST_CRITERIA)}")
    print(f"Job 2 Relevant: {is_relevant(test_job_wrong_skill, TEST_CRITERIA)}")
    print(f"Job 3 Relevant: {is_relevant(test_job_wrong_level, TEST_CRITERIA)}")
    print(f"Job 4 Relevant: {is_relevant(test_job_excluded_company, TEST_CRITERIA)}")
    print(f"Job 5 Relevant: {is_relevant(test_job_not_preferred, TEST_CRITERIA)}")


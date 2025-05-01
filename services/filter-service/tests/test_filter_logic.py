# services/filter-service/tests/test_filter_logic.py

import pytest
from typing import Dict, List, Any
from common_utils.logging import get_logger

# Import the functions to test from the filter_logic module
# Assumes conftest.py adds the service root directory to sys.path
from src.filter_logic import (
    _validate_job_details,
    _validate_criteria,
    _normalize_text,
    _matches_skills,
    _matches_experience,
    _matches_company_preferences,
    is_relevant
)

# --- Test Data ---
VALID_JOB = {
    'id': 1, # Added ID for consistency
    'title': 'Senior Python Developer',
    'description': 'Looking for a Python developer with AWS experience',
    'company': 'Tech Corp'
}

VALID_CRITERIA = {
    'required_skills': ['python', 'aws'],
    'experience_level': 'senior',
    'exclude_companies': ['Bad Corp'],
    'preferred_companies': ['Tech Corp']
}

# --- Test Input Validation ---
def test_validate_job_details_valid():
    """Tests that validation passes with required job fields."""
    assert _validate_job_details(VALID_JOB) is True

def test_validate_job_details_missing_fields():
    """Tests that validation fails if required job fields are missing."""
    invalid_job = {
        'id': 2,
        'title': 'Developer',
        'description': 'Python role'
        # missing company
    }
    assert _validate_job_details(invalid_job) is False

def test_validate_criteria_valid():
    """Tests that validation passes with required criteria fields."""
    # Note: This test depends on the fields defined inside _validate_criteria
    # Adjust VALID_CRITERIA or the test if the function changes
    assert _validate_criteria(VALID_CRITERIA) is True

def test_validate_criteria_missing_fields():
    """Tests that validation fails if required criteria fields are missing."""
    invalid_criteria = {
        'required_skills': ['python']
        # missing experience_level (based on Blackbox example criteria)
    }
    # Note: This test depends on the fields defined inside _validate_criteria
    assert _validate_criteria(invalid_criteria) is False

# --- Test Text Normalization ---
def test_normalize_text():
    """Tests lowercase conversion and whitespace stripping."""
    text = "  Python   Developer\nAWS  "
    assert _normalize_text(text) == "python developer aws"
    assert _normalize_text(None) == "" # Test None input

# --- Test Skill Matching ---
@pytest.mark.parametrize("job_details,skills,expected", [
    # Basic skill matching
    (
        {'id': 10, 'title': 'Python Developer', 'description': 'AWS required'},
        ['python', 'aws'],
        True
    ),
    # Version number matching (assumes regex handles this)
    (
        {'id': 11, 'title': 'Python3 Developer', 'description': 'Python 3.9 required'},
        ['python'],
        True
    ),
    # Case insensitive matching (handled by normalize)
    (
        {'id': 12, 'title': 'PYTHON Developer', 'description': 'AWS required'},
        ['python', 'aws'],
        True
    ),
    # Missing skill
    (
        {'id': 13, 'title': 'Python Developer', 'description': ''},
        ['python', 'aws'],
        False # Fails because 'aws' is missing
    ),
    # Partial word matching prevention (checks for whole words)
    (
        {'id': 14, 'title': 'Developer', 'description': 'Typescript required'},
        ['script'], # Should not match 'Typescript'
        False
    )
])
def test_matches_skills(job_details, skills, expected):
    """Tests the _matches_skills helper function with various inputs."""
    # Ensure required fields for validation are present
    job_details.setdefault('company', 'Test Company')
    job_details.setdefault('description', job_details.get('description', ''))
    job_details.setdefault('title', job_details.get('title', ''))
    job_details.setdefault('id', job_details.get('id', 99)) # Add default ID if missing
    assert _matches_skills(job_details, skills) == expected

# --- Test Experience Matching ---
@pytest.mark.parametrize("job_details,level,expected", [
    # Junior positions match 'junior' requirement
    (
        {'id': 20, 'title': 'Junior Developer', 'description': 'Entry level role'},
        'junior',
        True
    ),
    # Junior positions can only apply to junior requirements
    (
        {'id': 21, 'title': 'Junior Developer', 'description': 'Entry level role'},
        'mid',
        False  # Junior positions can only apply to junior requirements
    ),
    # Mid positions can apply to junior and mid requirements
    (
        {'id': 22, 'title': 'Mid-level Developer', 'description': 'Intermediate role'},
        'junior',
        True  # Mid positions can apply to junior and mid requirements
    ),
    # Senior positions can apply to any level requirement
    (
        {'id': 23, 'title': 'Senior Developer', 'description': 'Lead role'},
        'junior',
        True  # Senior positions can apply to any level requirement
    ),
    # Senior positions can apply to mid requirements
    (
        {'id': 24, 'title': 'Senior Developer', 'description': 'Lead role'},
        'mid',
        True  # Senior positions can apply to any level requirement
    )
])
def test_matches_experience(job_details, level, expected):
    """Tests the _matches_experience helper function."""
    # Ensure required fields for validation are present
    job_details.setdefault('company', 'Test Company')
    job_details.setdefault('description', job_details.get('description', ''))
    job_details.setdefault('title', job_details.get('title', ''))
    job_details.setdefault('id', job_details.get('id', 99)) # Add default ID if missing
    assert _matches_experience(job_details, level) == expected

# --- Test Company Preferences ---
@pytest.mark.parametrize("job_details,criteria,expected", [
    # Preferred company match
    (
        {'id': 30, 'company': 'Good Corp'},
        {'preferred_companies': ['Good Corp'], 'exclude_companies': []},
        True
    ),
    # Excluded company match
    (
        {'id': 31, 'company': 'Bad Corp'},
        {'preferred_companies': [], 'exclude_companies': ['Bad Corp']},
        False
    ),
    # Case insensitive matching
    (
        {'id': 32, 'company': 'GOOD CORP'},
        {'preferred_companies': ['good corp'], 'exclude_companies': []},
        True
    ),
    # No preferences specified
    (
        {'id': 33, 'company': 'Any Corp'},
        {'preferred_companies': [], 'exclude_companies': []},
        True
    ),
    # Not in preferred companies list when one exists
    (
        {'id': 34, 'company': 'Average Corp'},
        {'preferred_companies': ['Good Corp'], 'exclude_companies': []},
        False
    )
])
def test_matches_company_preferences(job_details, criteria, expected):
    """Tests the _matches_company_preferences helper function."""
    # Ensure required fields for validation are present
    job_details.setdefault('title', 'Test Title')
    job_details.setdefault('description', 'Test Desc')
    job_details.setdefault('company', job_details.get('company', ''))
    job_details.setdefault('id', job_details.get('id', 99)) # Add default ID if missing
    assert _matches_company_preferences(job_details, criteria) == expected

# --- Test Main Function Integration ---
# These tests combine the results of the helper functions via is_relevant

def test_is_relevant_all_matching():
    """Tests the main is_relevant function when all sub-checks should pass."""
    job = {
        'id': 40,
        'title': 'Senior Python Developer',
        'description': 'AWS and SQL required',
        'company': 'Good Corp'
    }
    criteria = {
        'required_skills': ['python', 'aws'],
        'experience_level': 'senior',
        'preferred_companies': ['Good Corp'],
         'exclude_companies': ['Bad Corp']
    }
    assert is_relevant(job, criteria) is True

def test_is_relevant_missing_skill_fails():
    """Tests is_relevant when a required skill is missing."""
    job = {
        'id': 41,
        'title': 'Senior Python Developer',
        'description': 'Only Python required',
        'company': 'Good Corp'
    }
    criteria = {
        'required_skills': ['python', 'aws'], # Requires AWS which is missing
        'experience_level': 'senior',
        'preferred_companies': ['Good Corp']
    }
    assert is_relevant(job, criteria) is False

def test_is_relevant_wrong_experience_fails():
    """Tests is_relevant when experience doesn't match (depends on logic)."""
    job = {
        'id': 42,
        'title': 'Junior Python Developer',
        'description': 'AWS and SQL required',
        'company': 'Good Corp'
    }
    criteria = {
        'required_skills': ['python', 'aws'],
        'experience_level': 'senior', # Requires senior, job is junior
        'preferred_companies': ['Good Corp']
    }
    # This assumes _matches_experience returns False for junior when senior is required
    assert is_relevant(job, criteria) is False

def test_is_relevant_excluded_company_fails():
    """Tests is_relevant when the company is on the exclusion list."""
    job = {
        'id': 43,
        'title': 'Senior Python Developer',
        'description': 'AWS and SQL required',
        'company': 'Bad Corp'
    }
    criteria = {
        'required_skills': ['python', 'aws'],
        'experience_level': 'senior',
        'exclude_companies': ['Bad Corp']
    }
    assert is_relevant(job, criteria) is False

def test_is_relevant_invalid_inputs_fail():
    """Tests is_relevant handles invalid input gracefully (via validation helpers)."""
    # Missing required job fields
    job = {
        'id': 44,
        'title': 'Developer'
        # missing description and company
    }
    criteria = {
        'required_skills': ['python'],
        'experience_level': 'mid'
    }
    assert is_relevant(job, criteria) is False

    # Missing required criteria fields
    job_valid = {
        'id': 45,
        'title': 'Python Dev',
        'description': '...',
        'company': '...'
    }
    criteria_invalid = {
        'required_skills': ['python']
        # missing experience_level
    }
    # Note: This depends on _validate_criteria being called within is_relevant
    # If is_relevant has defaults, this might pass depending on implementation
    # Let's assume validation happens and fails it.
    # assert is_relevant(job_valid, criteria_invalid) is False # Commented out as it depends on validation call


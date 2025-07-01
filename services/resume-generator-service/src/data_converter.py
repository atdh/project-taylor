from typing import Dict, Any
import copy

def convert_to_engine_format(data: Dict[str, Any], engine: str) -> Dict[str, Any]:
    """Convert resume data to engine-specific format"""
    
    if engine == "jsonresume":
        return convert_to_jsonresume_format(data)
    elif engine == "reactive":
        return convert_to_reactive_format(data)
    else:
        # Default: return as-is
        return data

def convert_to_jsonresume_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert data to JSON Resume format (or validate if already in correct format)"""
    
    # If data is already in JSON Resume format, return as-is
    if is_jsonresume_format(data):
        return data
    
    # TODO: Add conversion logic for other formats if needed
    # For now, assume input is already JSON Resume format
    return data

def convert_to_reactive_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert JSON Resume format to Reactive Resume format"""
    
    # This is a placeholder for future Reactive Resume integration
    # Reactive Resume has its own schema which differs from JSON Resume
    
    reactive_data = {
        "basics": {
            "name": data.get("basics", {}).get("name", ""),
            "headline": data.get("basics", {}).get("label", ""),
            "email": data.get("basics", {}).get("email", ""),
            "phone": data.get("basics", {}).get("phone", ""),
            "website": data.get("basics", {}).get("url", ""),
            "summary": data.get("basics", {}).get("summary", ""),
            "location": format_location_for_reactive(data.get("basics", {}).get("location", {}))
        },
        "sections": {
            "work": convert_work_for_reactive(data.get("work", [])),
            "education": convert_education_for_reactive(data.get("education", [])),
            "skills": convert_skills_for_reactive(data.get("skills", [])),
            "projects": convert_projects_for_reactive(data.get("projects", []))
        }
    }
    
    return reactive_data

def is_jsonresume_format(data: Dict[str, Any]) -> bool:
    """Check if data follows JSON Resume schema"""
    
    # Basic validation - check for required JSON Resume structure
    required_fields = ["basics"]
    
    for field in required_fields:
        if field not in data:
            return False
    
    # Check basics structure
    basics = data.get("basics", {})
    if not isinstance(basics, dict):
        return False
    
    # If it has the basic structure, assume it's JSON Resume format
    return True

def format_location_for_reactive(location: Dict[str, Any]) -> str:
    """Format location object for Reactive Resume"""
    if not location:
        return ""
    
    parts = []
    if location.get("city"):
        parts.append(location["city"])
    if location.get("region"):
        parts.append(location["region"])
    if location.get("countryCode"):
        parts.append(location["countryCode"])
    
    return ", ".join(parts)

def convert_work_for_reactive(work_list: list) -> list:
    """Convert work experience for Reactive Resume format"""
    converted = []
    
    for job in work_list:
        converted_job = {
            "company": job.get("name", ""),
            "position": job.get("position", ""),
            "location": job.get("location", ""),
            "startDate": job.get("startDate", ""),
            "endDate": job.get("endDate", ""),
            "summary": job.get("summary", ""),
            "highlights": job.get("highlights", [])
        }
        converted.append(converted_job)
    
    return converted

def convert_education_for_reactive(education_list: list) -> list:
    """Convert education for Reactive Resume format"""
    converted = []
    
    for edu in education_list:
        converted_edu = {
            "institution": edu.get("institution", ""),
            "degree": edu.get("studyType", ""),
            "area": edu.get("area", ""),
            "startDate": edu.get("startDate", ""),
            "endDate": edu.get("endDate", ""),
            "gpa": edu.get("score", ""),
            "courses": edu.get("courses", [])
        }
        converted.append(converted_edu)
    
    return converted

def convert_skills_for_reactive(skills_list: list) -> list:
    """Convert skills for Reactive Resume format"""
    converted = []
    
    for skill_group in skills_list:
        converted_skill = {
            "name": skill_group.get("name", ""),
            "keywords": skill_group.get("keywords", []),
            "level": skill_group.get("level", "")
        }
        converted.append(converted_skill)
    
    return converted

def convert_projects_for_reactive(projects_list: list) -> list:
    """Convert projects for Reactive Resume format"""
    converted = []
    
    for project in projects_list:
        converted_project = {
            "name": project.get("name", ""),
            "description": project.get("description", ""),
            "url": project.get("url", ""),
            "startDate": project.get("startDate", ""),
            "endDate": project.get("endDate", ""),
            "highlights": project.get("highlights", [])
        }
        converted.append(converted_project)
    
    return converted

def validate_jsonresume_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data against JSON Resume schema and return validation results"""
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required fields
    if "basics" not in data:
        validation_result["valid"] = False
        validation_result["errors"].append("Missing required field: basics")
    
    # Check basics structure
    basics = data.get("basics", {})
    if basics:
        required_basics = ["name"]
        for field in required_basics:
            if field not in basics:
                validation_result["warnings"].append(f"Missing recommended field: basics.{field}")
    
    # Check optional sections
    optional_sections = ["work", "education", "skills", "projects", "volunteer", "awards", "publications"]
    for section in optional_sections:
        if section in data and not isinstance(data[section], list):
            validation_result["errors"].append(f"Field '{section}' should be an array")
            validation_result["valid"] = False
    
    return validation_result

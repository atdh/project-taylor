import re
import json
from datetime import datetime, date
from typing import Any, Dict, Optional, Union
import logging
from decimal import Decimal

def parse_salary(salary_text: str) -> Optional[Dict[str, Union[float, str]]]:
    """
    Parse salary information from text
    Args:
        salary_text: String containing salary information
    Returns:
        Dictionary with min, max, and currency if found
    """
    try:
        # Remove commas and normalize format
        clean_text = salary_text.replace(",", "").lower()
        
        # Extract numbers and currency
        numbers = re.findall(r'\d+\.?\d*', clean_text)
        if not numbers:
            return None
            
        # Determine currency
        currency = "USD"  # Default
        currency_map = {
            "£": "GBP",
            "€": "EUR",
            "¥": "JPY",
            "c$": "CAD",
            "a$": "AUD"
        }
        for symbol, code in currency_map.items():
            if symbol in salary_text:
                currency = code
                break
                
        # Convert to annual if needed
        multiplier = 1
        if "per hour" in clean_text or "/hr" in clean_text:
            multiplier = 2080  # 40 hours * 52 weeks
        elif "per month" in clean_text:
            multiplier = 12
            
        # Parse range or single value
        numbers = [float(n) * multiplier for n in numbers]
        if len(numbers) >= 2:
            return {
                "min": min(numbers[:2]),
                "max": max(numbers[:2]),
                "currency": currency
            }
        else:
            base = numbers[0]
            return {
                "min": base * 0.9,  # Estimated range
                "max": base * 1.1,
                "currency": currency
            }
            
    except Exception as e:
        logging.debug(f"Error parsing salary: {e}")
        return None

def parse_date(date_text: str) -> Optional[str]:
    """
    Parse date from various text formats to ISO format
    Args:
        date_text: String containing date information
    Returns:
        ISO formatted date string if parseable
    """
    try:
        # Common date formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%B %d, %Y",
            "%b %d, %Y"
        ]
        
        # Try exact formats
        for fmt in formats:
            try:
                return datetime.strptime(date_text, fmt).date().isoformat()
            except ValueError:
                continue
                
        # Handle relative dates
        clean_text = date_text.lower().strip()
        if "today" in clean_text:
            return date.today().isoformat()
        elif "yesterday" in clean_text:
            return (date.today() - timedelta(days=1)).isoformat()
            
        # Handle "X days/months ago"
        match = re.search(r'(\d+)\s*(day|month|week)s?\s*ago', clean_text)
        if match:
            number = int(match.group(1))
            unit = match.group(2)
            if unit == "day":
                delta = timedelta(days=number)
            elif unit == "week":
                delta = timedelta(weeks=number)
            elif unit == "month":
                delta = timedelta(days=number * 30)  # Approximate
            return (date.today() - delta).isoformat()
            
    except Exception as e:
        logging.debug(f"Error parsing date: {e}")
        
    return None

def standardize_location(location: str) -> Dict[str, str]:
    """
    Standardize location information
    Args:
        location: Location string
    Returns:
        Dictionary with standardized location components
    """
    try:
        # Remove extra whitespace and normalize
        clean_location = " ".join(location.strip().split())
        
        # Check for remote indicators
        if re.search(r'\b(remote|virtual|work from home|wfh)\b', clean_location.lower()):
            return {
                "type": "remote",
                "country": None,
                "state": None,
                "city": None
            }
            
        # Try to parse components
        components = clean_location.split(",")
        components = [c.strip() for c in components]
        
        result = {
            "type": "on-site",
            "country": None,
            "state": None,
            "city": None
        }
        
        if len(components) >= 3:
            result["city"] = components[0]
            result["state"] = components[1]
            result["country"] = components[2]
        elif len(components) == 2:
            result["city"] = components[0]
            result["state"] = components[1]
        else:
            result["city"] = components[0]
            
        return result
        
    except Exception as e:
        logging.debug(f"Error standardizing location: {e}")
        return {
            "type": "unknown",
            "country": None,
            "state": None,
            "city": None
        }

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling special types"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount with appropriate symbol
    Args:
        amount: Numeric amount
        currency: Currency code
    Returns:
        Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "AUD": "A$",
        "CAD": "C$"
    }
    
    symbol = currency_symbols.get(currency, "$")
    
    if currency == "JPY":
        return f"{symbol}{int(amount):,}"
    else:
        return f"{symbol}{amount:,.2f}"

def extract_skills(text: str) -> list[str]:
    """
    Extract technical skills from text
    Args:
        text: Input text to analyze
    Returns:
        List of identified skills
    """
    # Common technical skills (expand as needed)
    skill_patterns = [
        r'\b(python|java|javascript|typescript|react|angular|vue|node\.js)\b',
        r'\b(sql|mysql|postgresql|mongodb|redis)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|terraform)\b',
        r'\b(git|ci/cd|jenkins|github actions)\b',
        r'\b(rest|graphql|api|microservices)\b'
    ]
    
    skills = set()
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        skills.update(matches)
    
    return sorted(list(skills))

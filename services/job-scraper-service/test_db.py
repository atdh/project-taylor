from dotenv import load_dotenv
import os
from supabase import create_client
import logging
from requests.exceptions import ConnectionError, RequestException
import socket
import dns.resolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dns_resolution(hostname):
    """Test DNS resolution for a given hostname"""
    try:
        logger.info(f"Attempting to resolve DNS for: {hostname}")
        answers = dns.resolver.resolve(hostname, 'A')
        for rdata in answers:
            logger.info(f"IP Address: {rdata}")
        return True
    except dns.resolver.NXDOMAIN:
        logger.error(f"DNS resolution failed: Domain {hostname} does not exist")
        return False
    except Exception as e:
        logger.error(f"DNS resolution failed: {str(e)}")
        return False

def test_supabase_connection():
    # Load environment variables
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Missing required environment variables")
        logger.info(f"SUPABASE_URL present: {bool(supabase_url)}")
        logger.info(f"SUPABASE_KEY present: {bool(supabase_key)}")
        return False
    
    # Extract hostname from URL
    hostname = supabase_url.replace("https://", "").replace("http://", "").split("/")[0]
    
    # Test DNS resolution first
    if not test_dns_resolution(hostname):
        return False
    
    logger.info(f"Testing connection to Supabase URL: {supabase_url}")
    
    try:
        # Create the Supabase client instance
        supabase = create_client(supabase_url, supabase_key)
        
        # Try to fetch something from the database
        response = supabase.table('jobs').select("*").limit(1).execute()
        
        logger.info("Successfully connected to Supabase!")
        logger.info(f"Response data: {response.data}")
        return True
        
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return False
    except RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    test_supabase_connection()

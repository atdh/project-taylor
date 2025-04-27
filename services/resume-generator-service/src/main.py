import json
import sys
import asyncio
import os
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from common_utils.logging import get_logger
from llm.openrouter_client import llm_client
from formatters.pandoc_client import pandoc

# Load environment variables
load_dotenv()

# Configure logging
logger = get_logger("resume-generator")

class ResumeGeneratorMCP:
    """MCP-compliant resume generation service"""
    
    async def process_request(self, request: Dict) -> Dict:
        """
        Process an MCP request to generate a tailored resume
        Args:
            request: Dictionary containing:
                - job_description: Target job details
                - base_resume: Original resume content
                - output_format: Desired output format (docx, pdf)
                - custom_instructions: Optional additional instructions
        Returns:
            Dictionary containing:
                - resume_content: Generated resume in requested format (base64)
                - analysis: Job match analysis
                - metadata: Processing information
        """
        try:
            # Validate request
            self._validate_request(request)
            
            # Generate tailored resume content using LLM
            markdown_content = await llm_client.generate_resume(
                job_description=request["job_description"],
                base_resume=request["base_resume"],
                custom_instructions=request.get("custom_instructions")
            )
            
            # Analyze job match
            analysis = await llm_client.analyze_job_match(
                job_description=request["job_description"],
                resume=markdown_content
            )
            
            # Convert to requested format
            output_format = request.get("output_format", "docx")
            if output_format == "docx":
                formatted_content = await pandoc.markdown_to_docx(
                    markdown_content,
                    template_name=request.get("template_name"),
                    metadata=self._build_metadata(request)
                )
            elif output_format == "pdf":
                formatted_content = await pandoc.markdown_to_pdf(
                    markdown_content,
                    template_name=request.get("template_name"),
                    metadata=self._build_metadata(request)
                )
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            # Encode content for response
            import base64
            encoded_content = base64.b64encode(formatted_content).decode()
            
            # Return MCP-compliant response
            return {
                "resume_content": encoded_content,
                "content_type": f"application/{output_format}",
                "analysis": analysis,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "model_used": os.getenv("OPENROUTER_DEFAULT_MODEL"),
                    "template_used": request.get("template_name"),
                    "format": output_format
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "error": str(e),
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat()
                }
            }

    def _validate_request(self, request: Dict):
        """Validate incoming request"""
        required_fields = ["job_description", "base_resume"]
        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")
                
        valid_formats = ["docx", "pdf"]
        if "output_format" in request and request["output_format"] not in valid_formats:
            raise ValueError(
                f"Invalid output format. Must be one of: {', '.join(valid_formats)}"
            )

    def _build_metadata(self, request: Dict) -> Dict:
        """Build metadata for document template"""
        return {
            "title": request.get("position_title", "Resume"),
            "author": request.get("candidate_name", ""),
            "date": datetime.now().strftime("%B %d, %Y"),
            "company": request.get("company_name", ""),
            "position": request.get("position_title", ""),
            "contact": {
                "email": request.get("contact_email", ""),
                "phone": request.get("contact_phone", ""),
                "linkedin": request.get("linkedin_url", "")
            }
        }

async def main():
    """Main MCP entry point"""
    try:
        # Read request from stdin
        request = json.loads(sys.stdin.read())
        
        # Process request
        generator = ResumeGeneratorMCP()
        response = await generator.process_request(request)
        
        # Write response to stdout
        print(json.dumps(response, indent=2))
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON input")
        print(json.dumps({"error": "Invalid JSON input"}))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging
from dotenv import load_dotenv
import uvicorn
import os
from emailer import EmailSender

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Email Delivery Service")
email_sender = EmailSender()

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    company_name: str
    position_name: str
    recipient_name: Optional[str] = None
    custom_message: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "running", "service": "email-delivery"}

@app.post("/send")
async def send_email(
    email_request: EmailRequest,
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...)
):
    """
    Send an email with resume attachment
    """
    try:
        # Save resume temporarily
        temp_path = f"/tmp/{resume.filename}"
        with open(temp_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)

        # Queue email sending task
        background_tasks.add_task(
            email_sender.send_email,
            to_email=email_request.to_email,
            subject=email_request.subject,
            company_name=email_request.company_name,
            position_name=email_request.position_name,
            recipient_name=email_request.recipient_name,
            custom_message=email_request.custom_message,
            resume_path=temp_path
        )

        return JSONResponse(
            status_code=202,
            content={"message": "Email queued for delivery"}
        )

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{email_id}")
async def get_status(email_id: str):
    """
    Get the status of an email delivery
    """
    try:
        status = await email_sender.get_status(email_id)
        return {"email_id": email_id, "status": status}
    except Exception as e:
        logger.error(f"Error getting email status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

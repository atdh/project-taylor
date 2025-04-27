import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import logging
from typing import Optional
import aiofiles
from tenacity import retry, stop_after_attempt, wait_exponential
import jinja2
from datetime import datetime
import uuid
import redis
from email.utils import formataddr

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        """Initialize email sender with configuration"""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        self.from_name = os.getenv("FROM_NAME", "Automated Job Application")

        # Initialize Redis for status tracking
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True
        )

        # Initialize template engine
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates")
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def send_email(
        self,
        to_email: str,
        subject: str,
        company_name: str,
        position_name: str,
        recipient_name: Optional[str] = None,
        custom_message: Optional[str] = None,
        resume_path: Optional[str] = None
    ) -> str:
        """
        Send an email with optional resume attachment
        Returns: email_id for status tracking
        """
        try:
            email_id = str(uuid.uuid4())
            self._update_status(email_id, "preparing")

            # Create message
            msg = MIMEMultipart()
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = to_email
            msg["Subject"] = subject

            # Generate email body from template
            body_html = await self._generate_email_body(
                company_name,
                position_name,
                recipient_name,
                custom_message
            )
            msg.attach(MIMEText(body_html, "html"))

            # Attach resume if provided
            if resume_path and os.path.exists(resume_path):
                async with aiofiles.open(resume_path, "rb") as f:
                    resume_data = await f.read()
                    attachment = MIMEApplication(resume_data, _subtype="docx")
                    attachment.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename="resume.docx"
                    )
                    msg.attach(attachment)

            # Send email
            self._update_status(email_id, "sending")
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )

            self._update_status(email_id, "delivered")
            logger.info(f"Email sent successfully: {email_id}")
            return email_id

        except Exception as e:
            self._update_status(email_id, "failed", str(e))
            logger.error(f"Failed to send email: {e}")
            raise

        finally:
            # Cleanup temporary files
            if resume_path and os.path.exists(resume_path):
                os.remove(resume_path)

    async def _generate_email_body(
        self,
        company_name: str,
        position_name: str,
        recipient_name: Optional[str],
        custom_message: Optional[str]
    ) -> str:
        """Generate email body from template"""
        template = self.template_env.get_template("email_template.html")
        return template.render(
            company_name=company_name,
            position_name=position_name,
            recipient_name=recipient_name or "Hiring Manager",
            custom_message=custom_message,
            current_year=datetime.now().year
        )

    def _update_status(
        self,
        email_id: str,
        status: str,
        error: Optional[str] = None
    ):
        """Update email status in Redis"""
        self.redis_client.hset(
            f"email:{email_id}",
            mapping={
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "error": error or ""
            }
        )
        # Set expiration for cleanup (e.g., 24 hours)
        self.redis_client.expire(f"email:{email_id}", 86400)

    async def get_status(self, email_id: str) -> dict:
        """Get email delivery status"""
        status = self.redis_client.hgetall(f"email:{email_id}")
        if not status:
            raise ValueError(f"Email ID not found: {email_id}")
        return status

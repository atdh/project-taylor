# Email Delivery Service

This service is responsible for sending tailored resumes to job applications via email.

## Features
- Sends professionally formatted emails with resume attachments
- Supports customizable email templates
- Handles attachments and file types
- Provides delivery status tracking
- Implements retry mechanisms for failed deliveries

## Setup
1. Copy `.env.example` to `.env` and fill in required values
2. Install dependencies: `pip install -r requirements.txt`
3. Run the service: `python src/main.py`

## Testing
Run tests with: `pytest tests/`

## Docker
Build: `docker build -t email-delivery-service .`
Run: `docker run email-delivery-service`

## Email Templates
The service uses customizable email templates that can be modified in the `src/templates` directory. Variables in templates can be replaced with actual values when sending emails.

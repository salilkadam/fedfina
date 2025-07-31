"""
Email Service for sending conversation reports
"""
import os
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class EmailConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    use_tls: bool
    from_email: str
    from_name: str

class EmailService:
    def __init__(self):
        self.config = self._load_config()
        self.enabled = os.getenv("EMAIL_ENABLED", "true").lower() == "true"
    
    def _load_config(self) -> EmailConfig:
        """Load email configuration from environment variables"""
        return EmailConfig(
            host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            from_email=os.getenv("SMTP_FROM_EMAIL", ""),
            from_name=os.getenv("SMTP_FROM_NAME", "FedFina Reports")
        )
    
    def _validate_config(self) -> bool:
        """Validate that all required email configuration is present"""
        required_fields = [
            self.config.host,
            self.config.username,
            self.config.password,
            self.config.from_email
        ]
        return all(field for field in required_fields)
    
    async def send_conversation_report(self, 
                                     to_email: str,
                                     account_id: str,
                                     subject: str,
                                     html_body: str,
                                     text_body: str,
                                     pdf_filepath: Optional[str] = None) -> bool:
        """Send conversation report email with optional PDF attachment"""
        try:
            if not self.enabled:
                logger.info("Email sending is disabled")
                return True
            
            if not self._validate_config():
                logger.error("Email configuration is incomplete")
                return False
            
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Add PDF attachment if provided
            if pdf_filepath and os.path.exists(pdf_filepath):
                with open(pdf_filepath, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                filename = os.path.basename(pdf_filepath)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                message.attach(part)
                logger.info(f"PDF attachment added: {filename}")
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                use_tls=False,  # Use STARTTLS instead of TLS
                start_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    async def send_test_email(self, to_email: str) -> bool:
        """Send a test email to verify configuration"""
        try:
            if not self.enabled:
                logger.info("Email sending is disabled")
                return True
            
            if not self._validate_config():
                logger.error("Email configuration is incomplete")
                return False
            
            subject = "FedFina Email Service Test"
            text_body = """
            This is a test email from the FedFina conversation reporting system.
            
            If you receive this email, the email service is configured correctly.
            
            Best regards,
            FedFina Team
            """
            
            html_body = f"""
            <html>
            <body>
                <h2>FedFina Email Service Test</h2>
                <p>This is a test email from the FedFina conversation reporting system.</p>
                <p>If you receive this email, the email service is configured correctly.</p>
                <br>
                <p><strong>Best regards,</strong><br>
                FedFina Team</p>
            </body>
            </html>
            """
            
            return await self.send_conversation_report(
                to_email=to_email,
                account_id="TEST",
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
        except Exception as e:
            logger.error(f"Error sending test email: {str(e)}")
            return False
    
    def get_config_status(self) -> dict:
        """Get the current email configuration status"""
        return {
            "enabled": self.enabled,
            "configured": self._validate_config(),
            "host": self.config.host,
            "port": self.config.port,
            "username": self.config.username,
            "from_email": self.config.from_email,
            "use_tls": self.config.use_tls
        } 
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import os
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM_EMAIL")
        self.from_name = os.getenv("SMTP_FROM_NAME")
    
    async def send_email(self, to_email: str, subject: str, html_content: str):
        """Send email using SMTP"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        
        html_part = MIMEText(html_content, "html", "utf-8")  # Added utf-8 encoding
        message.attach(html_part)
        
        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            print(f"✅ Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    async def send_otp_email(self, to_email: str, otp: str, user_name: str):
        """Send OTP verification email"""
        with open("app/templates/otp_template.html", "r", encoding="utf-8") as f:  # Added encoding
            template_content = f.read()
        
        template = Template(template_content)
        html_content = template.render(otp=otp, user_name=user_name)
        
        subject = "Your OTP Code - Skynet"
        return await self.send_email(to_email, subject, html_content)
    
    async def send_welcome_email(self, to_email: str, user_name: str):
        """Send welcome email after successful registration"""
        with open("app/templates/welcome_template.html", "r", encoding="utf-8") as f:  # Added encoding
            template_content = f.read()
        
        template = Template(template_content)
        html_content = template.render(user_name=user_name)
        
        subject = "Welcome to Skynet! 🚀"
        return await self.send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Dependency to get email service"""
    return email_service

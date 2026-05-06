import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
    """
    Sends a real email using Gmail SMTP.
    Requires SMTP_EMAIL and SMTP_PASSWORD to be set in .env.
    """
    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        print(f"Warning: SMTP_EMAIL or SMTP_PASSWORD not set. Cannot send email to {to_email}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body of the message
        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        
        # Send the email
        server.send_message(msg)
        server.quit()
        
        print(f"Successfully sent email to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

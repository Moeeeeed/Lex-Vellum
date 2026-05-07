import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from app.core.config import settings
from typing import List, Optional, Tuple
def send_email(
    to_email: str, 
    subject: str, 
    body: str, 
    is_html: bool = False,
    attachments: Optional[List[Tuple[str, bytes]]] = None
):
    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        print(f"Warning: SMTP_EMAIL or SMTP_PASSWORD not set. Cannot send email to {to_email}")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type))
        if attachments:
            for filename, content in attachments:
                part = MIMEApplication(content)
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(part)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Successfully sent email to {to_email} with {len(attachments) if attachments else 0} attachments")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False

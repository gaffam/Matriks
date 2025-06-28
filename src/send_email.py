import smtplib
import os
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from config import load_config

CFG = load_config()


def send_email(to_addr: str, subject: str, body: str, attachment: Optional[str] = None) -> None:
    """Send an email with optional PDF attachment using SMTP settings from config."""
    email_cfg = CFG.get("email", {})
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_cfg.get("username")
    msg["To"] = to_addr
    msg.set_content(body)
    if attachment:
        data = Path(attachment).read_bytes()
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=Path(attachment).name)
    with smtplib.SMTP(email_cfg.get("smtp_host"), email_cfg.get("smtp_port", 587)) as server:
        server.starttls()
        pwd = os.environ.get("SMTP_PASSWORD") or email_cfg.get("password")
        server.login(email_cfg.get("username"), pwd)
        server.send_message(msg)

import smtplib
from email.message import EmailMessage

from pydantic import EmailStr

from core.config.settings import Settings


class EmailService:
    def __init__(self, settings: Settings):
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_username
        self._password = settings.smtp_password
        self._from_email = settings.smtp_from_email

    async def send_auth_code(self, email: EmailStr, code: str) -> None:
        msg = EmailMessage()
        msg["From"] = self._from_email
        msg["To"] = email
        msg["Subject"] = "Your HydroDrags Login Code"

        msg.set_content(
            f"""
Your HydroDrags login code is:

{code}

This code will expire in 10 minutes.

If you did not request this, you can safely ignore this email.
"""
        )

        # SMTP is blocking — acceptable for now
        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._username, self._password)
            server.send_message(msg)
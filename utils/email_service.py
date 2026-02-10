# core/services/email.py
import smtplib
from email.message import EmailMessage
from logging import info

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
        print(f"Sending email to {email}")

        # SMTP is blocking — acceptable for now
        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._username, self._password)
            server.send_message(msg)

    async def send_purchase_receipt(
            self,
            *,
            to_email: EmailStr,
            purchaser_name: str,
            paypal_order_id: str,
            amount: float,
            tickets: list[dict],
    ) -> None:
        msg = EmailMessage()
        msg["From"] = self._from_email
        msg["To"] = to_email
        msg["Subject"] = "Your HydroDrags Receipt & Tickets"

        ticket_lines = "\n".join(
            f"- {t['ticket_type'].replace('_', ' ').title()} — Code: {t['ticket_code']}"
            for t in tickets
        )

        msg.set_content(
            f"""
Hi {purchaser_name},

Thank you for your purchase!

PayPal Order ID:
{paypal_order_id}

Total Paid:
${amount:.2f}

Your Tickets:
{ticket_lines}

Please save this email or take a screenshot of your tickets.
Tickets may also be looked up at the gate using your phone number.

If you have any issues, just reply to this email.

— HydroDrags
"""
        )

        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._username, self._password)
            server.send_message(msg)
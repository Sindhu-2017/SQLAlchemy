import asyncio
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from app.core.config import get_settings
from app.models.income import Income


logger = logging.getLogger(__name__)

class EmailSender:
    async def send_income_confirmation(self,receiver: str,income: Income) -> bool:
        
        # Send the email without blocking the asynchronous API event loop
        return await asyncio.to_thread(
            self._send_income_confirmation_sync,
            receiver,
            income
        )

    def _send_income_confirmation_sync(self, receiver: str, income: Income) -> bool:
        settings = get_settings()
        sender = settings.EMAIL_SENDER
        password = settings.EMAIL_PASSWORD.get_secret_value()

        if not sender or not password:
            logger.error("Gmail SMTP credentials are not configured.")
            return False
        
        message = EmailMessage()

        message["Subject"] = "Income Management-Income Created Successfully"
        message["From"] = sender
        message["To"] = receiver
        message["Date"] = formatdate(localtime=True)
        message["Message-ID"] = make_msgid()
        email_body = f"""
        Hello,
        Your income record has been created successfully.

        Income Details
        --------------
        Income ID       : {income.income_id}
        Income Date     : {income.income_date}
        Source          : {income.source}
        Income Type     : {income.income_type}
        Amount          : {income.amount}
        Tax Percentage  : {income.tax_percentage}%
        Tax Amount      : {income.tax_amount}
        Net Income      : {income.net_income}
        Cash in Hand    : {income.cash_in_hand}

        Thank you for using Income Management.
        Regards,
        Income Management Team
        """

        message.set_content(email_body)
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=15) as smtp:
                # authentictes our gmail account 
                smtp.login(sender,password)
                smtp.send_message(message)

            logger.info("Income confirmation email sent for income_id=%s",income.income_id)
            return True

        except (smtplib.SMTPException, OSError):
            logger.exception("Failed to send income confirmation email for income_id=%s",income.income_id)
            return False

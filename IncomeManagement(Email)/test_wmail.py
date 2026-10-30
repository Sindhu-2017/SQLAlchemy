import smtplib
import ssl

from app.core.config import get_settings

settings = get_settings()

sender = settings.EMAIL_SENDER
password = settings.EMAIL_PASSWORD.get_secret_value()

print("Sender:", sender)
print("Password configured:", bool(password))
print("Password length:", len(password))
print("Password contains spaces:", " " in password)

try:
    with smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=30,
    ) as smtp:

        print("\nConnected to Gmail.")

        smtp.ehlo()

        print("EHLO response:", smtp.esmtp_features)

        smtp.starttls(context=ssl.create_default_context())

        print("\nTLS connection established.")

        smtp.ehlo()

        print("SMTP authentication methods:",
              smtp.esmtp_features.get("auth"))

        print("\nAttempting authentication...")

        smtp.login(sender, password)

        print("Gmail authentication successful!")

except Exception as error:
    print("\nError:", type(error).__name__)
    print("Details:", str(error))
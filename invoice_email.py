import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, client_name):

    sender_email = "vigneshbhimala@gmail.com"
    sender_password = "oydk agbk wejn qrdd"

    subject = "Employee Created Successfully"

    body = f"""
    Hello {client_name},

    Your invoice is genearted successfully.

    Welcome to the company 🚀
    """

    message = MIMEMultipart()

    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(sender_email, sender_password)

    server.send_message(message)

    server.quit()
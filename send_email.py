import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

# Read result.txt
with open("result.txt", "r") as f:
    body = f.read()

# Email details
sender = os.environ["GMAIL_USERNAME"]
receiver = "anthony.j.cutajar@gmail.com; danielle.e.horner@gmail.com"  # or another recipient
password = os.environ["GMAIL_PASSWORD"]  # or GMAIL_APP_PASSWORD

msg = MIMEText(body)
msg["Subject"] = "Maxwell Summary"
msg["From"] = sender
msg["To"] = receiver

# Send email
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())

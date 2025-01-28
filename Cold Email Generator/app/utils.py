import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def clean_text(text):
    """Function to clean text."""
    return text.strip()


def send_email(sender_email, recipient_email, subject, body, attachments=None):
    """
    Send email using SMTP with optional attachments.
    :param sender_email: Sender's email address.
    :param recipient_email: Recipient's email address.
    :param subject: Subject of the email.
    :param body: Body of the email.
    :param attachments: List of tuples [(filename, filedata)] to attach to the email.
    """
    # Gmail SMTP server configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = sender_email  # Your Gmail address
    smtp_password = " "  # Replace with your generated App Password

    try:
        # Create MIME Email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach files if provided
        if attachments:
            for filename, filedata in attachments:
                # Create a MIMEBase object
                part = MIMEBase("application", "octet-stream")
                part.set_payload(filedata)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={filename}")
                msg.attach(part)

        # Connect and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()  # Explicitly call EHLO
            server.starttls()  # Start TLS encryption
            server.login(smtp_user, smtp_password)  # Login with App Password
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")
        raise

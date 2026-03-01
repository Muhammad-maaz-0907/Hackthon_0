# Send Email via Gmail API
# Usage: python send_email.py

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Paths
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'Integrations', 'Gmail', 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'Integrations', 'Gmail', 'token.json')


def get_gmail_service():
    """Authenticate and build Gmail service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def send_email(to, subject, body, cc=None, bcc=None):
    """Send an email via Gmail API."""
    try:
        service = get_gmail_service()

        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        if cc:
            message['cc'] = cc
        if bcc:
            # BCC is not added to headers, just to recipients
            pass

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Send
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        print(f"✓ Email sent successfully!")
        print(f"  To: {to}")
        print(f"  Subject: {subject}")
        print(f"  Message ID: {sent_message['id']}")
        return sent_message

    except HttpError as error:
        print(f"✗ Error sending email: {error}")
        return None


def main():
    """Interactive email sender."""
    print("\n=== Gmail Email Sender ===\n")

    to = input("To (email address): ").strip()
    if not to:
        print("Error: Recipient email is required")
        return

    subject = input("Subject: ").strip()
    if not subject:
        print("Error: Subject is required")
        return

    print("\nEnter email body (type 'SEND' on a new line to send):")
    body_lines = []
    while True:
        line = input()
        if line.strip() == 'SEND':
            break
        body_lines.append(line)

    body = '\n'.join(body_lines)

    if not body.strip():
        print("Error: Email body is required")
        return

    send_email(to, subject, body)


if __name__ == '__main__':
    main()

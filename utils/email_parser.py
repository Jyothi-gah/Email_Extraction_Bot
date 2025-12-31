import imaplib
import email
import re
from email.header import decode_header
from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER

def fetch_latest_meeting_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        if not email_ids:
            return None

        latest_email_id = email_ids[-1]
        res, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        # Regex for links
        meet_pattern = r"(https://meet\.google\.com/[a-z-]+)"
        zoom_pattern = r"(https://[a-zA-Z0-9]+\.zoom\.us/[jw]/[a-zA-Z0-9?=&]+)"
        zoho_pattern = r"(https?://meet\.zoho\.[a-z]{2,3}/[a-zA-Z0-9/=?&_-]+)"

        link = None
        platform = None

        if re.search(meet_pattern, body):
            link = re.search(meet_pattern, body).group(0)
            platform = "google_meet"
        elif re.search(zoom_pattern, body):
            link = re.search(zoom_pattern, body).group(0)
            platform = "zoom"
        elif re.search(zoho_pattern, body):
            link = re.search(zoho_pattern, body).group(0)
            platform = "zoho"

        if link:
            return {
                "platform": platform,
                "link": link,
                "subject": subject,
                "from": msg.get("From"),
                "to": msg.get("To"),
                "cc": msg.get("Cc")
            }
        return None
    except Exception as e:
        print(f"Email Error: {e}")
        return None
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    """Test SMTP connection and credentials"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    try:
        print("Testing SMTP connection...")
        print(f"Using email: {smtp_username}")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)
        print("Server connected")
        
        server.starttls()
        print("TLS started")
        
        server.login(smtp_username, smtp_password)
        print("Login successful")
        
        server.quit()
        print("SMTP connection test successful!")
        return True
    except Exception as e:
        print(f"SMTP connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_smtp_connection() 
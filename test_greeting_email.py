"""
Test script to send a greeting email
From: idcp.administrator@gmail.com
To: manilkumar1909@gmail.com
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from email_notification_agent import EmailNotificationAgent

def send_greeting_email():
    """Send a test greeting email"""
    
    # Initialize email agent
    agent = EmailNotificationAgent()
    
    # Recipient
    recipient = "manilkumar1909@gmail.com"
    
    # Email subject
    subject = "Greeting from Workforce Orchestrator System"
    
    # Email body (HTML)
    body_html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 30px; 
                text-align: center; 
                border-radius: 10px 10px 0 0; 
            }
            .content { 
                background: #f9f9f9; 
                padding: 30px; 
                border-radius: 0 0 10px 10px; 
            }
            .greeting { 
                font-size: 24px; 
                font-weight: bold; 
                color: #667eea; 
                margin-bottom: 20px; 
            }
            .message { 
                background: white; 
                padding: 20px; 
                border-left: 4px solid #667eea; 
                margin: 20px 0; 
            }
            .footer { 
                text-align: center; 
                margin-top: 30px; 
                color: #666; 
                font-size: 12px; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Greetings from IDCP Workforce Orchestrator!</h1>
            </div>
            <div class="content">
                <div class="greeting">Hello Anil Kumar! 👋</div>
                
                <div class="message">
                    <p>This is a <strong>test greeting email</strong> from the Workforce Orchestrator system.</p>
                    
                    <p>We're excited to inform you that our email notification system is now <strong>fully operational</strong>!</p>
                    
                    <h3>✅ System Features:</h3>
                    <ul>
                        <li>📧 Automated email notifications at workflow stages</li>
                        <li>📄 Real email extraction from resumes</li>
                        <li>🔄 Dynamic candidate refresh from Resumes folder</li>
                        <li>📊 Complete workflow tracking</li>
                        <li>🎯 Professional HTML email templates</li>
                    </ul>
                    
                    <h3>📬 Your Email Address:</h3>
                    <p><strong>manilkumar1909@gmail.com</strong></p>
                    <p>This email was successfully extracted from your resume!</p>
                    
                    <h3>🚀 Next Steps:</h3>
                    <p>You will receive automated notifications when:</p>
                    <ul>
                        <li>Your onboarding is initiated</li>
                        <li>Background check is completed</li>
                        <li>Assets are allocated to you</li>
                        <li>Offboarding process begins</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                    <p>Sender: idcp.administrator@gmail.com</p>
                    <p>© 2026 Workforce Orchestrator System</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("=" * 60)
    print("SENDING TEST GREETING EMAIL")
    print("=" * 60)
    print(f"From: {agent.sender_email}")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print("=" * 60)
    
    # Send email
    result = agent.send_email(
        recipient_email=recipient,
        subject=subject,
        body_html=body_html
    )
    
    print("\nRESULT:")
    print("=" * 60)
    if result['success']:
        print("✅ SUCCESS! Email sent successfully!")
        print(f"Message: {result['message']}")
        print(f"Timestamp: {result['log']['timestamp']}")
        print("\n📧 Please check manilkumar1909@gmail.com inbox!")
        print("(Check spam folder if not in inbox)")
    else:
        print("❌ FAILED! Email could not be sent.")
        print(f"Error: {result['error']}")
        print("\nPossible reasons:")
        print("1. Gmail credentials are invalid or expired")
        print("2. Gmail account needs 2-factor authentication")
        print("3. App password needs to be regenerated")
        print("4. SMTP connection blocked by firewall")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    send_greeting_email()

# Made with Bob

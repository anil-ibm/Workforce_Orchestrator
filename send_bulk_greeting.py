"""
Send greeting emails to multiple IBM recipients
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from email_notification_agent import EmailNotificationAgent

def send_bulk_greetings():
    """Send greeting emails to multiple recipients"""
    
    # Initialize email agent
    agent = EmailNotificationAgent()
    
    # List of recipients
    recipients = [
        "jerrinjohn@in.ibm.com",
        "anitha.indrakanti@in.ibm.com",
        "smaudgal@in.ibm.com",
        "kumarm.anill@ibm.com",
        "sonykum1@in.ibm.com",
        "Sarah.Smruthi@ibm.com"
    ]
    
    # Email subject
    subject = "Greetings from Workforce Orchestrator System"
    
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
            .feature-list {
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }
            .feature-item {
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }
            .feature-item:last-child {
                border-bottom: none;
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
                <h1>Greetings from IDCP Workforce Orchestrator!</h1>
            </div>
            <div class="content">
                <div class="greeting">Hello IBM Team!</div>
                
                <div class="message">
                    <p>We're excited to share that our <strong>Workforce Orchestrator system</strong> is now fully operational with advanced email notification capabilities!</p>
                    
                    <p>This automated email demonstrates our system's ability to send professional, HTML-formatted notifications to multiple recipients.</p>
                </div>
                
                <div class="feature-list">
                    <h3 style="color: #667eea; margin-top: 0;">System Features:</h3>
                    
                    <div class="feature-item">
                        <strong>Email Notifications</strong><br>
                        Automated emails at every workflow stage (Onboarding, BGC, Asset Allocation, Offboarding)
                    </div>
                    
                    <div class="feature-item">
                        <strong>Resume Email Extraction</strong><br>
                        Intelligent parsing of PDF/DOCX resumes to extract real email addresses
                    </div>
                    
                    <div class="feature-item">
                        <strong>Dynamic Candidate Management</strong><br>
                        Refresh button to scan and load new candidates from Resumes folder
                    </div>
                    
                    <div class="feature-item">
                        <strong>BGV Portal</strong><br>
                        AI-powered document verification with Gemini API integration
                    </div>
                    
                    <div class="feature-item">
                        <strong>Workflow Tracking</strong><br>
                        Complete visibility of candidate progress through all stages
                    </div>
                    
                    <div class="feature-item">
                        <strong>Professional Templates</strong><br>
                        Beautiful HTML email templates with gradient designs
                    </div>
                </div>
                
                <div class="message">
                    <h3 style="color: #667eea; margin-top: 0;">Technical Highlights:</h3>
                    <ul>
                        <li>Gmail SMTP integration with TLS encryption</li>
                        <li>Real-time API triggers for workflow stages</li>
                        <li>Python-based email notification agent</li>
                        <li>Resume parsing with PyPDF2 and python-docx</li>
                        <li>RESTful API endpoints for all operations</li>
                        <li>Responsive web dashboard</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                    <p>Sender: idcp.administrator@gmail.com</p>
                    <p>2026 Workforce Orchestrator System - IBM</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("=" * 70)
    print("SENDING BULK GREETING EMAILS TO IBM TEAM")
    print("=" * 70)
    print(f"From: {agent.sender_email}")
    print(f"Recipients: {len(recipients)}")
    print("=" * 70)
    
    # Send emails to all recipients
    results = []
    for recipient in recipients:
        print(f"\nSending to: {recipient}...")
        
        result = agent.send_email(
            recipient_email=recipient,
            subject=subject,
            body_html=body_html
        )
        
        results.append({
            'recipient': recipient,
            'result': result
        })
        
        if result['success']:
            print(f"  SUCCESS - Email sent to {recipient}")
        else:
            print(f"  FAILED - {result.get('error', 'Unknown error')}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    successful = sum(1 for r in results if r['result']['success'])
    failed = len(results) - successful
    
    print(f"Total emails: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        print("\nSuccessfully sent to:")
        for r in results:
            if r['result']['success']:
                print(f"  - {r['recipient']}")
    
    if failed > 0:
        print("\nFailed to send to:")
        for r in results:
            if not r['result']['success']:
                print(f"  - {r['recipient']}: {r['result'].get('error', 'Unknown')}")
    
    print("=" * 70)
    print("\nPlease check all inboxes (and spam folders)!")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    send_bulk_greetings()

# Made with Bob

"""
Email Notification Agent for Workforce Orchestrator
Sends automated emails at various workflow stages
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import json

# Email configuration
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'idcp.administrator@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', 'mzdbgmctrlhtfdjj')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))


class EmailNotificationAgent:
    """Intelligent email notification agent for workforce management"""
    
    def __init__(self, sender_email=None, sender_password=None, smtp_server=None, smtp_port=None):
        self.sender_email = sender_email or SENDER_EMAIL
        self.sender_password = sender_password or SENDER_PASSWORD
        self.smtp_server = smtp_server or SMTP_SERVER
        self.smtp_port = smtp_port or SMTP_PORT
        self.email_history = []
    
    def send_email(self, recipient_email, subject, body_html, cc_emails=None):
        """
        Send an email using SMTP
        
        Args:
            recipient_email: Primary recipient email
            subject: Email subject
            body_html: HTML body content
            cc_emails: List of CC email addresses (optional)
            
        Returns:
            dict: Status of email sending
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Attach HTML body
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                
                # Send email
                recipients = [recipient_email]
                if cc_emails:
                    recipients.extend(cc_emails)
                
                server.send_message(msg)
            
            # Log email
            email_log = {
                "timestamp": datetime.now().isoformat(),
                "recipient": recipient_email,
                "cc": cc_emails,
                "subject": subject,
                "status": "sent"
            }
            self.email_history.append(email_log)
            
            return {
                "success": True,
                "message": f"Email sent successfully to {recipient_email}",
                "log": email_log
            }
            
        except Exception as e:
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "recipient": recipient_email,
                "subject": subject,
                "status": "failed",
                "error": str(e)
            }
            self.email_history.append(error_log)
            
            return {
                "success": False,
                "error": str(e),
                "log": error_log
            }
    
    def send_onboarding_welcome_email(self, employee_data, manager_email=None):
        """Send welcome email to new employee"""
        subject = f"Welcome to the Team, {employee_data['name']}! 🎉"
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .info-box {{ background: white; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome Aboard!</h1>
                    <p>We're excited to have you join our team</p>
                </div>
                <div class="content">
                    <h2>Hello {employee_data['name']},</h2>
                    <p>Welcome to our organization! We're thrilled to have you as part of our team.</p>
                    
                    <div class="info-box">
                        <h3>Your Details:</h3>
                        <p><strong>Employee ID:</strong> {employee_data.get('employee_id', 'Will be assigned')}</p>
                        <p><strong>Designation:</strong> {employee_data.get('designation', 'N/A')}</p>
                        <p><strong>Department:</strong> {employee_data.get('department', 'N/A')}</p>
                        <p><strong>Start Date:</strong> {employee_data.get('start_date', 'TBD')}</p>
                    </div>
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Complete your profile screening</li>
                        <li>Submit required documents for BGC (Background Check)</li>
                        <li>Complete asset allocation process</li>
                        <li>Attend orientation session</li>
                    </ol>
                    
                    <p>If you have any questions, please don't hesitate to reach out to your manager or HR team.</p>
                    
                    <p>Looking forward to working with you!</p>
                    
                    <p><strong>Best regards,</strong><br>
                    IDCP HR Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        cc_emails = [manager_email] if manager_email else None
        return self.send_email(employee_data['email'], subject, body_html, cc_emails)
    
    def send_bgc_initiation_email(self, employee_data, bgv_portal_url):
        """Send BGC initiation email with portal link"""
        subject = f"Action Required: Background Verification - {employee_data['name']}"
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ background: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; font-weight: bold; }}
                .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }}
                .checklist {{ background: white; padding: 20px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Background Verification Required</h1>
                </div>
                <div class="content">
                    <h2>Hello {employee_data['name']},</h2>
                    <p>As part of your onboarding process, we need to complete your background verification.</p>
                    
                    <div class="alert">
                        <strong>⚠️ Action Required:</strong> Please upload your documents within 48 hours.
                    </div>
                    
                    <div class="checklist">
                        <h3>📋 Documents Required:</h3>
                        <ul>
                            <li>✅ Aadhaar Card (Front side - clear image)</li>
                            <li>✅ Aadhaar Card (Back side - clear image)</li>
                            <li>✅ Completed Details Form (PDF/DOCX)</li>
                            <li>✅ Resume/CV (PDF/DOCX)</li>
                        </ul>
                        
                        <p><strong>Important:</strong> Ensure all documents are clear and readable. Our AI system will verify:</p>
                        <ul>
                            <li>Aadhaar structure (12-digit number, logo, QR code)</li>
                            <li>Name consistency across all documents</li>
                            <li>Document authenticity</li>
                        </ul>
                    </div>
                    
                    <center>
                        <a href="{bgv_portal_url}" class="button">🔐 Start BGV Process</a>
                    </center>
                    
                    <p><strong>Need Help?</strong><br>
                    Contact HR at: {self.sender_email}</p>
                    
                    <p><strong>Best regards,</strong><br>
                    IDCP HR Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(employee_data['email'], subject, body_html)
    
    def send_bgc_completion_email(self, employee_data, verification_status, manager_email=None):
        """Send BGC completion notification"""
        status_emoji = "✅" if verification_status == "successful" else "❌" if verification_status == "rejected" else "⚠️"
        status_text = "Successful" if verification_status == "successful" else "Rejected" if verification_status == "rejected" else "Requires Resubmission"
        status_color = "#28a745" if verification_status == "successful" else "#dc3545" if verification_status == "rejected" else "#ffc107"
        
        subject = f"BGC {status_text} - {employee_data['name']}"
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status-box {{ background: white; border-left: 4px solid {status_color}; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_emoji} BGC {status_text}</h1>
                </div>
                <div class="content">
                    <h2>Hello {employee_data['name']},</h2>
                    
                    <div class="status-box">
                        <h3>Verification Status: {status_text}</h3>
                        <p><strong>Employee ID:</strong> {employee_data.get('employee_id', 'N/A')}</p>
                        <p><strong>Verification Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    {'<p>Congratulations! Your background verification has been completed successfully. You can now proceed to the next stage of onboarding.</p>' if verification_status == 'successful' else ''}
                    {'<p>Unfortunately, your background verification could not be completed. Please contact HR for more information.</p>' if verification_status == 'rejected' else ''}
                    {'<p>Your documents require resubmission. Please review the feedback and upload corrected documents.</p>' if verification_status == 'resubmit' else ''}
                    
                    <p><strong>Best regards,</strong><br>
                    IDCP HR Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        cc_emails = [manager_email] if manager_email else None
        return self.send_email(employee_data['email'], subject, body_html, cc_emails)
    
    def send_asset_allocation_email(self, employee_data, assets, manager_email=None):
        """Send asset allocation notification"""
        subject = f"Asset Allocation Confirmation - {employee_data['name']}"
        
        assets_html = ""
        for asset in assets:
            assets_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{asset.get('asset_type', 'N/A')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{asset.get('asset_id', 'N/A')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{asset.get('serial_number', 'N/A')}</td>
            </tr>
            """
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                table {{ width: 100%; background: white; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💼 Assets Allocated</h1>
                </div>
                <div class="content">
                    <h2>Hello {employee_data['name']},</h2>
                    <p>The following assets have been allocated to you:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Asset Type</th>
                                <th>Asset ID</th>
                                <th>Serial Number</th>
                            </tr>
                        </thead>
                        <tbody>
                            {assets_html}
                        </tbody>
                    </table>
                    
                    <p><strong>Important:</strong> Please take care of these assets. You are responsible for their safe keeping.</p>
                    
                    <p><strong>Best regards,</strong><br>
                    IDCP IT Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        cc_emails = [manager_email] if manager_email else None
        return self.send_email(employee_data['email'], subject, body_html, cc_emails)
    
    def send_offboarding_initiation_email(self, employee_data, manager_email=None):
        """Send offboarding initiation email"""
        subject = f"Offboarding Process Initiated - {employee_data['name']}"
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .checklist {{ background: white; padding: 20px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👋 Offboarding Process</h1>
                </div>
                <div class="content">
                    <h2>Hello {employee_data['name']},</h2>
                    <p>Your offboarding process has been initiated.</p>
                    
                    <div class="checklist">
                        <h3>📋 Offboarding Checklist:</h3>
                        <ul>
                            <li>Return all company assets (laptop, phone, ID card, etc.)</li>
                            <li>Complete knowledge transfer</li>
                            <li>Clear all pending tasks</li>
                            <li>Exit interview with HR</li>
                            <li>Final settlement processing</li>
                        </ul>
                    </div>
                    
                    <p><strong>Last Working Day:</strong> {employee_data.get('last_working_day', 'TBD')}</p>
                    
                    <p>Thank you for your contributions to the organization. We wish you all the best in your future endeavors.</p>
                    
                    <p><strong>Best regards,</strong><br>
                    IDCP HR Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        cc_emails = [manager_email] if manager_email else None
        return self.send_email(employee_data['email'], subject, body_html, cc_emails)
    
    def send_offboarding_completion_email(self, employee_data, manager_email=None):
        """Send offboarding completion email"""
        subject = f"Offboarding Completed - {employee_data['name']}"
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Offboarding Completed</h1>
                </div>
                <div class="content">
                    <h2>Hello {employee_data['name']},</h2>
                    <p>Your offboarding process has been completed successfully.</p>
                    
                    <p><strong>Final Details:</strong></p>
                    <ul>
                        <li>All assets have been returned</li>
                        <li>Access has been revoked</li>
                        <li>Final settlement will be processed</li>
                    </ul>
                    
                    <p>Thank you for being part of our team. We wish you success in your future endeavors!</p>
                    
                    <p><strong>Best regards,</strong><br>
                    IDCP HR Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        cc_emails = [manager_email] if manager_email else None
        return self.send_email(employee_data['email'], subject, body_html, cc_emails)
    
    def send_manager_notification(self, manager_email, employee_data, event_type, details=""):
        """Send notification to manager about employee workflow events"""
        event_titles = {
            "onboarding_started": "New Employee Onboarding Started",
            "bgc_completed": "BGC Completed",
            "assets_allocated": "Assets Allocated",
            "onboarding_completed": "Onboarding Completed",
            "offboarding_started": "Employee Offboarding Started",
            "offboarding_completed": "Employee Offboarding Completed"
        }
        
        subject = f"{event_titles.get(event_type, 'Workflow Update')} - {employee_data['name']}"
        
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: white; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Manager Notification</h1>
                </div>
                <div class="content">
                    <h2>{event_titles.get(event_type, 'Workflow Update')}</h2>
                    
                    <div class="info-box">
                        <p><strong>Employee:</strong> {employee_data['name']}</p>
                        <p><strong>Employee ID:</strong> {employee_data.get('employee_id', 'N/A')}</p>
                        <p><strong>Email:</strong> {employee_data['email']}</p>
                        <p><strong>Event:</strong> {event_type.replace('_', ' ').title()}</p>
                        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    {f'<p><strong>Details:</strong> {details}</p>' if details else ''}
                    
                    <p><strong>Best regards,</strong><br>
                    IDCP Workforce Orchestrator</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from IDCP Workforce Orchestrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(manager_email, subject, body_html)
    
    def get_email_history(self):
        """Get email sending history"""
        return self.email_history


# Example usage
if __name__ == "__main__":
    print("Email Notification Agent - Ready for integration")
    
    # Test email configuration
    agent = EmailNotificationAgent()
    print(f"Email Agent configured with: {agent.sender_email}")
    print(f"SMTP Server: {agent.smtp_server}:{agent.smtp_port}")

# Made with Bob
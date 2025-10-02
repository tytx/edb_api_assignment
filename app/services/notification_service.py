"""
Email notification service using AWS SES
"""
import os
import boto3
from botocore.exceptions import ClientError
from models.member_model import Member


class NotificationService:
    """Service for sending email notifications via AWS SES"""

    def __init__(self):
        self.ses_client = boto3.client('ses', region_name=os.getenv('AWS_REGION_NAME', 'us-east-1'))
        self.sender_email = os.getenv('NOTIFICATION_EMAIL', 'admin@yourdomain.com')
        self.enabled = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'

    def send_new_member_notification(self, member: Member, cognito_user_email: str = None) -> bool:
        """
        Send notification email to the Cognito user who created the member

        Args:
            member: The newly created member object
            cognito_user_email: Email of the Cognito user making the request

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print("Notifications are disabled")
            return False

        # Send notification to the Cognito user (the person who submitted the form)
        if cognito_user_email:
            return self._send_cognito_user_notification(member, cognito_user_email)
        else:
            # Fallback: send to admin email if no Cognito user email found
            return self._send_admin_notification(member)

    def _send_cognito_user_notification(self, member: Member, cognito_email: str) -> bool:
        """Send notification to the Cognito user who created the member"""
        subject = f"Member Registration Successful: {member.firstName} {member.lastName}"

        body_text = f"""
Hi,

You have successfully registered a new member.

Member Details:
- Name: {member.firstName} {member.lastName}
- Email: {member.email}
- Phone: {member.phone or 'Not provided'}
- Age: {member.age or 'Not provided'}
- Employee: {'Yes' if member.isEmployee else 'No'}
- Registration Date: {member.createdAt}
- Member ID: {member.id}

Thank you for using the Membership API.
"""

        body_html = f"""
<html>
<head></head>
<body>
  <h2>Member Registration Successful</h2>
  <p>Hi,</p>
  <p>You have successfully registered a new member.</p>

  <h3>Member Details:</h3>
  <table style="border-collapse: collapse; border: 1px solid #ddd;">
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Name</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.firstName} {member.lastName}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Email</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.email}</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Phone</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.phone or 'Not provided'}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Age</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.age or 'Not provided'}</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Employee</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{'Yes' if member.isEmployee else 'No'}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Registration Date</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.createdAt}</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Member ID</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.id}</td>
    </tr>
  </table>

  <p style="margin-top: 20px;">Thank you for using the Membership API.</p>
</body>
</html>
"""

        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [cognito_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': body_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )

            print(f"Notification sent to Cognito user {cognito_email}! Message ID: {response['MessageId']}")
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"Failed to send notification to Cognito user. Error: {error_code} - {error_message}")
            return False
        except Exception as e:
            print(f"Unexpected error sending notification: {str(e)}")
            return False

    def _send_welcome_email_to_member(self, member: Member) -> bool:
        """Send welcome email to the new member"""
        subject = f"Welcome to Our Membership, {member.firstName}!"

        body_text = f"""
Hi {member.firstName},

Thank you for registering! We're excited to have you as a member.

Your registration details:
- Name: {member.firstName} {member.lastName}
- Email: {member.email}
- Phone: {member.phone or 'Not provided'}
- Member ID: {member.id}

If you have any questions, please don't hesitate to reach out.

Best regards,
The Membership Team
"""

        body_html = f"""
<html>
<head></head>
<body>
  <h2>Welcome to Our Membership!</h2>
  <p>Hi {member.firstName},</p>
  <p>Thank you for registering! We're excited to have you as a member.</p>

  <h3>Your Registration Details:</h3>
  <table style="border-collapse: collapse; border: 1px solid #ddd;">
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Name</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.firstName} {member.lastName}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Email</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.email}</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Phone</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.phone or 'Not provided'}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Member ID</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.id}</td>
    </tr>
  </table>

  <p style="margin-top: 20px;">If you have any questions, please don't hesitate to reach out.</p>
  <p>Best regards,<br>The Membership Team</p>
</body>
</html>
"""

        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [member.email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': body_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )

            print(f"Welcome email sent to {member.email}! Message ID: {response['MessageId']}")
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"Failed to send welcome email to member. Error: {error_code} - {error_message}")
            return False
        except Exception as e:
            print(f"Unexpected error sending welcome email: {str(e)}")
            return False

    def _send_admin_notification(self, member: Member) -> bool:
        """Send notification to admin about new member"""
        subject = f"New Member Registration: {member.firstName} {member.lastName}"

        body_text = f"""
New Member Registration

Name: {member.firstName} {member.lastName}
Email: {member.email}
Phone: {member.phone or 'Not provided'}
Age: {member.age or 'Not provided'}
Employee: {'Yes' if member.isEmployee else 'No'}
Registration Date: {member.createdAt}
Member ID: {member.id}

---
This is an automated notification from the Membership API.
"""

        body_html = f"""
<html>
<head></head>
<body>
  <h2>New Member Registration</h2>
  <table style="border-collapse: collapse; border: 1px solid #ddd;">
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Name</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.firstName} {member.lastName}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Email</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.email}</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Phone</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.phone or 'Not provided'}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Age</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.age or 'Not provided'}</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Employee</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{'Yes' if member.isEmployee else 'No'}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Registration Date</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.createdAt}</td>
    </tr>
    <tr style="background-color: #f2f2f2;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Member ID</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">{member.id}</td>
    </tr>
  </table>
  <p style="color: #666; font-size: 12px; margin-top: 20px;">
    This is an automated notification from the Membership API.
  </p>
</body>
</html>
"""

        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [self.sender_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': body_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )

            print(f"Email sent successfully! Message ID: {response['MessageId']}")
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"Failed to send email. Error: {error_code} - {error_message}")

            # Don't fail the API request if email fails - just log it
            if error_code == 'MessageRejected':
                print("Email address not verified in SES. Please verify the sender email in AWS SES console.")

            return False
        except Exception as e:
            print(f"Unexpected error sending email: {str(e)}")
            return False


# Singleton instance
_notification_service = None

def get_notification_service() -> NotificationService:
    """Get or create notification service singleton"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service

import requests
from decouple import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def logToSlack(url, payload, headers={"Content-Type": "application/json"}):
    requests.post(url=url, headers=headers, json=payload)


# sendgrid
def send_email(from_email, to_email, subject, html_content):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    api_key = config("SIMBA_MAILING_API_KEY")
    if api_key:
        sg = SendGridAPIClient(api_key)

        sg.send(message)
        
def send_verification_email(to_email, code):
    from_email="tito.adeoye.1@gmail.com"
    to_email=to_email
    subject="Verify your email"
    html_content=f"""
        <h2>Welcome 🎉</h2>
        <p>You registered with: <b>{to_email}</b></p>
        <p>Your verification code:</p>
        <h1>{code}</h1>
        <p>This code expires in 10 minutes.</p>
        """

    send_email(
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )
        
def send_reset_password_email(to_email, reset_link):
    name = to_email.split('@')[0]
    
    from_email="tito.adeoye.1@gmail.com"
    to_email=to_email
    subject="Reset password"
    html_content=f"""
    <html>
      <body>
        <p>Hi {name},</p>
        <p>You requested a password reset. Click the link below to set a new password:</p>
        <p>
          <a href="{reset_link}" style="padding:10px 20px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px;">
            Reset Password
          </a>
          or click this link:
          <span>{reset_link}</span>
        </p>
        <p>If you didn't request this, you can ignore this email.</p>
        <p>Thanks,<br/>The App Team</p>
      </body>
    </html>
    """
    
    
    send_email(
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        html_content=html_content
    )


def upload_to_cloudinary(file, type="auto"):
    if not file:
        raise Exception('File does not exist')
    
    try:
        cloudinary_url = f"https://api.cloudinary.com/v1_1/{config('CLOUDINARY_CLOUD_NAME')}/{type}/upload"
        files = {'file': file}
        payload = {
			"upload_preset": config('CLOUDINARY_UPLOAD_PRESET_NAME'),
			"public_id": config('CLOUDINARY_PID'),
		}
        
        response = requests.post(url=cloudinary_url, data=payload, files=files)
        
        response.raise_for_status()
        data = response.json()
        
        return getattr(data, 'secure_url')
        
    except Exception as e:
        raise e
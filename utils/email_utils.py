import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import url_for, current_app

mail = Mail()

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def send_reset_email(user_email):
    # The token generation is already handled inside the function,
    # so we don't need it as a parameter
    token = get_serializer().dumps(user_email, salt='password-reset-salt')
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    msg = Message(
        'SmartArters - Password Reset Request',
        sender=os.getenv('MAIL_DEFAULT_SENDER'),
        recipients=[user_email]
    )
    
    # Plain text version
    msg.body = f'''To reset your password, visit the following link:

{reset_url}

If you did not make this request, please ignore this email.'''

    # HTML version
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
        <h1 style="color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Password Reset Request</h1>
        
        <div style="color: #34495e; line-height: 1.6; margin: 20px 0;">
            <p style="margin: 10px 0;">A password reset has been requested for your SmartArters account.</p>
            
            <p style="margin: 10px 0; color: #e74c3c;">This link will expire in 15 minutes.</p>
            
            <div style="background-color: #f8f9fa; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <p style="margin: 10px 0;">Click the button below to reset your password:</p>
                
                <a href="{reset_url}" style="display: inline-block; background-color: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px 0;">Reset Password</a>
                
                <p style="margin: 10px 0; font-size: 0.9em; color: #7f8c8d;">Or copy and paste this URL into your browser:</p>
                <p style="margin: 10px 0; word-break: break-all; font-size: 0.9em; color: #3498db;">{reset_url}</p>
            </div>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="margin: 5px 0; color: #7f8c8d; font-size: 0.9em;">If you did not request this password reset, please ignore this email.</p>
            <p style="margin: 5px 0; color: #2c3e50; font-weight: bold;">The SmartArters Team</p>
        </div>
    </div>
    '''
    mail.send(msg)

def send_welcome_email(user_email, name):
    msg = Message(
        'Welcome to SmartArters!',
        sender=os.getenv('MAIL_DEFAULT_SENDER'),
        recipients=[user_email]
    )
    
    # Plain text version
    msg.body = f'''Welcome to SmartArters, {name}!

Thank you for choosing SmartArters. We're excited to have you on board.

You can now log in to your account and start ranking your favorite artworks.
At the draw you will be able to relax and enjoy drinks with your friends, instead of worrying about keeping track of your rankings on paper.

Best regards,
The SmartArters Team'''

    # HTML version
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
        <h1 style="color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Welcome to SmartArters!</h1>
        
        <div style="color: #34495e; line-height: 1.6; margin: 20px 0;">
            <p style="margin: 10px 0;">Dear {name},</p>
            
            <p style="margin: 10px 0;">Thank you for joining SmartArters. We're excited to have you on board.</p>
            
            <p style="margin: 10px 0;">You can now log in to your account and start ranking your favorite artworks.</p>
            
            <p style="margin: 10px 0;">At the draw you will be able to relax and enjoy drinks with your friends, instead of worrying about keeping track of your rankings on paper.</p>
            
            <p style="margin: 10px 0; color: #3498db;">Here's to digitalizing the Altera art club! 🍻</p>

            <p style="margin: 10px 0;">You can login at <a href="{url_for('auth.login', _external=True)}">{url_for('auth.login', _external=True)}</a>.</p>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="margin: 5px 0;">Best regards,</p>
            <p style="margin: 5px 0; color: #2c3e50; font-weight: bold;">The SmartArters Team</p>
        </div>
    </div>
    '''
    mail.send(msg) 
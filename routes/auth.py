from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database.db import get_db_connection
from utils.email_utils import send_reset_email, get_serializer, send_welcome_email
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('rankings.rankings'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', 
                          (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('rankings.rankings'))
        
        return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        conn = get_db_connection()
        
        if conn.execute('SELECT id FROM users WHERE email = ?', 
                       (email,)).fetchone():
            conn.close()
            return render_template('signup.html', error='Email already registered')
        
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                    (name, email, hashed_password))
        conn.commit()
        conn.close()
        
        # Send welcome email after successful registration
        send_welcome_email(email, name)
        
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            # Reset the token_used flag when generating a new token
            conn.execute('UPDATE users SET reset_token_used = 0 WHERE email = ?', 
                        (email,))
            conn.commit()
            conn.close()
            
            # Generate token and send email
            token = get_serializer().dumps(email, salt='password-reset-salt')
            send_reset_email(email)
            
            flash('Password reset instructions have been sent to your email.', 'info')
            return redirect(url_for('auth.login'))
        
        conn.close()
        flash('Email address not found.', 'error')
        return redirect(url_for('auth.forgot_password'))
    return render_template('forgot_password.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = get_serializer().loads(token, salt='password-reset-salt', max_age=900)
        
        # Clear any existing flash messages
        session.pop('_flashes', None)
        
        # Check if token has been used
        conn = get_db_connection()
        token_used = conn.execute('SELECT reset_token_used FROM users WHERE email = ?', 
                                (email,)).fetchone()['reset_token_used']
        conn.close()
        
        if token_used == 1:
            flash('This password reset link has already been used. Please request a new one if needed.', 'error')
            return redirect(url_for('auth.forgot_password'))
            
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    # Clear any existing flash messages when showing the reset form
    session.pop('_flashes', None)
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html')
        
        conn = get_db_connection()
        hashed_password = generate_password_hash(password)
        # Update password and mark token as used
        conn.execute('''UPDATE users 
                       SET password = ?, reset_token_used = 1 
                       WHERE email = ?''',
                    (hashed_password, email))
        conn.commit()
        conn.close()
        
        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password.html')
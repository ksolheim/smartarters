from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-please-change')

DATABASE = 'database/raffle_rankings.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', 
                          (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('rankings'))
        
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        conn = get_db_connection()
        
        # Check if username already exists
        if conn.execute('SELECT id FROM users WHERE username = ?', 
                       (username,)).fetchone():
            conn.close()
            return render_template('signup.html', error='Username already exists')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, hashed_password))
        conn.commit()
        conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/rankings')
@login_required
def rankings():
    conn = get_db_connection()
    
    # Get artworks with their rankings for the current user
    artworks = conn.execute("""
        SELECT 
            a.*,
            ur.rank
        FROM artworks a
        LEFT JOIN user_rankings ur 
            ON a.art_id = ur.art_id 
            AND ur.user_id = ?
        ORDER BY COALESCE(ur.rank, 999999)  -- Unranked items go to the end
    """, (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('rankings.html', artworks=artworks)

@app.route('/draw', methods=['GET'])
@login_required
def draw():
    conn = get_db_connection()
    try:
        artworks = conn.execute('''
            SELECT 
                a.art_id, 
                a.art_title,
                a.artist,
                COALESCE(s.is_won, 0) as is_won,
                COALESCE(ur.rank, 0) as user_ranking
            FROM artworks a 
            LEFT JOIN artwork_status s 
                ON a.art_id = s.art_id AND s.user_id = ?
            LEFT JOIN user_rankings ur
                ON a.art_id = ur.art_id AND ur.user_id = ?
            WHERE ur.rank > 0  -- Only get ranked artworks
            ORDER BY ur.rank
            LIMIT 5  -- Get only top 5
        ''', (session['user_id'], session['user_id'])).fetchall()
        return render_template('draw.html', artworks=artworks)
    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500
    finally:
        conn.close()

@app.route('/mark_won/<int:art_id>', methods=['POST'])
@login_required
def mark_won(art_id):
    conn = get_db_connection()
    try:
        # Check if a record already exists
        existing = conn.execute(
            'SELECT 1 FROM artwork_status WHERE art_id = ? AND user_id = ?', 
            (art_id, session['user_id'])
        ).fetchone()
        
        if existing:
            conn.execute(
                'UPDATE artwork_status SET is_won = 1 WHERE art_id = ? AND user_id = ?',
                (art_id, session['user_id'])
            )
        else:
            conn.execute(
                'INSERT INTO artwork_status (art_id, user_id, is_won) VALUES (?, ?, 1)',
                (art_id, session['user_id'])
            )
        
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/update_rankings', methods=['POST'])
@login_required
def update_rankings():
    rankings = request.json.get('rankings', [])
    user_id = session['user_id']
    
    conn = get_db_connection()
    try:
        # Delete existing rankings for this user
        conn.execute('DELETE FROM user_rankings WHERE user_id = ?', (user_id,))
        
        # Insert new rankings
        for ranking in rankings:
            conn.execute(
                'INSERT INTO user_rankings (user_id, art_id, rank) VALUES (?, ?, ?)',
                (user_id, ranking['art_id'], ranking['rank'])
            )
        
        conn.commit()
        return jsonify({'status': 'success'})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001, debug=True)
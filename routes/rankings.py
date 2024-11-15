from flask import Blueprint, render_template, request, jsonify, session
import sqlite3
from routes.auth import login_required
from database.db import get_db_connection

rankings_bp = Blueprint('rankings', __name__)

@rankings_bp.route('/rankings')
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

@rankings_bp.route('/update_rankings', methods=['POST'])
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
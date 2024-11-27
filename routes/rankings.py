"""Rankings routes."""
from flask import Blueprint, render_template, request, jsonify, session
from routes.auth import login_required
from database.db import get_db_connection, dict_cursor

rankings_bp = Blueprint('rankings', __name__)

@rankings_bp.route('/rankings')
@login_required
def rankings():
    """Rankings route."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.*,
                ur.rank
            FROM artworks a
            LEFT JOIN user_rankings ur 
                ON a.art_id = ur.art_id 
                AND ur.user_id = ?
            ORDER BY COALESCE(ur.rank, 999999)  -- Unranked items go to the end
        """, (session['user_id'],))
        
        artworks = dict_cursor(cursor)
        return render_template('rankings.html', artworks=artworks)
    finally:
        cursor.close()
        conn.close()

@rankings_bp.route('/update_rankings', methods=['POST'])
@login_required
def update_rankings():
    """Update rankings route."""
    ranking_data = request.json.get('rankings', [])
    user_id = session['user_id']

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_rankings WHERE user_id = ?', (user_id,))

        for ranking in ranking_data:
            cursor.execute(
                'INSERT INTO user_rankings (user_id, art_id, rank) VALUES (?, ?, ?)',
                (user_id, ranking['art_id'], ranking['rank'])
            )

        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

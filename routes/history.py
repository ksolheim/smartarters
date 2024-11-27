from flask import Blueprint, render_template, jsonify, session
from routes.auth import login_required
from database.db import get_db_connection, dict_cursor

history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
@login_required
def history():
    """History route."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                a.art_id, 
                a.art_title,
                a.artist,
                a.price,
                a.jpg_name,
                COALESCE(s.is_won, 0) as is_won,
                COALESCE(ur.rank, 0) as user_ranking
            FROM artworks a 
            LEFT JOIN artwork_status s 
                ON a.art_id = s.art_id AND s.user_id = ?
            LEFT JOIN user_rankings ur
                ON a.art_id = ur.art_id AND ur.user_id = ?
            ORDER BY a.art_id ASC
        ''', (session['user_id'], session['user_id']))
        
        artworks = dict_cursor(cursor)
        return render_template('history.html', artworks=artworks)
    except Exception as e:
        return f"Database error: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()

@history_bp.route('/history/undo_won/<int:art_id>', methods=['POST'])
@login_required
def undo_won(art_id):
    """Undo won route."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM artwork_status 
            WHERE user_id = ? AND art_id = ?
        ''', (session['user_id'], art_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

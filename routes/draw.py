"""Draw routes."""
from flask import Blueprint, render_template, jsonify, session
from routes.auth import login_required
from database.db import get_db_connection
from database.db import dict_cursor, dict_cursor_one

draw_bp = Blueprint('draw', __name__)

@draw_bp.route('/draw', methods=['GET'])
@login_required
def draw():
    """Draw route."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT TOP 5
                a.art_id, 
                a.art_title,
                a.artist,
                a.price,
                COALESCE(s.is_won, 0) as is_won,
                COALESCE(ur.rank, 0) as user_ranking
            FROM artworks a 
            LEFT JOIN artwork_status s 
                ON a.art_id = s.art_id AND s.user_id = ?
            LEFT JOIN user_rankings ur
                ON a.art_id = ur.art_id AND ur.user_id = ?
            WHERE ur.rank > 0  -- Only get ranked artworks
            AND (s.is_won IS NULL OR s.is_won = 0)  -- Only get artworks not marked as won
            ORDER BY ur.rank
        ''', (session['user_id'], session['user_id']))
        
        artworks = dict_cursor(cursor)
        return render_template('draw.html', artworks=artworks)
    except Exception as e:
        return f"Database error: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()

@draw_bp.route('/get_next_artworks', methods=['GET'])
@login_required
def get_next_artworks():
    """Get next artworks route."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT TOP 5
                a.art_id, 
                a.art_title,
                a.artist,
                a.price,
                COALESCE(s.is_won, 0) as is_won,
                COALESCE(ur.rank, 0) as user_ranking
            FROM artworks a 
            LEFT JOIN artwork_status s 
                ON a.art_id = s.art_id AND s.user_id = ?
            LEFT JOIN user_rankings ur
                ON a.art_id = ur.art_id AND ur.user_id = ?
            WHERE ur.rank > 0  -- Only get ranked artworks
            AND (s.is_won IS NULL OR s.is_won = 0)  -- Only get artworks not marked as won
            ORDER BY ur.rank
        ''', (session['user_id'], session['user_id']))

        artwork_list = dict_cursor(cursor)

        return jsonify({
            'success': True,
            'artworks': artwork_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@draw_bp.route('/mark_won/<int:art_id>', methods=['POST'])
@login_required
def mark_won(art_id):
    """Mark won route."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                a.art_id, 
                a.art_title,
                a.artist,
                a.price,
                COALESCE(ur.rank, 0) as user_ranking,
                s.is_won
            FROM artworks a 
            LEFT JOIN user_rankings ur
                ON a.art_id = ur.art_id AND ur.user_id = ?
            LEFT JOIN artwork_status s
                ON a.art_id = s.art_id AND s.user_id = ?
            WHERE a.art_id = ?
        ''', (session['user_id'], session['user_id'], art_id))
        
        artwork = dict_cursor_one(cursor)

        if not artwork:
            return jsonify({'error': 'Artwork not found'}), 404

        if artwork.get('is_won') == 1:
            return jsonify({
                'success': False,
                'error': 'This artwork has already been marked as won'
            }), 400

        cursor.execute('''
            MERGE artwork_status AS target
            USING (VALUES (?, ?, 1)) AS source (user_id, art_id, is_won)
            ON target.user_id = source.user_id AND target.art_id = source.art_id
            WHEN MATCHED THEN
                UPDATE SET is_won = source.is_won
            WHEN NOT MATCHED THEN
                INSERT (user_id, art_id, is_won)
                VALUES (source.user_id, source.art_id, source.is_won);
        ''', (session['user_id'], art_id))

        conn.commit()

        return jsonify({
            'success': True,
            'artwork': artwork
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

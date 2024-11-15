from flask import Blueprint, render_template, request, jsonify, session
from routes.auth import login_required
from database.db import get_db_connection
import sqlite3

draw_bp = Blueprint('draw', __name__)

@draw_bp.route('/draw', methods=['GET'])
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
            AND (s.is_won IS NULL OR s.is_won = 0)  -- Only get artworks not marked as won
            ORDER BY ur.rank
            LIMIT 5  -- Get only top 5
        ''', (session['user_id'], session['user_id'])).fetchall()
        return render_template('draw.html', artworks=artworks)
    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500
    finally:
        conn.close()

@draw_bp.route('/get_next_artworks', methods=['GET'])
@login_required
def get_next_artworks():
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
            AND (s.is_won IS NULL OR s.is_won = 0)  -- Only get artworks not marked as won
            ORDER BY ur.rank
            LIMIT 5  -- Get only top 5
        ''', (session['user_id'], session['user_id'])).fetchall()
        
        artwork_list = [dict(artwork) for artwork in artworks]
        print("Next artworks:", artwork_list)  # Debug print
        
        return jsonify({
            'success': True,
            'artworks': artwork_list
        })
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@draw_bp.route('/mark_won/<int:art_id>', methods=['POST'])
@login_required
def mark_won(art_id):
    conn = get_db_connection()
    try:
        artwork = conn.execute('''
            SELECT 
                a.art_id, 
                a.art_title,
                a.artist,
                COALESCE(ur.rank, 0) as user_ranking,
                s.is_won
            FROM artworks a 
            LEFT JOIN user_rankings ur
                ON a.art_id = ur.art_id AND ur.user_id = ?
            LEFT JOIN artwork_status s
                ON a.art_id = s.art_id AND s.user_id = ?
            WHERE a.art_id = ?
        ''', (session['user_id'], session['user_id'], art_id)).fetchone()
        
        if not artwork:
            return jsonify({'error': 'Artwork not found'}), 404

        if artwork['is_won'] == 1:
            return jsonify({
                'success': False,
                'error': 'This artwork has already been marked as won'
            }), 400

        conn.execute('''
            INSERT OR REPLACE INTO artwork_status (user_id, art_id, is_won) 
            VALUES (?, ?, 1)
        ''', (session['user_id'], art_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'artwork': dict(artwork)
        })
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close() 
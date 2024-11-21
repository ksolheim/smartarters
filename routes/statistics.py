"""Statistics routes."""
import sqlite3
from flask import Blueprint, render_template, session
from routes.auth import login_required
from database.db import get_db_connection

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/statistics')
@login_required
def statistics():
    """Statistics route."""
    conn = get_db_connection()
    # Fetch the most popular artworks based on user rankings
    artworks = conn.execute("""
        SELECT 
            a.art_id, 
            a.art_title, 
            a.artist, 
            COUNT(ur.rank) AS rank_count
        FROM artworks a
        JOIN user_rankings ur ON a.art_id = ur.art_id
        GROUP BY a.art_id
        ORDER BY rank_count DESC
        LIMIT 10
    """).fetchall()
    
    conn.close()
    return render_template('statistics.html', artworks=artworks) 
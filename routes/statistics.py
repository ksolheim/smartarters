"""Statistics routes."""
from flask import Blueprint, render_template
from routes.auth import login_required
from database.db import get_db_connection

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/statistics')
@login_required
def statistics():
    """Statistics route."""
    conn = get_db_connection()
    
    # Fetch all artworks with their statistics
    artworks = conn.execute("""
        SELECT 
            a.art_id, 
            a.art_title, 
            a.artist, 
            AVG(ur.rank) AS average_rank,
            COUNT(CASE WHEN ur.rank = 1 THEN 1 END) AS first_place_count,
            COUNT(CASE WHEN ur.rank = 2 THEN 1 END) AS second_place_count,
            COUNT(CASE WHEN ur.rank = 3 THEN 1 END) AS third_place_count
        FROM artworks a
        JOIN user_rankings ur ON a.art_id = ur.art_id
        GROUP BY a.art_id
    """).fetchall()
    
    # Prepare data sorted by Average Rank (ascending)
    average_sorted_artworks = sorted(artworks, key=lambda x: (x['average_rank'], -x['first_place_count']))
    average_labels = [artwork['art_title'] for artwork in average_sorted_artworks]
    average_data = [int(round(artwork['average_rank'])) for artwork in average_sorted_artworks]  # Rounded to whole numbers
    
    # Filter artworks that have at least one first, second, or third-place ranking
    top_ranked_artworks = [
        artwork for artwork in artworks 
        if artwork['first_place_count'] > 0 
        or artwork['second_place_count'] > 0 
        or artwork['third_place_count'] > 0
    ]
    
    # Prepare data sorted by Top Rankings (first, then second, then third)
    top_sorted_artworks = sorted(
        top_ranked_artworks, 
        key=lambda x: (
            -x['first_place_count'], 
            -x['second_place_count'], 
            -x['third_place_count']
        )
    )
    top_labels = [artwork['art_title'] for artwork in top_sorted_artworks]
    first_place = [artwork['first_place_count'] for artwork in top_sorted_artworks]
    second_place = [artwork['second_place_count'] for artwork in top_sorted_artworks]
    third_place = [artwork['third_place_count'] for artwork in top_sorted_artworks]
    
    conn.close()
    
    return render_template(
        'statistics.html', 
        artworks=artworks,  # All artworks for the table
        average_labels=average_labels,
        average_data=average_data,
        top_labels=top_labels,
        first_place=first_place,
        second_place=second_place,
        third_place=third_place
    ) 
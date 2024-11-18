"""Main routes."""
from flask import Blueprint, redirect, url_for, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Index route."""
    if 'user_id' in session:
        return redirect(url_for('rankings.rankings'))
    return redirect(url_for('auth.login'))

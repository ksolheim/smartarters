from flask import Flask
import os
from routes.auth import auth_bp
from routes.rankings import rankings_bp
from routes.draw import draw_bp
from routes.history import history_bp
from routes.main import main_bp

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key-please-change')

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(rankings_bp)
app.register_blueprint(draw_bp)
app.register_blueprint(history_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001, debug=True)
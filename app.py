"""Main application."""
import os
from flask import Flask
from dotenv import load_dotenv
from routes.auth import auth_bp
from routes.rankings import rankings_bp
from routes.draw import draw_bp
from routes.history import history_bp
from routes.main import main_bp
from utils.email_utils import mail

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'dev-key-please-change')

app.config.update(
    MAIL_SERVER = os.getenv('MAIL_SERVER'),
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587')),
    MAIL_USE_TLS = False,
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER'),
    SERVER_NAME = os.getenv('SERVER_NAME')
)

mail.init_app(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(rankings_bp)
app.register_blueprint(draw_bp)
app.register_blueprint(history_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001, debug=True)

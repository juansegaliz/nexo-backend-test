from flask import Flask, send_from_directory
from dotenv import load_dotenv
from app.extensions import init_cors
from config import Settings
import os


def create_app():
    load_dotenv()
    app = Flask(__name__)
    init_cors(app)

    from app.routes.health import bp as health_bp
    app.register_blueprint(health_bp, url_prefix="/")

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/")

    from app.routes.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix="/")

    from app.routes.friends import bp as friends_bp
    app.register_blueprint(friends_bp, url_prefix="/")

    @app.get("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(os.path.join(os.path.dirname(__file__), "../uploads"), filename)

    return app

from flask import Flask
from routes.main_routes import main_bp
from config import Config

def create_app():
    app = Flask(__name__, static_folder="views", static_url_path="")
    app.secret_key = Config.FLASK_SECRET_KEY
    app.register_blueprint(main_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=8000)
from flask import Flask
from routes.main_routes import main_bp

def create_app():
    app = Flask(__name__, static_folder="views", static_url_path="")
    app.register_blueprint(main_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=8000)
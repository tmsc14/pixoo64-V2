from flask import Blueprint, jsonify, request, send_from_directory
from services.data_service import DataService, BeerDataService
from services.pixoo_service import PixooService
from themes.flags_attendance import FlagsAttendanceTheme
from themes.beer_consumed import BeerConsumedTheme
from config import Config
import time

main_bp = Blueprint('main', __name__)
current_theme = None  # Will be initialized based on active theme

THEME_MAP = {
    "flags": FlagsAttendanceTheme,
    "beer": BeerConsumedTheme
}

@main_bp.route("/")
def serve_dashboard():
    return send_from_directory("views", "dashboard.html")

@main_bp.route("/api/kpi-data", methods=["GET"])
def get_kpi_data():
    theme = request.args.get("theme", "flags")
    service = DataService if theme == "flags" else BeerDataService
    return jsonify(service.read_data())

@main_bp.route("/api/update-kpis", methods=["POST"])
def update_kpis():
    data = request.json
    theme = data.pop("theme", "flags")
    
    # Select appropriate data service
    service = DataService if theme == "flags" else BeerDataService
    service.write_data(data)
    
    # Initialize theme and Pixoo service
    global current_theme
    current_theme = THEME_MAP[theme]()
    pixoo = PixooService()
    
    # Generate and display image
    static_img = current_theme.render_static(data)
    pixoo.draw_image(static_img)
    
    def animation_loop():
        frame_index = 0
        while not pixoo.stop_animation:
            animated_frame = current_theme.animate_frame(data, frame_index, static_img)
            pixoo.draw_image(animated_frame)
            frame_index += 1
            time.sleep(Config.ANIMATION_FRAME_DELAY)
    
    pixoo.start_animation(animation_loop)
    return jsonify(status="success", data=data)
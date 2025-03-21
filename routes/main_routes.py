from flask import Blueprint, jsonify, request, send_from_directory
from services.data_service import DataService
from services.pixoo_service import PixooService
from themes.flags_attendance import FlagsAttendanceTheme
from config import Config
import time

main_bp = Blueprint('main', __name__)
current_theme = FlagsAttendanceTheme()

@main_bp.route("/")
def serve_dashboard():
    return send_from_directory("views", "dashboard.html")

@main_bp.route("/api/kpi-data", methods=["GET"])
def get_kpi_data():
    return jsonify(DataService.read_data())

@main_bp.route("/api/update-kpis", methods=["POST"])
def update_kpis():
    data = request.json
    DataService.write_data(data)
    
    pixoo = PixooService()
    static_img = current_theme.render_static(data)
    pixoo.draw_image(static_img)
    
    def animation_loop():
        frame_index = 0
        while not pixoo.stop_animation:
            animated_frame = current_theme.animate_frame(data, frame_index, static_img)
            pixoo.draw_image(animated_frame)
            frame_index += 1
            time.sleep(Config.ANIMATION_FRAME_DELAY) # Delay between frames
    
    pixoo.start_animation(animation_loop)
    return jsonify(status="success", data=data)
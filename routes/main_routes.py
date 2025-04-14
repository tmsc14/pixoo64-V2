from flask import Blueprint, jsonify, request, send_from_directory, Response, stream_with_context
from services.data_service import DataService, BeerDataService
from services.pixoo_service import PixooService
from themes.flags_attendance import FlagsAttendanceTheme
from themes.beer_consumed import BeerConsumedTheme
from themes.ai_chat import AIChatTheme
from config import Config
import time
import requests

main_bp = Blueprint('main', __name__)
current_theme = None

THEME_MAP = {
    "flags": FlagsAttendanceTheme,
    "beer": BeerConsumedTheme,
    "chatbot": AIChatTheme
}

@main_bp.route("/")
def serve_dashboard():
    return send_from_directory("views", "dashboard.html")

@main_bp.route("/api/kpi-data", methods=["GET"])
def get_kpi_data():
    theme = request.args.get("theme", "flags")
    service = DataService if theme == "flags" else BeerDataService
    return jsonify(service.read_data())

def validate_and_parse_color(data, key):
    """Ensure that we are getting a valid color string or default."""
    default_color = "0,0,0"
    color_str = data.get(key, default_color)
    try:
        color_str = color_str.lstrip('#')
        if 'NaN' in color_str.upper():
            print(f"Invalid color '{color_str}', using default '{default_color}'.")
            return default_color
        if len(color_str) == 6:
            return f"{int(color_str[0:2], 16)},{int(color_str[2:4], 16)},{int(color_str[4:6], 16)}"
        else:
            parts = color_str.split(',')
            if len(parts) == 3 and all(part.isdigit() for part in parts):
                return color_str
    except Exception as e:
        print(f"Failed parsing color {key}: {color_str}, error: {e}, defaulting to {default_color}")
        return default_color
    return default_color

@main_bp.route('/api/update-kpis', methods=['POST'])
def update_kpis():
    global current_theme, pixoo
    data = request.json
    theme = data.pop("theme", "flags")
    data['line_color'] = validate_and_parse_color(data, 'line_color')
    data['background_color'] = validate_and_parse_color(data, 'background_color')
    data['text_color'] = validate_and_parse_color(data, 'text_color')
    current_theme = THEME_MAP[theme]()
    pixoo = PixooService()
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
    if theme == "flags":
        DataService.write_data(data)
    elif theme == "beer":
        BeerDataService.write_data(data)
    return jsonify(status="success", data=data)

@main_bp.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    headers = {
        'Authorization': f'Bearer {Config.DIFY_API_KEY}',
        'Content-Type': 'application/json'
    }
    dify_response = requests.post(
        'https://aibot.cloudstaff.io/v1/chat-messages',
        json=data,
        headers=headers,
        stream=True
    )
    def generate():
        for chunk in dify_response.iter_content(chunk_size=None):
            yield chunk
    return Response(
        stream_with_context(generate()),
        content_type=dify_response.headers.get('Content-Type', 'text/event-stream')
    )

@main_bp.route('/api/pixoo-display', methods=['POST'])
def pixoo_display():
    global current_theme, pixoo
    data = request.json
    theme = data.get("theme")
    if theme not in THEME_MAP:
        return jsonify({"status": "error", "message": "Invalid theme"}), 400
    current_theme = THEME_MAP[theme]()
    pixoo = PixooService()
    static_img = current_theme.render_static(data)
    pixoo.draw_image(static_img)
    def animation_loop():
        frame_index = 0
        while not pixoo.stop_animation:
            animated_frame = current_theme.animate_frame(data, frame_index, static_img)
            pixoo.draw_image(animated_frame)
            frame_index += 1
            time.sleep(Config.ANIMATION_FRAME_DELAY / 2 if data.get("state") == "thinking" else Config.ANIMATION_FRAME_DELAY)
    pixoo.start_animation(animation_loop)
    return jsonify({"status": "success"})
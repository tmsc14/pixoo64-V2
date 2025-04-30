from flask import Blueprint, jsonify, request, send_from_directory, Response, stream_with_context, session
from services.data_service import DataService, BeerDataService, ChatbotDataService
from services.pixoo_service import PixooService
from themes.flags_attendance import FlagsAttendanceTheme
from themes.beer_consumed import BeerConsumedTheme
from themes.ai_chat import AIChatTheme
from config import Config
import time
import requests

main_bp = Blueprint('main', __name__)
current_theme = None
pixoo = PixooService()
chatbot_data_cache = None

THEME_MAP = {
    "flags": FlagsAttendanceTheme,
    "beer": BeerConsumedTheme,
    "chatbot": AIChatTheme
}

def get_tokens_used():
    global chatbot_data_cache
    if chatbot_data_cache is None:
        chatbot_data_cache = ChatbotDataService.read_data() or {}
    return session.get('tokens_used', chatbot_data_cache.get('tokens_used', 0))

@main_bp.route("/")
def serve_dashboard():
    return send_from_directory("views", "dashboard.html")

@main_bp.route("/api/kpi-data", methods=["GET"])
def get_kpi_data():
    theme = request.args.get("theme", "flags")
    try:
        if theme == "chatbot":
            data = ChatbotDataService.read_data()
        else:
            service = DataService if theme == "flags" else BeerDataService
            data = service.read_data()
        if not data:
            return jsonify({"status": "error", "code": "NO_DATA"}), 404
        return jsonify(data)
    except Exception:
        return jsonify({"status": "error", "code": "KPI_FETCH_FAILED"}), 500

def validate_and_parse_color(data, key):
    default_color = "0,0,0"
    color_str = data.get(key, default_color)
    try:
        color_str = color_str.lstrip('#')
        if 'NaN' in color_str.upper():
            return default_color
        if len(color_str) == 6:
            return f"{int(color_str[0:2], 16)},{int(color_str[2:4], 16)},{int(color_str[4:6], 16)}"
        else:
            parts = color_str.split(',')
            if len(parts) == 3 and all(part.isdigit() for part in parts):
                return color_str
    except Exception:
        return default_color

@main_bp.route('/api/update-kpis', methods=['POST'])
def update_kpis():
    global current_theme, chatbot_data_cache
    chatbot_data_cache = None
    data = request.json
    theme = data.pop("theme", "flags")
    try:
        data['line_color'] = validate_and_parse_color(data, 'line_color')
        data['background_color'] = validate_and_parse_color(data, 'background_color')
        data['text_color'] = validate_and_parse_color(data, 'text_color')
        
        current_theme = THEME_MAP[theme]()
        static_img = current_theme.render_static(data)
        pixoo.draw_image(static_img)
        
        def animation_loop():
            frame_index = 0
            last_frame_hash = None
            while not pixoo.stop_animation:
                animated_frame = current_theme.animate_frame(data, frame_index, static_img)
                current_hash = hash(animated_frame.tobytes())
                if last_frame_hash != current_hash:
                    pixoo.draw_image(animated_frame)
                    last_frame_hash = current_hash
                frame_index += 1
                time.sleep(Config.ANIMATION_FRAME_DELAY)
        pixoo.start_animation(animation_loop)
        
        if theme == "flags":
            DataService.write_data(data)
        elif theme == "beer":
            BeerDataService.write_data(data)
        elif theme == "chatbot":
            ChatbotDataService.write_data({
                'background_color': data.get('background_color', '0,0,0'),
                'show_chat': data.get('show_chat', True),
                'tokens_used': get_tokens_used(),
                'country': data.get('country', 'Australia')
            })
            chatbot_data_cache = None
        else:
            return jsonify({"status": "error", "code": "INVALID_THEME"}), 400
            
        return jsonify(status="success", data=data)
    except Exception:
        return jsonify({"status": "error", "code": "KPI_UPDATE_FAILED"}), 500

@main_bp.route('/api/chat', methods=['POST'])
def handle_chat():
    global chatbot_data_cache
    chatbot_data_cache = None
    try:
        if 'tokens_used' not in session:
            session['tokens_used'] = 0
            ChatbotDataService.write_data({
                'background_color': '0,0,0',
                'show_chat': True,
                'tokens_used': 0,
                'country': 'Australia'
            })
            chatbot_data_cache = None

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

        total_chars = len(data.get('query', ''))
        chunks = []
        for chunk in dify_response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                chunk_text = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                chunks.append(chunk_text)
                total_chars += len(chunk_text)

        new_tokens = total_chars // 4
        session['tokens_used'] += new_tokens

        current_data = ChatbotDataService.read_data() or {}
        ChatbotDataService.write_data({
            'background_color': current_data.get('background_color', '0,0,0'),
            'show_chat': current_data.get('show_chat', True),
            'tokens_used': session['tokens_used'],
            'country': current_data.get('country', 'Australia')
        })
        chatbot_data_cache = None

        def generate():
            for chunk in chunks:
                yield chunk.encode('utf-8')
        return Response(
            stream_with_context(generate()),
            content_type=dify_response.headers.get('Content-Type', 'text/event-stream')
        )
    except requests.RequestException:
        return jsonify({"status": "error", "code": "DIFY_API_FAILED"}), 500
    except Exception:
        return jsonify({"status": "error", "code": "CHAT_FAILED"}), 500

@main_bp.route('/api/get-tokens', methods=['GET'])
def get_tokens():
    try:
        tokens_used = get_tokens_used()
        return jsonify({"tokens_used": tokens_used}), 200
    except Exception:
        return jsonify({"status": "error", "code": "TOKENS_FETCH_FAILED"}), 500

@main_bp.route('/api/pixoo-display', methods=['POST'])
def pixoo_display():
    global current_theme, chatbot_data_cache
    chatbot_data_cache = None
    data = request.json
    theme = data.get("theme")
    try:
        if theme not in THEME_MAP:
            return jsonify({"status": "error", "code": "INVALID_THEME"}), 400
        
        if theme == "chatbot":
            data["tokens_used"] = get_tokens_used()
        
        current_theme = THEME_MAP[theme]()
        static_img = current_theme.render_static(data)
        pixoo.draw_image(static_img)
        
        if theme == "chatbot" or data.get("show_chat", True):
            def animation_loop():
                frame_index = 0
                last_frame_hash = None
                while not pixoo.stop_animation:
                    animated_frame = current_theme.animate_frame(data, frame_index, static_img)
                    current_hash = hash(animated_frame.tobytes())
                    if last_frame_hash != current_hash:
                        pixoo.draw_image(animated_frame)
                        last_frame_hash = current_hash
                    frame_index += 1
                    time.sleep(Config.ANIMATION_FRAME_DELAY / 2 if data.get('state') == 'thinking' else Config.ANIMATION_FRAME_DELAY)
            pixoo.start_animation(animation_loop)
        
        return jsonify({"status": "success"})
    except Exception:
        return jsonify({"status": "error", "code": "DISPLAY_UPDATE_FAILED"}), 500
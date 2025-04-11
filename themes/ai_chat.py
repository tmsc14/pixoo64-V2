from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
from config import Config
import requests
import os
import json
import time
from threading import Thread
from services.pixoo_service import PixooService

class AIChatTheme(BaseTheme):
    def __init__(self):
        super().__init__()
        self.history = []  # Initialize history
        self.current_state = 'smiling'
        self.current_response = ""
        self.conversation_id = ""
        self.data = {}
        self.frame_index = 0
        self.last_activity = time.time()
        
        # Load animation states with fallbacks
        self.state_frames = {
            'smiling': self._load_frames("ai-bot/smiling", 1),
            'error': self._load_frames("ai-bot/error", 2),
            'sleeping': self._load_frames("ai-bot/sleeping", 2),
            'thinking': self._load_frames("ai-bot/thinking", 4)
        }

    def _load_frames(self, folder, frame_count):
        try:
            return self.load_frames(folder, "frame", frame_count, (24, 24))
        except Exception as e:
            print(f"Error loading {folder} frames: {e}")
            return [self._create_default_frame()]

    def _create_default_frame(self):
        img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 23, 23], outline="white")
        return img

    def get_name(self):
        return "ai_chat"

    def render_static(self, data):
        self.data = data
        bg_color = self.parse_color(data.get('background_color', '0,0,0'))
        img = Image.new("RGBA", (Config.PIXOO_SCREEN_SIZE, Config.PIXOO_SCREEN_SIZE), bg_color)
        self._draw_base_interface(img)
        return img

    def animate_frame(self, data, frame_index, static_bg):
        frame = static_bg.copy()
        draw = ImageDraw.Draw(frame)
        
        self._update_state()
        
        # Get valid frames
        frames = self.state_frames.get(self.current_state, [self._create_default_frame()])
        if not frames:
            frames = [self._create_default_frame()]
        
        current_frame = frames[self.frame_index % len(frames)]
        frame.paste(current_frame, (2, 2), current_frame)
        
        self._draw_conversation(draw)
        
        self.frame_index += 1
        return frame

    def _update_state(self):
        if time.time() - self.last_activity > 30:
            self.current_state = 'sleeping'
        elif self.current_state == 'error' and self.frame_index % 10 == 0:
            self.current_state = 'smiling'

    def _draw_base_interface(self, img):
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 28), (63, 63)], outline=(100, 100, 100))

    def _draw_conversation(self, draw):
        text_color = self.parse_color(self.data.get('text_color', '255,255,255'))
        messages = [self.current_response[i:i+15] for i in range(0, len(self.current_response), 15)][-4:]
        
        for i, msg in enumerate(messages):
            draw.text((2, 30 + i*8), msg, fill=text_color, font=self.font)

    def send_query(self, query):
        self.last_activity = time.time()
        self.current_state = 'thinking'
        self.current_response = ""
        Thread(target=self._process_query, args=(query,)).start()

    def _process_query(self, query):
        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('CHATBOT_API_KEY')}",
                "Content-Type": "application/json"
            }
            payload = {
                "query": query,
                "response_mode": "streaming",
                "user": "pixoo_user",
                "conversation_id": self.conversation_id,
                "inputs": {}
            }
            
            with requests.post("https://aibot.cloudstaff.io/v1/chat-messages",
                             headers=headers, 
                             json=payload, 
                             stream=True) as response:
                
                for line in response.iter_lines():
                    if line:
                        event_data = json.loads(line.decode().split("data: ")[1])
                        if event_data["event"] == "message":
                            self.current_response += event_data.get("answer", "")
                        elif event_data["event"] == "message_end":
                            self._handle_success_response(event_data)
                        elif event_data["event"] == "error":
                            self._handle_error(event_data.get("message", "Unknown error"))
                
        except Exception as e:
            self._handle_error(str(e))
        finally:
            self.last_activity = time.time()
            if self.current_state != 'error':
                self.current_state = 'smiling'

    def _handle_success_response(self, event_data):
        self.history.append(f"Bot: {self.current_response}")
        self.conversation_id = event_data["conversation_id"]
        self.current_response = ""
        PixooService().draw_image(self.render_static(self.data))

    def _handle_error(self, error_msg):
        self.current_state = 'error'
        self.current_response = f"Error: {error_msg}"
        self.frame_index = 0
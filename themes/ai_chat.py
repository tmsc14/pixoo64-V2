from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
import os
from views.fonts.pixel_font import PIXEL_FONT_3X5, draw_pixel_text
from utils.pixel_art import create_speech_bubble, create_pulse_node_frames, create_waveform_frames, get_pixel_icons
import textwrap
from datetime import datetime
import pytz

class AIChatTheme(BaseTheme):
    def __init__(self):
        super().__init__()
        self.name = "chatbot"
        self.error_frames = self.load_frames("ai-bot/error", 2, resize=(32, 32))
        self.sleeping_frames = self.load_frames("ai-bot/sleeping", 2, resize=(32, 32))
        self.smiling_frames = self.load_frames("ai-bot/smiling", 1, resize=(32, 32))
        self.thinking_frames = self.load_frames("ai-bot/thinking", 4, resize=(32, 32))
        self.fallback_frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        self.bubble_frame = create_speech_bubble()
        self.custom_frames = create_pulse_node_frames()
        self.waveform_frames = create_waveform_frames()

        # Load pixel art icons from pixel_art.py
        self.token_icon, self.cost_icon = get_pixel_icons()

    def load_frames(self, folder, num_frames, resize=None):
        frames = []
        for i in range(1, num_frames + 1):
            frame_path = os.path.join("views/img", folder, f"frame{i}.png")
            try:
                with Image.open(frame_path) as img:
                    img = img.copy()
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    if resize:
                        img = img.resize(resize, Image.LANCZOS)
                    frames.append(img)
            except FileNotFoundError:
                print(f"Frame not found: {frame_path}")
            except Exception as e:
                print(f"Error loading frame {frame_path}: {e}")
        return frames if frames else [self.fallback_frame]

    def get_name(self):
        return self.name

    def wrap_text(self, text, max_width):
        if not text:
            return [""]
        lines = textwrap.wrap(text, width=max_width, break_long_words=True)
        return lines if lines else [""]

    def get_current_time(self, country):
        timezone_map = {
            "Australia": "Australia/Sydney",
            "Philippines": "Asia/Manila",
            "United States": "America/New_York",
            "India": "Asia/Kolkata",
            "Colombia": "America/Bogota"
        }
        tz = timezone_map.get(country, "Australia/Sydney")
        return datetime.now(pytz.timezone(tz)).strftime("%H:%M")

    def calculate_token_cost(self, tokens_used, country):
        # Base rate: $0.00001 per token in USD
        rate_per_token_usd = 0.00001
        cost_usd = tokens_used * rate_per_token_usd
        currency_map = {
            "Australia": {"label": "AUD", "exchange_rate": 1.45},
            "Philippines": {"label": "PHP", "exchange_rate": 57.00},
            "United States": {"label": "USD", "exchange_rate": 1.00},
            "India": {"label": "INR", "exchange_rate": 84.00},
            "Colombia": {"label": "COP", "exchange_rate": 4200.00}
        }

        currency_info = currency_map.get(country, currency_map["Australia"])
        cost_local = cost_usd * currency_info["exchange_rate"]
        
        cost_local = round(cost_local, 2)
        
        cost_str = f"{cost_local:.2f}"
        
        full_str = f"{currency_info['label']} {cost_str}"
        if len(full_str) > 10:
            label_len = len(currency_info['label']) + 1  # +1 for space
            max_cost_len = 10 - label_len  # e.g., 10 - 4 = 6
            if len(cost_str) > max_cost_len:
                int_part = cost_str.split('.')[0]
                dec_part = cost_str.split('.')[1]
                max_int_len = max_cost_len - 3  # 3 chars for ".XX"
                if len(int_part) > max_int_len:
                    int_part = int_part[:max_int_len]
                cost_str = f"{int_part}.{dec_part}"
            full_str = f"{currency_info['label']} {cost_str}"
        
        return full_str

    def draw_pixel_icon(self, draw, x_start, y_start, icon, primary_color, highlight_color=None):
        """Draw a pixel art icon at the specified position."""
        for y, row in enumerate(icon):
            for x, pixel in enumerate(row):
                if pixel == 1:
                    draw.point((x_start + x, y_start + y), fill=primary_color)
                elif pixel == 7 and highlight_color:  # Highlight color for specific pixels
                    draw.point((x_start + x, y_start + y), fill=highlight_color)

    def render_static(self, data):
        state = data.get("state", "smiling")
        background_color = self.parse_color(data.get("background_color", "0,0,0"))
        img = Image.new("RGB", (64, 64), color=background_color)
        draw = ImageDraw.Draw(img)
        
        show_chat = data.get("show_chat", True)
        frames = {
            "error": self.error_frames,
            "sleeping": self.sleeping_frames,
            "smiling": self.smiling_frames,
            "thinking": self.thinking_frames
        }.get(state, self.smiling_frames)
        
        frame = frames[0] if frames else self.fallback_frame
        img.paste(frame, (16, 5), frame)  # Bot icon moved 3 pixels higher (from y=8 to y=5)

        if show_chat:
            if state in ("smiling", "thinking") and (data.get("bot_response") or data.get("message")):
                message = (data.get("bot_response") or data.get("message"))[:40]
                lines = self.wrap_text(message, 20)[:2]
                if self.bubble_frame:
                    img.paste(self.bubble_frame, (20, 40), self.bubble_frame)
                for i, line in enumerate(lines):
                    draw_pixel_text(draw, 22, 42 + i * 6, line, color=(0, 0, 0), spacing=1)
            elif state == "error":
                draw_pixel_text(draw, 22, 48, "ERR!", color=(0, 0, 0), spacing=1)
                if self.bubble_frame:
                    img.paste(self.bubble_frame, (20, 40), self.bubble_frame)
        else:
            tokens_used = data.get("tokens_used", 0)
            country = data.get("country", "Australia")
            current_time = self.get_current_time(country)
            token_cost = self.calculate_token_cost(tokens_used, country)
            
            time_width = len(current_time) * 4
            time_x = (64 - time_width) // 2
            draw_pixel_text(draw, time_x, 1, current_time, color=(255, 255, 255), spacing=1)
            
            waveform_frame = self.waveform_frames[0]
            waveform_width = waveform_frame.size[0]
            waveform_x = (64 - waveform_width) // 2
            img.paste(waveform_frame, (waveform_x, 34), waveform_frame)  # Moved 3 pixels higher (from y=37 to y=34)
            
            self.draw_pixel_icon(draw, 2, 47, self.token_icon, primary_color=(255, 215, 0), highlight_color=(255, 255, 255))
            draw_pixel_text(draw, 12, 47, str(tokens_used), color=(255, 255, 255), spacing=1)  # Moved to y=45 to match icon
            
            self.draw_pixel_icon(draw, 2, 53, self.cost_icon, primary_color=(255, 215, 0), highlight_color=(0, 255, 0))
            draw_pixel_text(draw, 12, 53, token_cost, color=(255, 255, 255), spacing=1)  # Moved to y=55 to match icon
        
        return img

    def animate_frame(self, data, frame_index, static_bg):
        background_color = self.parse_color(data.get("background_color", "0,0,0"))
        img = Image.new("RGB", (64, 64), color=background_color)
        draw = ImageDraw.Draw(img)
        
        state = data.get("state", "smiling")
        show_chat = data.get("show_chat", True)
        
        frames = {
            "error": self.error_frames,
            "sleeping": self.sleeping_frames,
            "smiling": self.smiling_frames,
            "thinking": self.thinking_frames
        }.get(state, self.smiling_frames)
        
        if not frames:
            img.paste(self.fallback_frame, (16, 5), self.fallback_frame)  # Moved 3 pixels higher (from y=8 to y=5)
        else:
            frame = frames[0] if state == "smiling" else frames[frame_index % len(frames)]
            if not show_chat and self.custom_frames and state == "thinking":
                frame = self.custom_frames[frame_index % len(self.custom_frames)]
            img.paste(frame, (16, 5), frame)  # Moved 3 pixels higher (from y=8 to y=5)
        
        if show_chat:
            if state in ("thinking", "smiling") and (data.get("message") or data.get("bot_response")):
                message = (data.get("message") or data.get("bot_response"))[:40]
                lines = self.wrap_text(message, 20)[:2]
                total_chars = sum(len(line) for line in lines)
                if total_chars > 20:
                    x_offset = 22 - ((frame_index * 3) % (total_chars * 4 + 40))
                else:
                    x_offset = 22
                if self.bubble_frame:
                    pulse = 255 if (frame_index // 4) % 2 == 0 else 200
                    bubble = self.bubble_frame.copy()
                    bubble_data = bubble.getdata()
                    new_data = [(r, g, b, a if a == 0 else min(a, pulse)) for r, g, b, a in bubble_data]
                    bubble.putdata(new_data)
                    img.paste(bubble, (20, 40), bubble)
                for i, line in enumerate(lines):
                    draw_pixel_text(draw, x_offset, 42 + i * 6, line, color=(0, 0, 0), spacing=1)
            elif state == "error":
                if (frame_index // 4) % 2 == 0:
                    draw_pixel_text(draw, 22, 48, "ERR!", color=(0, 0, 0), spacing=1)
                    if self.bubble_frame:
                        img.paste(self.bubble_frame, (20, 40), self.bubble_frame)
        else:
            tokens_used = data.get("tokens_used", 0)
            country = data.get("country", "Australia")
            current_time = self.get_current_time(country)
            token_cost = self.calculate_token_cost(tokens_used, country)
            
            time_width = len(current_time) * 4
            time_x = (68 - time_width) // 2
            draw_pixel_text(draw, time_x, 1, current_time, color=(255, 255, 255), spacing=1)
            
            waveform_frame = self.waveform_frames[frame_index % len(self.waveform_frames)]
            waveform_width = waveform_frame.size[0]
            waveform_x = (67 - waveform_width) // 2
            img.paste(waveform_frame, (waveform_x, 34), waveform_frame)  # Moved 3 pixels higher (from y=37 to y=34)
            
            self.draw_pixel_icon(draw, 2, 45, self.token_icon, primary_color=(255, 215, 0), highlight_color=(255, 255, 255))
            draw_pixel_text(draw, 12, 47, str(tokens_used), color=(255, 255, 255), spacing=1)  # Moved to y=45 to match icon
            
            self.draw_pixel_icon(draw, 2, 55, self.cost_icon, primary_color=(255, 215, 0), highlight_color=(0, 255, 0))
            draw_pixel_text(draw, 12, 57, token_cost, color=(255, 255, 255), spacing=1)  # Moved to y=55 to match icon
        
        return img
from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
import os
from views.fonts.pixel_font import PIXEL_FONT_3X5, draw_pixel_text
from utils.pixel_art import create_speech_bubble, create_pulse_node_frames, create_waveform_frames
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
        """Wrap text to fit within max_width characters, return list of lines."""
        if not text:
            return [""]
        lines = textwrap.wrap(text, width=max_width, break_long_words=True)
        return lines if lines else [""]

    def get_current_time(self, country):
        # Map countries to timezones
        timezone_map = {
            "Australia": "Australia/Sydney",
            "Philippines": "Asia/Manila",
            "United States": "America/New_York",
            "India": "Asia/Kolkata",
            "Colombia": "America/Bogota"
        }
        tz = timezone_map.get(country, "Australia/Sydney")
        return datetime.now(pytz.timezone(tz)).strftime("%H:%M")

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
        img.paste(frame, (16, 8), frame)  # Bot icon at (16, 8)
        
        if show_chat:
            if state in ("smiling", "thinking") and (data.get("bot_response") or data.get("message")):
                message = (data.get("bot_response") or data.get("message"))[:40]  # Limit to 40 chars
                lines = self.wrap_text(message, 20)[:2]  # Max 2 lines, 20 chars each
                if self.bubble_frame:
                    img.paste(self.bubble_frame, (20, 40), self.bubble_frame)  # Bubble at (20, 40)
                for i, line in enumerate(lines):
                    draw_pixel_text(draw, 22, 42 + i * 6, line, color=(0, 0, 0), spacing=1)  # Text inside bubble
            elif state == "error":
                draw_pixel_text(draw, 22, 48, "ERR!", color=(0, 0, 0), spacing=1)
                if self.bubble_frame:
                    img.paste(self.bubble_frame, (20, 40), self.bubble_frame)
        else:
            # Display tokens, cost, time, and waveform when chat is off
            tokens_used = data.get("tokens_used", 0)
            token_cost = data.get("token_cost", 0.0)
            country = data.get("country", "Australia")
            current_time = self.get_current_time(country)
            
            # Time above center (y=28, centered horizontally)
            time_width = len(current_time) * 4  # Approx 4 pixels per char with spacing=1
            time_x = (64 - time_width) // 2  # Center horizontally
            draw_pixel_text(draw, time_x, 28, current_time, color=(255, 255, 255), spacing=1)
            
            # Tokens and cost on the left at the bottom
            draw_pixel_text(draw, 2, 40, f"Tokens: {tokens_used}", color=(255, 255, 255), spacing=1)
            draw_pixel_text(draw, 2, 48, f"Cost: ${token_cost}", color=(255, 255, 255), spacing=1)
            
            # Centered waveform
            waveform_frame = self.waveform_frames[0]
            waveform_width = waveform_frame.size[0]  # Get actual width of waveform
            waveform_x = (64 - waveform_width) // 2  # Center horizontally
            img.paste(waveform_frame, (waveform_x, 40), waveform_frame)
        
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
            img.paste(self.fallback_frame, (16, 8), self.fallback_frame)
        else:
            frame = frames[0] if state == "smiling" else frames[frame_index % len(frames)]
            if not show_chat and self.custom_frames and state == "thinking":
                frame = self.custom_frames[frame_index % len(self.custom_frames)]
            img.paste(frame, (16, 8), frame)
        
        if show_chat:
            if state in ("thinking", "smiling") and (data.get("message") or data.get("bot_response")):
                message = (data.get("message") or data.get("bot_response"))[:40]
                lines = self.wrap_text(message, 20)[:2]
                total_chars = sum(len(line) for line in lines)
                if total_chars > 20:  # Scroll if message exceeds bubble width
                    x_offset = 22 - ((frame_index * 3) % (total_chars * 4 + 40))
                else:
                    x_offset = 22
                if self.bubble_frame:
                    # Pulse bubble brightness
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
            # Display tokens, cost, time, and waveform when chat is off
            tokens_used = data.get("tokens_used", 0)
            token_cost = data.get("token_cost", 0.0)
            country = data.get("country", "Australia")
            
            # Re-fetch the current time for real-time updates
            timezone_map = {
                "Australia": "Australia/Sydney",
                "Philippines": "Asia/Manila",
                "United States": "America/New_York",
                "India": "Asia/Kolkata",
                "Colombia": "America/Bogota"
            }
            tz = timezone_map.get(country, "Australia/Sydney")
            current_time = datetime.now(pytz.timezone(tz)).strftime("%H:%M")
            
            # Time above center (y=28, centered horizontally)
            time_width = len(current_time) * 4  # Approx 4 pixels per char with spacing=1
            time_x = (64 - time_width) // 2  # Center horizontally
            draw_pixel_text(draw, time_x, 1, current_time, color=(255, 255, 255), spacing=1)
            
            # Tokens and cost on the left at the bottom
            draw_pixel_text(draw, 2, 50, f"Tokens: {tokens_used}", color=(255, 255, 255), spacing=1)
            draw_pixel_text(draw, 2, 58, f"Cost: ${token_cost}", color=(255, 255, 255), spacing=1)
            
            # Centered waveform
            waveform_frame = self.waveform_frames[frame_index % len(self.waveform_frames)]
            waveform_width = waveform_frame.size[0]  # Get actual width of waveform
            waveform_x = (64 - waveform_width) // 2  # Center horizontally
            img.paste(waveform_frame, (waveform_x, 37), waveform_frame)
        
        return img
from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
import os
from views.fonts.pixel_font import PIXEL_FONT_3X5, draw_pixel_text

class AIChatTheme(BaseTheme):
    def __init__(self):
        super().__init__()
        self.name = "chatbot"
        self.error_frames = self.load_frames("ai-bot/error", 2, resize=(32, 32))
        self.sleeping_frames = self.load_frames("ai-bot/sleeping", 2, resize=(32, 32))
        self.smiling_frames = self.load_frames("ai-bot/smiling", 1, resize=(32, 32))
        self.thinking_frames = self.load_frames("ai-bot/thinking", 4, resize=(32, 32))
        self.fallback_frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))

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

    def render_static(self, data):
        state = data.get("state", "smiling")
        background_color = self.parse_color(data.get("background_color", "0,0,0"))
        img = Image.new("RGB", (64, 64), color=background_color)
        draw = ImageDraw.Draw(img)
        
        frames = {
            "error": self.error_frames,
            "sleeping": self.sleeping_frames,
            "smiling": self.smiling_frames,
            "thinking": self.thinking_frames
        }.get(state, self.smiling_frames)
        
        frame = frames[0] if frames else self.fallback_frame
        img.paste(frame, (16, 16), frame)
        
        # Send counter
        send_count = data.get("send_count", 0)
        if send_count > 0:
            draw_pixel_text(draw, 2, 2, f"S:{send_count}", color=(255, 255, 255))
        
        # Static text for smiling or error
        if state == "smiling" and data.get("bot_response"):
            draw_pixel_text(draw, 2, 48, data["bot_response"][:10], color=(255, 255, 255))
        elif state == "error":
            draw_pixel_text(draw, 2, 48, "ERR!", color=(255, 255, 255))
        
        return img

    def animate_frame(self, data, frame_index, static_bg):
        state = data.get("state", "smiling")
        background_color = self.parse_color(data.get("background_color", "0,0,0"))
        img = Image.new("RGB", (64, 64), color=background_color)
        draw = ImageDraw.Draw(img)
        
        frames = {
            "error": self.error_frames,
            "sleeping": self.sleeping_frames,
            "smiling": self.smiling_frames,
            "thinking": self.thinking_frames
        }.get(state, self.smiling_frames)
        
        if not frames:
            img.paste(self.fallback_frame, (16, 16), self.fallback_frame)
            return img
        
        frame = frames[0] if state == "smiling" else frames[frame_index % len(frames)]
        img.paste(frame, (16, 16), frame)
        
        # Send counter
        send_count = data.get("send_count", 0)
        if send_count > 0:
            draw_pixel_text(draw, 2, 2, f"S:{send_count}", color=(255, 255, 255))
        
        # Text animations
        if state == "thinking" and data.get("message"):
            message = data["message"][:15]
            text_width = len(message) * 4  # 3px char + 1px spacing
            x_offset = 64 - ((frame_index * 4) % (text_width + 64))
            draw_pixel_text(draw, x_offset, 48, message, color=(255, 255, 255))
        elif state == "smiling" and data.get("bot_response"):
            response = data["bot_response"][:10]
            slide_frames = 8  # Slide over 8 frames
            x_offset = min(2, 64 - (frame_index * 8) if frame_index < slide_frames else 2)
            draw_pixel_text(draw, x_offset, 48, response, color=(255, 255, 255))
        elif state == "error":
            # Blink ERR! (on/off every 4 frames)
            if (frame_index // 4) % 2 == 0:
                draw_pixel_text(draw, 2, 48, "ERR!", color=(255, 255, 255))
        
        return img
from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
import os

class AIChatTheme(BaseTheme):
    def __init__(self):
        super().__init__()
        self.name = "chatbot"
        # Load pixel art frames for each state
        self.error_frames = self.load_frames("ai-bot/error", 2, resize=(32, 32))
        self.sleeping_frames = self.load_frames("ai-bot/sleeping", 2, resize=(32, 32))
        self.smiling_frames = self.load_frames("ai-bot/smiling", 1, resize=(32, 32))
        self.thinking_frames = self.load_frames("ai-bot/thinking", 4, resize=(32, 32))
        # Fallback frame if any state is empty
        self.fallback_frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))

    def load_frames(self, folder, num_frames, resize=None):
        """Load frames with correct naming (frame1.png, frame2.png, etc.)."""
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
        """Render a static image for the chatbot state."""
        state = data.get("state", "smiling")
        background_color = self.parse_color(data.get("background_color", "0,0,0"))
        
        # Create 64x64 canvas
        img = Image.new("RGB", (64, 64), color=background_color)
        
        # Select frame based on state
        frames = {
            "error": self.error_frames,
            "sleeping": self.sleeping_frames,
            "smiling": self.smiling_frames,
            "thinking": self.thinking_frames
        }.get(state, self.smiling_frames)
        
        # Use first frame or fallback
        frame = frames[0] if frames else self.fallback_frame
        img.paste(frame, (16, 16), frame)  # Center 32x32 frame
        
        return img

    def animate_frame(self, data, frame_index, static_bg):
        """Render an animated frame based on state."""
        state = data.get("state", "smiling")
        background_color = self.parse_color(data.get("background_color", "0,0,0"))
        
        # Create canvas
        img = Image.new("RGB", (64, 64), color=background_color)
        
        # Select frames
        frames = {
            "error": self.error_frames,
            "sleeping": self.sleeping_frames,
            "smiling": self.smiling_frames,
            "thinking": self.thinking_frames
        }.get(state, self.smiling_frames)
        
        if not frames:
            img.paste(self.fallback_frame, (16, 16), self.fallback_frame)
            return img
        
        # Select frame (static for smiling, cycling for others)
        frame = frames[0] if state == "smiling" else frames[frame_index % len(frames)]
        img.paste(frame, (16, 16), frame)
        
        return img
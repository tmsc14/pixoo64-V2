from abc import ABC, abstractmethod
from PIL import Image, ImageDraw, ImageFont
import os

class BaseTheme(ABC):
    def __init__(self):
        self.font = self._load_font()

    def _load_font(self):
        try:
            return ImageFont.truetype("views/fonts/PressStart2P.ttf", 7.5)
        except IOError:
            try:
                return ImageFont.truetype("views/fonts/TinyUnicode.ttf", 6)
            except IOError:
                return ImageFont.load_default()

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def render_static(self, data):
        pass

    @abstractmethod
    def animate_frame(self, data, frame_index, static_bg):
        pass

    def load_frames(self, folder, prefix, num_frames, resize=(10,10)):
        frames = []
        for i in range(1, num_frames + 1):
            frame_path = os.path.join("views/img", folder, f"{prefix}-frame{i}.png")
            try:
                with Image.open(frame_path) as img:
                    img = img.copy()  # Ensure image is fully loaded
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    if resize:
                        img = img.resize(resize, Image.LANCZOS)
                    frames.append(img)
            except FileNotFoundError:
                print(f"Frame not found: {frame_path}")
        return frames

    @staticmethod
    def parse_color(color_str):
        return tuple(map(int, color_str.split(',')))

    @staticmethod
    def format_kpi(value):
        value = int(value)
        if value >= 1000:
            return f"{value / 1000:.1f}k" if value < 10000 else f"{value // 1000}k"
        return str(value)
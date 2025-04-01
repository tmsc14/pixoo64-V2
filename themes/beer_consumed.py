from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
from config import Config

class BeerConsumedTheme(BaseTheme):
    def get_name(self):
        return "beer_consumed"

    def render_static(self, data):
        bg_color = self.parse_color(data.get('background_color', '0,0,0'))
        text_color = self.parse_color(data.get('text_color', '255,255,255'))
        
        img = Image.new("RGBA", (Config.PIXOO_SCREEN_SIZE, Config.PIXOO_SCREEN_SIZE), bg_color)
        draw = ImageDraw.Draw(img)

        # Load full-size beer frames (64x64)
        beer_frames = self.load_frames("beer-frames", "bc", 5, resize=None)
        if beer_frames:
            total = int(data.get('beers_total_available', 1000))
            consumed = int(data.get('beers_consumed', 0))
            percentage = (consumed / total) * 100 if total > 0 else 0
            frame_index = self._get_frame_index(percentage)
            if frame_index < len(beer_frames):
                img.paste(beer_frames[frame_index], (0, 2), beer_frames[frame_index]) #MOVE ICON LOCATION
            else:
                print(f"Warning: No frame available for index {frame_index}")
        else:
            print("Warning: No beer frames loaded.")

        # Draw stats
        self._draw_stats(draw, data, text_color)
        return img

    def _get_frame_index(self, percentage):
        if percentage >= 100:
            return 0  # Frame 5 (100%)
        elif percentage >= 75:
            return 1  # Frame 4 (75%)
        elif percentage >= 50:
            return 2  # Frame 3 (50%)
        elif percentage >= 25:
            return 3  # Frame 2 (25%)
        else:
            return 4  # Frame 1 (0%)

    def _draw_stats(self, draw, data, text_color):
        location = data.get("location", "Unknown")
        total = self.format_kpi(data.get("beers_total_available", 1000))
        consumed = self.format_kpi(data.get("beers_consumed", 0))

        draw.text((2, 20), f"L:{location}", fill=text_color, font=self.font)
        draw.text((2, 29), f"T:{total}", fill=text_color, font=self.font)
        draw.text((2, 38), f"C:{consumed}", fill=text_color, font=self.font)

    def animate_frame(self, data, frame_index, static_bg):
        return static_bg
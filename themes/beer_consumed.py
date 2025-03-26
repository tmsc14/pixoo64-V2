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
            consumed = data.get('beers_week', 0)
            frame_index = min(4, max(0, consumed))  # Ensure index 0-4
            if frame_index < len(beer_frames):
                img.paste(beer_frames[frame_index], (0, 0), beer_frames[frame_index])
            else:
                print(f"Warning: No frame available for index {frame_index}")
        else:
            print("Warning: No beer frames loaded.")

        # Draw stats
        self._draw_stats(draw, data, text_color)
        return img
    
    def _draw_stats(self, draw, data, text_color):
        stats = [
            f'W:{data.get("beers_week", 0)}',
            f'M:{data.get("beers_month", 0)}',
            f'T:{data.get("beers_total", 0)}'
        ]
        
        # Draw stats at bottom
        for i, text in enumerate(stats):
            draw.text((2 + (i * 20), 54), text, fill=text_color, font=self.font)
            
    def animate_frame(self, data, frame_index, static_bg):
        return static_bg
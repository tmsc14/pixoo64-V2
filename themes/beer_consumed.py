from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
from config import Config
import pytz
from datetime import datetime
from views.fonts.pixel_font import draw_pixel_text

class BeerConsumedTheme(BaseTheme):
    def get_name(self):
        return "beer_consumed"

    def render_static(self, data):
        bg_color = self.parse_color(data.get('background_color', '0,0,0'))
        text_color = self.parse_color(data.get('text_color', '255,255,255'))
        
        img = Image.new("RGBA", (Config.PIXOO_SCREEN_SIZE, Config.PIXOO_SCREEN_SIZE), bg_color)
        draw = ImageDraw.Draw(img)

        # PH timezone
        ph_tz = pytz.timezone('Asia/Manila')
        current_time = datetime.now(ph_tz)
        is_friday = current_time.weekday() == 4  # 0=Monday, 4=Friday

        # Load beer frames
        beer_frames = self.load_frames("beer-frames", "bc", 5, resize=None)
        
        if beer_frames:
            resized_frames = []
            for frame in beer_frames:
                resized_frame = frame.resize((29, 29), Image.Resampling.LANCZOS)
                resized_frames.append(resized_frame)
            
            total = int(data.get('beers_total_available', 1000))
            consumed = int(data.get('beers_consumed', 0))
            percentage = (consumed / total) * 100 if total > 0 else 0
            frame_index = self._get_frame_index(percentage)
            
            beer_y = 11
            if is_friday:
                beer_x = 34
                # Draw "BEER FRIDAY" text
                draw_pixel_text(draw, 7, 21, "BEER", text_color)
                draw_pixel_text(draw, 4, 28, "FRIDAY", text_color)
            else:
                # Centered when no Friday text
                beer_x = (Config.PIXOO_SCREEN_SIZE - 23) // 2  # 17

            if frame_index < len(resized_frames):
                img.paste(resized_frames[frame_index], (beer_x, beer_y), resized_frames[frame_index])

        # Draw stats and location
        self._draw_stats(img, draw, data, text_color)
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

    def _draw_stats(self, img, draw, data, text_color):
        location = data.get("location", "Unknown")
        total = self.format_kpi(data.get("beers_total_available", 1000))
        consumed = self.format_kpi(data.get("beers_consumed", 0))

        # Load and draw icons
        try:
            # Beer opener icon (total)
            beer_opener = Image.open("views/img/beer-frames/icons/beer-opener.png") \
                .convert("RGBA") \
                .resize((19, 10), Image.Resampling.LANCZOS)
            img.paste(beer_opener, (2, 42), beer_opener)
            draw.text((23, 43), f"{total}", fill=text_color, font=self.font)

            # Empty bottle icon (consumed)
            empty_bottle = Image.open("views/img/beer-frames/icons/empty-bottle.png") \
                .convert("RGBA") \
                .resize((20, 9), Image.Resampling.LANCZOS)
            img.paste(empty_bottle, (2, 53), empty_bottle)
            draw.text((24, 54), f"{consumed}", fill=text_color, font=self.font)

        except Exception as e:
            print(f"Error loading icons: {e}")
            draw.text((1, 47), f"{total}", fill=text_color, font=self.font)
            draw.text((1, 57), f"{consumed}", fill=text_color, font=self.font)

        # Location text
        draw.text((1, 2), f"{location}", fill=text_color, font=self.font)

    def animate_frame(self, data, frame_index, static_bg):
        return static_bg
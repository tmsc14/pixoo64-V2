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
                # Draw "BEER FRIDAY"
                draw_pixel_text(draw, 7, 18, "BEER", text_color)
                draw_pixel_text(draw, 4, 25, "FRIDAY", text_color)
            else:
                beer_x = (Config.PIXOO_SCREEN_SIZE - 23) // 2  # Center on the top

            if frame_index < len(resized_frames):
                img.paste(resized_frames[frame_index], (beer_x, beer_y), resized_frames[frame_index])

        # Draw stats and location
        self._draw_stats(img, draw, data, text_color)
        return img

    def _get_frame_index(self, percentage):
        if percentage >= 100:
            return 0
        elif percentage >= 75: 
            return 1
        elif percentage >= 50:
            return 2
        elif percentage >= 25:
            return 3
        else:
            return 4

    def _draw_stats(self, img, draw, data, text_color):
        location = data.get("location", "Unknown")
        total = self.format_kpi(data.get('beers_total_available', 1000))
        consumed = self.format_kpi(data.get('beers_consumed', 0))

        try:
            beer_opener = Image.open("views/img/beer-frames/icons/beer-opener.png") \
                .convert("RGBA") \
                .resize((19, 10), Image.Resampling.LANCZOS)
            img.paste(beer_opener, (2, 42), beer_opener)
            draw.text((23, 43), f"{total}", fill=text_color, font=self.font)

            empty_bottle = Image.open("views/img/beer-frames/icons/empty-bottle.png") \
                .convert("RGBA") \
                .resize((20, 9), Image.Resampling.LANCZOS)
            img.paste(empty_bottle, (2, 53), empty_bottle)
            draw.text((24, 54), f"{consumed}", fill=text_color, font=self.font)

        except Exception as e:
            print(f"Error loading icons: {e}")
            draw.text((1, 47), f"{total}", fill=text_color, font=self.font)
            draw.text((1, 57), f"{consumed}", fill=text_color, font=self.font)

        draw.text((2, 2), f"{location}", fill=text_color, font=self.font)

    def animate_frame(self, data, frame_index, static_bg):
        animated = static_bg.copy()
        draw = ImageDraw.Draw(animated)
        
        # Define a selection of colors representing different beer tones
        beer_colors = [(255, 223, 186), (255, 193, 102), (255, 166, 77), (204, 140, 57), (179, 107, 0)]
        
        # Total rotating pixel positions
        perimeter = 256
        wave_length = len(beer_colors)
        wave_speed = 1
        
        for i in range(perimeter):
            color_index = (i + frame_index * wave_speed) % wave_length
            color = beer_colors[color_index]

            if i < 64:  # Top edge (left to right)
                x, y = i, 0
            elif i < 128:  # Right edge (top to bottom)
                x, y = 63, i - 64
            elif i < 192:  # Bottom edge (right to left)
                x, y = 191 - i, 63
            else:  # Left edge (bottom to top)
                x, y = 0, 255 - i

            draw.point((x, y), fill=color)

        # Draw real-time updating time
        self._draw_time(draw, data)
        return animated

    def _draw_time(self, draw, data):
        # Ensure 'country' key exists, or fall back if missing
        country = data.get("country", "Australia")  # Default to 'Australia' if missing
        tz_name = Config.COUNTRY_TIMEZONES.get(country, "Australia/Sydney")
        
        try:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            time_str = now.strftime("%H:%M")

            text_color = self.parse_color(data.get('text_color', '255,255,255'))

            # Draw the time for dynamic display update
            draw_pixel_text(draw, 6, 32, time_str, text_color)

        except Exception as e:
            print(f"Error in drawing time: {e}")
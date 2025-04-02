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
            
            if frame_index < len(resized_frames):
                img.paste(resized_frames[frame_index], (20, 11), resized_frames[frame_index])
            else:
                print(f"Warning: No frame available for index {frame_index}")
        else:
            print("Warning: No beer frames loaded.")

        # Draw stats with beer bottle icon
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

        # Load beer opener icon (for total)
        beer_opener_path = "views/img/beer-frames/icons/beer-opener.png"
        empty_bottle_path = "views/img/beer-frames/icons/empty-bottle.png"
        
        try:
            beer_opener = Image.open(beer_opener_path).convert("RGBA")
            beer_opener = beer_opener.resize((19, 10), Image.Resampling.LANCZOS) 
            icon_x = 1 
            icon_y = 42 

            img.paste(beer_opener, (icon_x, icon_y), beer_opener)
            
            text_x = icon_x + beer_opener.width + 2 
            draw.text((text_x, 43), f"{total}", fill=text_color, font=self.font) 

        except Exception as e:
            print(f"Error loading beer opener icon: {e}")
            draw.text((1, 47), f"{total}", fill=text_color, font=self.font)

        # Load empty bottle icon (for consumed)
        try:
            empty_bottle = Image.open(empty_bottle_path).convert("RGBA")
            empty_bottle = empty_bottle.resize((20, 9), Image.Resampling.LANCZOS) 
            bottle_x = 1 
            bottle_y = 53 

            img.paste(empty_bottle, (bottle_x, bottle_y), empty_bottle) 

            text_x = bottle_x + empty_bottle.width + 2 
            draw.text((text_x, 54), f"{consumed}", fill=text_color, font=self.font)

        except Exception as e:
            print(f"Error loading empty bottle icon: {e}")
            draw.text((1, 57), f"{consumed}", fill=text_color, font=self.font)

        draw.text((1, 2), f"{location}", fill=text_color, font=self.font)

    def animate_frame(self, data, frame_index, static_bg):
        return static_bg
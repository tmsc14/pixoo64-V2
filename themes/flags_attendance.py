from PIL import Image, ImageDraw
from datetime import datetime
from pytz import timezone
from themes.base_theme import BaseTheme
from config import Config

class FlagsAttendanceTheme(BaseTheme):
    def get_name(self):
        return "flags_attendance"

    def render_static(self, data):
        bg_color = self.parse_color(data['background_color'])
        line_color = self.parse_color(data['line_color'])
        text_color = self.parse_color(data['text_color'])

        img = Image.new("RGBA", (Config.PIXOO_SCREEN_SIZE, Config.PIXOO_SCREEN_SIZE), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw lines
        for y in range(0, 44):
            draw.point((46, y), fill=line_color)
        for x in range(0, 46):
            draw.point((x, 14), fill=line_color)
            draw.point((x, 29), fill=line_color)
        for x in range(0, 64):
            draw.point((x, 44), fill=line_color)

        # Draw static text
        draw.text((14, 4), self.format_kpi(data['green_flags']), fill=text_color, font=self.font)
        draw.text((14, 19), self.format_kpi(data['red_flags']), fill=text_color, font=self.font)
        draw.text((14, 34), self.format_kpi(data['attendance']), fill=text_color, font=self.font)
        
        right_x = 52
        draw.text((right_x, 3), "C", fill=text_color, font=self.font)
        draw.text((right_x, 13), "S", fill=text_color, font=self.font)
        draw.text((right_x, 24), "#", fill=text_color, font=self.font)
        draw.text((right_x, 34), "1", fill=text_color, font=self.font)

        return img

    def animate_frame(self, data, frame_index, static_bg):
        frame = static_bg.copy()
        draw = ImageDraw.Draw(frame)

        # Load animation frames
        gf = self.load_frames("green-flag-frames", "GF", 5)[frame_index % 5]
        rf = self.load_frames("red-flag-frames", "RF", 5)[frame_index % 5]
        af = self.load_frames("attendance-frames", "AF", 2)[frame_index % 2]

        # Paste animations
        frame.paste(gf, (2, 2), gf)
        frame.paste(rf, (2, 17), rf)
        frame.paste(af, (2, 32), af)

        # Draw time/date if enabled
        if data['showDateTime']:
            self._draw_time_date(draw, data, static_bg)

        return frame

    def _draw_time_date(self, draw, data, static_bg):
        tz = timezone(Config.COUNTRY_TIMEZONES.get(data["country"], "Australia/Sydney"))
        now = datetime.now(tz)
        country_code = {
            "Australia": "AU",
            "Philippines": "PH",
            "United States": "US",
            "India": "IN",
            "Colombia": "CO",
        }.get(data["country"], "AU")

        bg_color = self.parse_color(data['background_color'])
        text_color = self.parse_color(data['text_color'])

        # Draw country code
        draw.text((2, 46), country_code, fill=text_color, font=self.font)
        # Draw time
        draw.text((23, 46), now.strftime("%H:%M"), fill=text_color, font=self.font)
        # Draw date
        draw.text((0, 55), now.strftime("%d/%m/%y"), fill=text_color, font=self.font)
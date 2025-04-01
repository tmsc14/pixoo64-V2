from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
from config import Config
import random
import math
import time

class BeerConsumedTheme(BaseTheme):
    def __init__(self):
        super().__init__()
        self.particles = []
        self.last_update = time.time()
        # Initialize particles right away
        self._create_particles(20)
        
    def get_name(self):
        return "beer_consumed"
    
    def _create_particles(self, count=15):
        """Generate random particles around the beer glass area"""
        for _ in range(count):
            self.particles.append({
                'x': random.randint(10, 54),  # Centered around beer glass (18+34/2 = 35)
                'y': random.randint(0, 40),   # Centered around beer glass (11+34/2 = 28)
                'dx': random.uniform(-1, 1),
                'dy': random.uniform(-1.5, -0.5),  # Mostly upward movement
                'size': random.randint(1, 2),
                'life': random.randint(20, 40),
                'color': random.choice([
                    (255, 255, 255, 200),  # White
                    (255, 240, 150, 180),  # Yellowish
                    (180, 220, 255, 150)   # Bluish
                ])
            })
    
    def _update_particles(self):
        """Update particle positions and lifetimes"""
        # Update existing particles
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            
            # Some particles get smaller as they fade
            if random.random() < 0.3 and p['size'] > 1:
                p['size'] -= 0.2
        
        # Remove dead particles and add new ones
        self.particles = [p for p in self.particles if p['life'] > 0]
        if len(self.particles) < 10 or random.random() < 0.4:
            self._create_particles(random.randint(1, 3))

    def render_static(self, data):
        bg_color = self.parse_color(data.get('background_color', '0,0,0'))
        text_color = self.parse_color(data.get('text_color', '255,255,255'))
        
        img = Image.new("RGBA", (Config.PIXOO_SCREEN_SIZE, Config.PIXOO_SCREEN_SIZE), bg_color)
        draw = ImageDraw.Draw(img)

        # Update particles first
        self._update_particles()
        
        # Draw all active particles
        for p in self.particles:
            alpha = int(p['color'][3] * (p['life'] / 40))  # Fade out based on life
            draw.ellipse([
                (p['x']-p['size'], p['y']-p['size']),
                (p['x']+p['size'], p['y']+p['size'])
            ], fill=(*p['color'][:3], alpha))

        # Beer glass animation
        beer_frames = self.load_frames("beer-frames", "bc", 5, resize=None)
        if beer_frames:
            resized_frame = beer_frames[self._get_frame_index(
                (int(data.get('beers_consumed', 0)) / 
                 max(1, int(data.get('beers_total_available', 1000)))) * 100
            )].resize((34, 34), Image.Resampling.LANCZOS)
            img.paste(resized_frame, (18, 11), resized_frame)

        # Draw stats
        self._draw_stats(draw, data, text_color)
        return img

    def _get_frame_index(self, percentage):
        thresholds = [100, 75, 50, 25, 0]
        for i, threshold in enumerate(thresholds):
            if percentage >= threshold:
                return i
        return 4

    def _draw_stats(self, draw, data, text_color):
        draw.text((1, 2), data.get("location", "Unknown"), fill=text_color, font=self.font)
        draw.text((2, 46), f"T:{self.format_kpi(data.get('beers_total_available', 1000))}", 
                 fill=text_color, font=self.font)
        draw.text((2, 55), f"C:{self.format_kpi(data.get('beers_consumed', 0))}", 
                 fill=text_color, font=self.font)

    def animate_frame(self, data, frame_index, static_bg):
        return self.render_static(data)
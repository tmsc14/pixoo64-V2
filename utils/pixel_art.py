from PIL import Image, ImageDraw

def create_speech_bubble():
    """Create a 48x24 speech bubble with white fill, pixel art border, rounded corners, and 4x4 tail."""
    img = Image.new("RGBA", (52, 28), (0, 0, 0, 0))  # Transparent, includes tail
    draw = ImageDraw.Draw(img)
    
    # White fill for main bubble (48x24)
    fill_color = (255, 255, 255, 255)
    draw.rectangle(
        [(2, 2), (49, 25)],  # Inner area
        fill=fill_color
    )
    
    # Pixel art border (2px thick, with a pattern)
    border_color = (0, 0, 0, 255)
    pattern_color = (150, 150, 150, 255)  # Gray for border pattern
    # Top and bottom borders
    for x in range(2, 50):
        if (x % 4) in (0, 1):  # Alternating pattern
            draw.point((x, 1), fill=border_color)
            draw.point((x, 0), fill=border_color)
            draw.point((x, 26), fill=border_color)
            draw.point((x, 27), fill=border_color)
        else:
            draw.point((x, 1), fill=pattern_color)
            draw.point((x, 0), fill=pattern_color)
            draw.point((x, 26), fill=pattern_color)
            draw.point((x, 27), fill=pattern_color)
    # Left and right borders
    for y in range(2, 26):
        if (y % 4) in (0, 1):
            draw.point((1, y), fill=border_color)
            draw.point((0, y), fill=border_color)
            draw.point((50, y), fill=border_color)
            draw.point((51, y), fill=border_color)
        else:
            draw.point((1, y), fill=pattern_color)
            draw.point((0, y), fill=pattern_color)
            draw.point((50, y), fill=pattern_color)
            draw.point((51, y), fill=pattern_color)
    
    # Round corners with ellipses
    draw.ellipse([(0, 0), (4, 4)], fill=border_color)  # Top-left
    draw.ellipse([(47, 0), (51, 4)], fill=border_color)  # Top-right
    draw.ellipse([(0, 23), (4, 27)], fill=border_color)  # Bottom-left
    draw.ellipse([(47, 23), (51, 27)], fill=border_color)  # Bottom-right
    
    # Fill corners to match background
    draw.rectangle([(0, 0), (1, 1)], fill=(0, 0, 0, 0))  # Top-left
    draw.rectangle([(50, 0), (51, 1)], fill=(0, 0, 0, 0))  # Top-right
    draw.rectangle([(0, 26), (1, 27)], fill=(0, 0, 0, 0))  # Bottom-left
    draw.rectangle([(50, 26), (51, 27)], fill=(0, 0, 0, 0))  # Bottom-right
    
    # 4x4 tail (bottom-left, pointing up to bot)
    draw.polygon(
        [(2, 24), (2, 28), (6, 24)],  # Triangle pointing up
        fill=fill_color,
        outline=border_color
    )
    
    return img

def create_pulse_node_frames():
    """Create 3 frames of a 32x32 AI pulse node (circle, blue-cyan-white, glowing)."""
    frames = []
    sizes = [(8, (0, 0, 255, 255)), (12, (0, 255, 255, 255)), (16, (255, 255, 255, 255))]
    glow_color = (100, 100, 100, 128)
    
    for size, fill_color in sizes:
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = 16, 16
        radius = size // 2
        draw.ellipse(
            [(center_x - radius, center_y - radius), (center_x + radius - 1, center_y + radius - 1)],
            fill=fill_color,
            outline=(150, 150, 150, 255)
        )
        
        glow_radius = radius + 2
        draw.ellipse(
            [(center_x - glow_radius, center_y - glow_radius), (center_x + glow_radius - 1, center_y + glow_radius - 1)],
            fill=glow_color
        )
        
        frames.append(img)
    
    return frames

def create_waveform_frames():
    """Create 3 frames of a 16x8 waveform animation (blue signal wave)."""
    frames = []
    wave_heights = [
        [2, 4, 6, 4, 2],  # Frame 1: Small wave
        [3, 6, 3, 6, 3],  # Frame 2: Medium wave
        [4, 2, 6, 2, 4]   # Frame 3: Alternating wave
    ]
    wave_color = (0, 128, 255, 255)  # Bright blue
    
    for heights in wave_heights:
        img = Image.new("RGBA", (16, 8), (0, 0, 0, 0))  # Transparent 16x8 canvas
        draw = ImageDraw.Draw(img)
        
        # Draw vertical bars for the waveform, centered in 16px width
        total_width = len(heights) * 3 - 1  # 5 bars, 3px each (including spacing) = 14px
        start_x = (16 - total_width) // 2  # Center the waveform
        for x, height in enumerate(heights):
            x_pos = start_x + x * 3  # Space bars 3 pixels apart
            y_top = 4 - height // 2  # Center vertically
            y_bottom = 4 + height // 2
            draw.line([(x_pos, y_top), (x_pos, y_bottom)], fill=wave_color, width=1)
        
        frames.append(img)
    
    return frames

def get_pixel_icons():
    """Return the pixel art icons for token consumption and cost."""
    token_icon = [
        [0, 0, 1, 1, 1, 1, 0, 0],  # Coin top outline
        [0, 1, 1, 0, 0, 1, 1, 0],  # Coin sides
        [1, 1, 0, 7, 7, 0, 1, 1],  # Star top + coin
        [1, 1, 0, 7, 7, 7, 1, 1],  # Star middle + coin
        [1, 1, 0, 7, 7, 0, 1, 1],  # Star bottom + coin
        [1, 1, 0, 0, 0, 0, 1, 1],  # Coin sides
        [0, 1, 1, 0, 0, 1, 1, 0],  # Coin sides
        [0, 0, 1, 1, 1, 1, 0, 0],  # Coin bottom outline
    ]

    cost_icon = [
        [0, 0, 0, 7, 7, 0, 0, 0],  # Dollar sign top
        [0, 0, 7, 7, 7, 7, 0, 0],  # Dollar crossbar
        [0, 0, 0, 7, 7, 0, 0, 0],  # Dollar middle
        [0, 0, 7, 7, 7, 7, 0, 0],  # Dollar crossbar
        [0, 0, 0, 7, 7, 0, 0, 0],  # Dollar bottom
        [0, 1, 1, 1, 1, 1, 1, 0],  # Top coin outline
        [0, 1, 1, 1, 1, 1, 1, 0],  # Middle coin overlap
        [0, 0, 1, 1, 1, 1, 0, 0],  # Bottom coin outline
    ]

    return token_icon, cost_icon

def create_chat_stars():
    """Create 3 frames of a 4x4 star animation for chat bubble decoration."""
    frames = []
    star_patterns = [
        [
            [0, 0, 1, 0],  # Frame 1: Small star
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 0],
        ],
        [
            [0, 1, 1, 0],  # Frame 2: Medium star
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [0, 1, 1, 0],
        ],
        [
            [1, 0, 0, 1],  # Frame 3: Rotated star
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1],
        ],
    ]
    star_color = (255, 215, 0, 255)  # Yellow
    
    for pattern in star_patterns:
        img = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for y, row in enumerate(pattern):
            for x, pixel in enumerate(row):
                if pixel == 1:
                    draw.point((x, y), fill=star_color)
        frames.append(img)
    
    return frames
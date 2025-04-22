from PIL import Image, ImageDraw

def create_speech_bubble():
    """Create a 40x20 speech bubble with white fill, 2px black outline, rounded corners, and 4x4 tail."""
    img = Image.new("RGBA", (44, 24), (0, 0, 0, 0))  # Transparent, includes tail
    draw = ImageDraw.Draw(img)
    
    # White fill for main bubble (40x20)
    fill_color = (255, 255, 255, 255)
    draw.rectangle(
        [(2, 2), (41, 21)],  # Inner area
        fill=fill_color
    )
    
    # Black 2px outline, rounded rectangle
    outline_color = (0, 0, 0, 255)
    draw.rectangle(
        [(2, 2), (41, 21)],
        outline=outline_color,
        width=2
    )
    
    # Round corners with ellipses
    draw.ellipse([(0, 0), (4, 4)], fill=outline_color)  # Top-left
    draw.ellipse([(39, 0), (43, 4)], fill=outline_color)  # Top-right
    draw.ellipse([(0, 19), (4, 23)], fill=outline_color)  # Bottom-left
    draw.ellipse([(39, 19), (43, 23)], fill=outline_color)  # Bottom-right
    
    # Fill corners to match background
    draw.rectangle([(0, 0), (1, 1)], fill=(0, 0, 0, 0))  # Top-left
    draw.rectangle([(42, 0), (43, 1)], fill=(0, 0, 0, 0))  # Top-right
    draw.rectangle([(0, 22), (1, 23)], fill=(0, 0, 0, 0))  # Bottom-left
    draw.rectangle([(42, 22), (43, 23)], fill=(0, 0, 0, 0))  # Bottom-right
    
    # 4x4 tail (bottom-left, pointing up to bot)
    draw.polygon(
        [(2, 20), (2, 24), (6, 20)],  # Triangle pointing up
        fill=fill_color,
        outline=outline_color
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
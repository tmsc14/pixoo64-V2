from PIL import Image, ImageDraw

def create_speech_bubble():
    """Create a 48x10 speech bubble with white 2px outline, rounded corners, transparent center."""
    img = Image.new("RGBA", (48, 10), (0, 0, 0, 0))  # Transparent
    draw = ImageDraw.Draw(img)
    
    # White 2px outline, rounded rectangle
    outline_color = (255, 255, 255, 255)
    draw.rectangle(
        [(2, 2), (45, 7)],  # Inner area (leave 2px border)
        outline=outline_color,
        width=2
    )
    # Round corners (approximate with small ellipses)
    draw.ellipse([(0, 0), (4, 4)], fill=outline_color)  # Top-left
    draw.ellipse([(43, 0), (47, 4)], fill=outline_color)  # Top-right
    draw.ellipse([(0, 5), (4, 9)], fill=outline_color)  # Bottom-left
    draw.ellipse([(43, 5), (47, 9)], fill=outline_color)  # Bottom-right
    
    return img

def create_pulse_node_frames():
    """Create 3 frames of a 32x32 AI pulse node (circle, blue-cyan-white, glowing)."""
    frames = []
    sizes = [(8, (0, 0, 255, 255)), (12, (0, 255, 255, 255)), (16, (255, 255, 255, 255))]  # Size, color
    glow_color = (100, 100, 100, 128)  # Faint gray glow
    
    for size, fill_color in sizes:
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))  # Transparent
        draw = ImageDraw.Draw(img)
        
        # Center circle
        center_x, center_y = 16, 16
        radius = size // 2
        draw.ellipse(
            [(center_x - radius, center_y - radius), (center_x + radius - 1, center_y + radius - 1)],
            fill=fill_color,
            outline=(150, 150, 150, 255)  # Subtle hexagon-like edge
        )
        
        # Glow (larger, faint ellipse)
        glow_radius = radius + 2
        draw.ellipse(
            [(center_x - glow_radius, center_y - glow_radius), (center_x + glow_radius - 1, center_y + glow_radius - 1)],
            fill=glow_color
        )
        
        frames.append(img)
    
    return frames
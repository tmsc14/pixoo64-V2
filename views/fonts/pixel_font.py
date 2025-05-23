from PIL import ImageDraw

PIXEL_FONT_3X5 = {
    # Letters
    'A': [[0,1,0], [1,0,1], [1,1,1], [1,0,1], [1,0,1]],
    'B': [[1,1,0], [1,0,1], [1,1,0], [1,0,1], [1,1,0]],
    'C': [[0,1,1], [1,0,0], [1,0,0], [1,0,0], [0,1,1]],
    'D': [[1,1,0], [1,0,1], [1,0,1], [1,0,1], [1,1,0]],
    'E': [[1,1,1], [1,0,0], [1,1,1], [1,0,0], [1,1,1]],
    'F': [[1,1,1], [1,0,0], [1,1,1], [1,0,0], [1,0,0]],
    'G': [[0,1,1], [1,0,0], [1,0,1], [1,0,1], [0,1,1]],
    'H': [[1,0,1], [1,0,1], [1,1,1], [1,0,1], [1,0,1]],
    'I': [[1,1,1], [0,1,0], [0,1,0], [0,1,0], [1,1,1]],
    'J': [[1,1,1], [0,1,0], [0,1,0], [1,1,0], [0,1,0]],
    'K': [[1,0,1], [1,1,0], [1,0,0], [1,1,0], [1,0,1]],
    'L': [[1,0,0], [1,0,0], [1,0,0], [1,0,0], [1,1,1]],
    'M': [[1,0,1], [1,1,1], [1,1,1], [1,0,1], [1,0,1]],
    'N': [[1,0,1], [1,1,1], [1,1,1], [1,1,1], [1,0,1]],
    'O': [[0,1,0], [1,0,1], [1,0,1], [1,0,1], [0,1,0]],
    'P': [[1,1,0], [1,0,1], [1,1,0], [1,0,0], [1,0,0]],
    'Q': [[0,1,0], [1,0,1], [1,0,1], [1,1,1], [0,1,1]],
    'R': [[1,1,0], [1,0,1], [1,1,0], [1,0,1], [1,0,1]],
    'S': [[0,1,1], [1,0,0], [0,1,0], [0,0,1], [1,1,0]],
    'T': [[1,1,1], [0,1,0], [0,1,0], [0,1,0], [0,1,0]],
    'U': [[1,0,1], [1,0,1], [1,0,1], [1,0,1], [1,1,1]],
    'V': [[1,0,1], [1,0,1], [1,0,1], [1,0,1], [0,1,0]],
    'W': [[1,0,1], [1,0,1], [1,1,1], [1,1,1], [1,0,1]],
    'X': [[1,0,1], [1,0,1], [0,1,0], [1,0,1], [1,0,1]],
    'Y': [[1,0,1], [1,0,1], [0,1,0], [0,1,0], [0,1,0]],
    'Z': [[1,1,1], [0,0,1], [0,1,0], [1,0,0], [1,1,1]],
    
    # Numbers
    '0': [[0,1,0], [1,0,1], [1,0,1], [1,0,1], [0,1,0]],
    '1': [[0,1,0], [1,1,0], [0,1,0], [0,1,0], [1,1,1]],
    '2': [[1,1,0], [0,0,1], [0,1,0], [1,0,0], [1,1,1]],
    '3': [[1,1,0], [0,0,1], [0,1,0], [0,0,1], [1,1,0]],
    '4': [[1,0,1], [1,0,1], [1,1,1], [0,0,1], [0,0,1]],
    '5': [[1,1,1], [1,0,0], [1,1,0], [0,0,1], [1,1,0]],
    '6': [[0,1,1], [1,0,0], [1,1,0], [1,0,1], [0,1,0]],
    '7': [[1,1,1], [0,0,1], [0,1,0], [1,0,0], [1,0,0]],
    '8': [[0,1,0], [1,0,1], [0,1,0], [1,0,1], [0,1,0]],
    '9': [[0,1,0], [1,0,1], [0,1,1], [0,0,1], [1,1,0]],
    
    # Special Characters
    '!': [[1], [1], [1], [0], [1]],
    '?': [[1,1,0], [0,0,1], [0,1,0], [0,0,0], [0,1,0]],
    '#': [[0,1,0], [1,1,1], [0,1,0], [1,1,1], [0,1,0]],
    '%': [[1,0,0], [0,0,1], [0,1,0], [1,0,0], [0,0,1]],
    '&': [[0,1,0], [1,0,1], [0,1,0], [1,0,1], [0,1,1]],
    '(': [[0,1], [1,0], [1,0], [1,0], [0,1]],
    ')': [[1,0], [0,1], [0,1], [0,1], [1,0]],
    '-': [[0,0,0], [0,0,0], [1,1,1], [0,0,0], [0,0,0]],
    '_': [[0,0,0], [0,0,0], [0,0,0], [0,0,0], [1,1,1]],
    '+': [[0,0,0], [0,1,0], [1,1,1], [0,1,0], [0,0,0]],
    '=': [[0,0,0], [1,1,1], [0,0,0], [1,1,1], [0,0,0]],
    ':': [[0], [1], [0], [1], [0]],
    ' ': [[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0]],
    '.': [[0], [0], [0], [0], [1]],  # Decimal point: single pixel at bottom
    ',': [[0], [0], [0], [1], [1]],  # Comma: pixel at bottom with a small tail
}

def draw_pixel_text(draw: ImageDraw.Draw, x_start: int, y_start: int, 
                   text: str, color: tuple, spacing: int = 1):
    """
    Draws pixel text using the 3x5 font
    - draw: ImageDraw instance
    - x_start: Starting X position
    - y_start: Starting Y position
    - text: Text to draw (uppercase letters, numbers, and supported symbols)
    - color: RGB tuple for text color
    - spacing: Pixels between characters (default 1)
    """
    x_offset = 0
    for char in text.upper():
        if char in PIXEL_FONT_3X5:
            char_def = PIXEL_FONT_3X5[char]
            for y, row in enumerate(char_def):
                for x, pixel in enumerate(row):
                    if pixel:
                        draw.point(
                            (x_start + x + x_offset, y_start + y),
                            fill=color
                        )
            # Calculate width based on character definition
            char_width = len(char_def[0]) if char_def else 0
            x_offset += char_width + spacing
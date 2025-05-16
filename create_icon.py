from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    # Create a 256x256 image with a white background
    size = 256
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a blue circle
    circle_color = (59, 130, 246)  # COLOR_PRIMARY from app_gui.py
    draw.ellipse([20, 20, size-20, size-20], fill=circle_color)
    
    # Add text "CJ" in white
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "CJ"
    text_color = (255, 255, 255)
    
    # Calculate text position to center it
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Save as PNG and ICO
    image.save('code_journal_icon.png')
    image.save('code_journal_icon.ico', format='ICO')
    print("Icon created successfully!")

if __name__ == "__main__":
    create_app_icon() 
import os
from PIL import Image, ImageDraw, ImageFont # pylint: disable=import-error

def create_icon(text):
    '''create a simple icon'''
    SIZE = 256
    # Create a 256x256 transparent canvas (recommended for .ico)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle background
    rect_margin = 30
    draw.rounded_rectangle((rect_margin,
                           rect_margin,
                           SIZE - rect_margin,
                           SIZE - rect_margin),
                           radius=40,
                           fill="blue")

    font = ImageFont.truetype("segoeuib.ttf", 120)
    #text_w, text_h = draw.textsize(text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Center the text
    x = (SIZE - text_w) / 2
    y = (SIZE - text_h) / 2-30  # slight upward adjustment for optical centering

    # Draw the text
    draw.text((x, y), text, fill="white", font=font)

    #path = os.path.dirname(os.path.abspath(__file__))
    #icon_file = os.path.join(path, f"{text}.ico")
    # Save as .ico with multiple sizes
    img.save(f"{text}.ico", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])

def main():
    create_icon("CC")
    create_icon("VP")

if __name__ == "__main__":
    main()
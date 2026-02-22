"""Generate a crypto-themed icon for C-BOM."""
from PIL import Image, ImageDraw, ImageFont
import os

def create_cbom_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Dark background circle
        margin = size // 10
        draw.ellipse([margin, margin, size - margin, size - margin],
                     fill=(15, 30, 60, 255))

        # Outer ring
        ring = size // 12
        draw.ellipse([margin, margin, size - margin, size - margin],
                     outline=(0, 180, 255, 255), width=max(1, ring // 2))

        # Lock body
        lw = size * 0.28
        lh = size * 0.22
        lx = (size - lw) / 2
        ly = size * 0.5
        draw.rectangle([lx, ly, lx + lw, ly + lh],
                       fill=(0, 180, 255, 255))

        # Lock shackle (arc)
        sw = lw * 0.55
        sx = (size - sw) / 2
        sy = ly - lh * 0.9
        draw.arc([sx, sy, sx + sw, sy + lh * 1.2],
                 start=200, end=340,
                 fill=(0, 220, 255, 255), width=max(1, size // 20))

        # Keyhole dot
        kx = size / 2
        ky = ly + lh * 0.45
        kr = max(1, size // 22)
        draw.ellipse([kx - kr, ky - kr, kx + kr, ky + kr],
                     fill=(15, 30, 60, 255))

        images.append(img)

    out_path = os.path.join(os.path.dirname(__file__), "cbom.ico")
    images[0].save(out_path, format="ICO",
                   sizes=[(s, s) for s in sizes],
                   append_images=images[1:])
    print(f"Icon saved to: {out_path}")

if __name__ == "__main__":
    create_cbom_icon()

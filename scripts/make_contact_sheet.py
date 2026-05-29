"""Create a contact sheet for generated images."""

import argparse
from pathlib import Path


def make_contact_sheet(image_dir, output_path, cols=5, thumb_size=256):
    try:
        from PIL import Image, ImageDraw
    except Exception as exc:
        raise RuntimeError(f"Pillow is required to create contact sheets. Original error: {exc}") from exc

    image_dir = Path(image_dir)
    output_path = Path(output_path)
    paths = sorted(
        path
        for path in image_dir.iterdir()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".ppm", ".webp"}
    )
    if not paths:
        raise RuntimeError(f"No images found in {image_dir}")

    cols = max(1, int(cols))
    rows = (len(paths) + cols - 1) // cols
    label_h = 34
    canvas = Image.new("RGB", (cols * thumb_size, rows * (thumb_size + label_h)), "white")
    draw = ImageDraw.Draw(canvas)

    for idx, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_size, thumb_size))
        x = (idx % cols) * thumb_size
        y = (idx // cols) * (thumb_size + label_h)
        paste_x = x + (thumb_size - image.width) // 2
        paste_y = y + (thumb_size - image.height) // 2
        canvas.paste(image, (paste_x, paste_y))
        draw.text((x + 4, y + thumb_size + 4), path.stem[:32], fill=(0, 0, 0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=92)
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--thumb-size", type=int, default=256)
    args = parser.parse_args()
    output = make_contact_sheet(args.image_dir, args.output, args.cols, args.thumb_size)
    print(f"Wrote contact sheet: {output}")


if __name__ == "__main__":
    main()

"""Convert the official logo into platform icon formats for packaging."""

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "guihguih_cyber" / "assets" / "logo.png"
OUTPUT = ROOT / "build" / "branding"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as source:
        logo = source.convert("RGBA")

    large = ImageOps.pad(logo, (1024, 1024), Image.Resampling.LANCZOS)
    small = ImageOps.pad(logo, (256, 256), Image.Resampling.LANCZOS)
    large.save(OUTPUT / "app.icns")
    small.save(OUTPUT / "app.ico")
    small.save(OUTPUT / "guihguih-cyber.png")


if __name__ == "__main__":
    main()

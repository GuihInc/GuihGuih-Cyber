"""Generate a small original RGBA application icon using only Python stdlib."""

import struct
import sys
import zlib
from pathlib import Path


SIZE = 256


def inside_polygon(x, y, points):
    inside = False
    j = len(points) - 1
    for i, (xi, yi) in enumerate(points):
        xj, yj = points[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def png_chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)


def main(output):
    shield = [(128, 25), (205, 55), (194, 151), (128, 221), (62, 151), (51, 55)]
    inner = [(128, 50), (181, 70), (173, 143), (128, 192), (83, 143), (75, 70)]
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)
        for x in range(SIZE):
            if inside_polygon(x, y, shield):
                color = (120, 231, 176, 255)
            elif inside_polygon(x, y, inner):
                color = (8, 15, 24, 255)
            elif 100 < x < 115 and 118 < y < 132 or 108 < x < 157 and abs((y - 150) - (x - 125) * .7) < 7:
                color = (120, 231, 176, 255)
            else:
                color = (8, 15, 24, 255)
            raw.extend(color)
    header = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header) + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + png_chunk(b"IEND", b"")
    Path(output).write_bytes(data)


if __name__ == "__main__":
    main(sys.argv[1])


from __future__ import annotations

import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BG = (24, 26, 31, 255)
ACCENT = (15, 107, 104, 255)
RUST = (143, 63, 40, 255)
PAPER = (247, 245, 239, 255)
LINE = (216, 221, 229, 255)
MARK = (245, 211, 108, 255)
DARK = (16, 19, 23, 255)


def point_in_poly(x: float, y: float, points: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(points) - 1
    for i, (xi, yi) in enumerate(points):
        xj, yj = points[j]
        if (yi > y) != (yj > y):
            x_cross = (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi
            if x < x_cross:
                inside = not inside
        j = i
    return inside


def draw_poly(pixels: list[list[tuple[int, int, int, int]]], points: list[tuple[float, float]], color: tuple[int, int, int, int]) -> None:
    size = len(pixels)
    scaled = [(x * size / 64, y * size / 64) for x, y in points]
    min_x = max(0, int(min(x for x, _ in scaled)))
    max_x = min(size - 1, int(max(x for x, _ in scaled)) + 1)
    min_y = max(0, int(min(y for _, y in scaled)))
    max_y = min(size - 1, int(max(y for _, y in scaled)) + 1)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if point_in_poly(x + 0.5, y + 0.5, scaled):
                pixels[y][x] = color


def draw_rect(pixels: list[list[tuple[int, int, int, int]]], x0: float, y0: float, x1: float, y1: float, color: tuple[int, int, int, int]) -> None:
    draw_poly(pixels, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color)


def draw_circle(pixels: list[list[tuple[int, int, int, int]]], cx: float, cy: float, r: float, color: tuple[int, int, int, int]) -> None:
    size = len(pixels)
    cx *= size / 64
    cy *= size / 64
    r *= size / 64
    min_x = max(0, int(cx - r))
    max_x = min(size - 1, int(cx + r) + 1)
    min_y = max(0, int(cy - r))
    max_y = min(size - 1, int(cy + r) + 1)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r**2:
                pixels[y][x] = color


def make_pixels(size: int) -> list[list[tuple[int, int, int, int]]]:
    pixels = [[BG for _ in range(size)] for _ in range(size)]
    draw_poly(pixels, [(7, 39), (48, 39), (56, 47), (14, 47), (7, 43)], ACCENT)
    draw_poly(pixels, [(12, 33), (43, 33), (48, 39), (13, 39)], LINE)
    draw_poly(pixels, [(25, 20), (40, 20), (49, 33), (22, 33)], RUST)
    draw_poly(pixels, [(31, 14), (47, 14), (54, 20), (35, 20)], MARK)
    draw_poly(pixels, [(5, 37), (17, 32), (24, 32), (17, 40), (6, 40)], MARK)
    draw_poly(pixels, [(15, 47), (54, 47), (49, 53), (20, 53)], DARK)
    for cx in (22, 33, 44):
        draw_circle(pixels, cx, 47, 3, PAPER)

    # Pixel-friendly "MK" hint. Keep it blocky so it survives 16px.
    draw_rect(pixels, 26, 27, 29, 35, DARK)
    draw_rect(pixels, 35, 27, 38, 35, DARK)
    draw_poly(pixels, [(29, 27), (32, 31), (35, 27), (35, 32), (32, 35), (29, 32)], DARK)
    draw_rect(pixels, 41, 27, 44, 35, DARK)
    draw_poly(pixels, [(44, 31), (49, 27), (53, 27), (48, 31), (53, 35), (49, 35)], DARK)
    return pixels


def dib_from_pixels(pixels: list[list[tuple[int, int, int, int]]]) -> bytes:
    size = len(pixels)
    header = struct.pack(
        "<IIIHHIIIIII",
        40,
        size,
        size * 2,
        1,
        32,
        0,
        size * size * 4,
        2835,
        2835,
        0,
        0,
    )
    rows = []
    for row in reversed(pixels):
        rows.append(b"".join(struct.pack("<BBBB", b, g, r, a) for r, g, b, a in row))
    and_mask_stride = ((size + 31) // 32) * 4
    return header + b"".join(rows) + (b"\x00" * and_mask_stride * size)


def main() -> None:
    frames = []
    for size in (16, 32, 48, 64):
        data = dib_from_pixels(make_pixels(size))
        frames.append((size, data))

    header_size = 6 + len(frames) * 16
    offset = header_size
    directory = []
    payload = []
    for size, data in frames:
        directory.append(struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(data), offset))
        payload.append(data)
        offset += len(data)

    ico = struct.pack("<HHH", 0, 1, len(frames)) + b"".join(directory) + b"".join(payload)
    (ROOT / "favicon.ico").write_bytes(ico)


if __name__ == "__main__":
    main()

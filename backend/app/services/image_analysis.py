from __future__ import annotations

from collections import deque
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_DIMENSION = 640
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageAnalysisError(ValueError):
    """Raised when an uploaded image cannot be safely analyzed."""


def _foreground_regions(image: Image.Image) -> list[dict[str, int]]:
    width, height = image.size
    pixels = list(image.getdata())

    border = []
    for y in range(height):
        for x in range(width):
            if x < 2 or y < 2 or x >= width - 2 or y >= height - 2:
                border.append(pixels[y * width + x])

    background = tuple(
        sum(pixel[channel] for pixel in border) // max(len(border), 1)
        for channel in range(3)
    )
    threshold = 42
    mask = bytearray(width * height)

    for index, pixel in enumerate(pixels):
        distance = sum((pixel[channel] - background[channel]) ** 2 for channel in range(3)) ** 0.5
        if distance >= threshold:
            mask[index] = 1

    visited = bytearray(width * height)
    minimum_area = max(12, int(width * height * 0.001))
    regions: list[dict[str, int]] = []

    for start in range(width * height):
        if not mask[start] or visited[start]:
            continue

        queue = deque([start])
        visited[start] = 1
        area = 0
        min_x = width
        min_y = height
        max_x = 0
        max_y = 0

        while queue:
            current = queue.popleft()
            x = current % width
            y = current // width
            area += 1
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            for next_x, next_y in (
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1),
            ):
                if 0 <= next_x < width and 0 <= next_y < height:
                    next_index = next_y * width + next_x
                    if mask[next_index] and not visited[next_index]:
                        visited[next_index] = 1
                        queue.append(next_index)

        if area >= minimum_area:
            regions.append(
                {
                    "x": min_x,
                    "y": min_y,
                    "width": max_x - min_x + 1,
                    "height": max_y - min_y + 1,
                    "area": area,
                }
            )

    regions.sort(key=lambda region: region["area"], reverse=True)
    return regions[:100]


def analyze_image_bytes(image_bytes: bytes, filename: str | None = None) -> dict[str, Any]:
    if not image_bytes:
        raise ImageAnalysisError("No image data was supplied.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ImageAnalysisError("Image exceeds the 5 MB size limit.")

    try:
        with Image.open(BytesIO(image_bytes)) as source:
            image_format = source.format
            if image_format not in ALLOWED_FORMATS:
                raise ImageAnalysisError("Unsupported image type. Use JPEG, PNG, or WEBP.")
            source.verify()

        with Image.open(BytesIO(image_bytes)) as source:
            original_width, original_height = source.size
            image = source.convert("RGB")
            image.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))
            regions = _foreground_regions(image)
    except ImageAnalysisError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ImageAnalysisError("The uploaded file is not a valid readable image.") from exc

    region_count = len(regions)
    quality = "low" if region_count == 0 else "approximate"
    confidence = 0.25 if region_count == 0 else 0.55

    return {
        "method": "classical_cv_foreground_regions",
        "analysis_quality": quality,
        "confidence": confidence,
        "filename": Path(filename).name if filename else None,
        "format": image_format,
        "image_dimensions": {
            "width": original_width,
            "height": original_height,
        },
        "processed_dimensions": {
            "width": image.width,
            "height": image.height,
        },
        "approximate_detected_litter_count": region_count,
        "detected_regions": regions,
        "evidence": (
            "Count is an approximate number of visually distinct foreground "
            "regions relative to the image border; it is not a trained object detector."
        ),
    }

"""Main dithering module for e-paper display optimization."""

import json
import os
from typing import List, Optional, Dict, Any, Union

import numpy as np
from PIL import Image

from .bayer_matrix import create_bayer_matrix
from .color_helpers import hex_to_rgb
from .diffusion_maps import get_diffusion_map
from .find_closest_color import find_closest_palette_color
from .utilities import random_integer

# Load default palettes
_data_dir = os.path.join(os.path.dirname(__file__), "data")
with open(os.path.join(_data_dir, "default_palettes.json"), "r") as f:
    PALETTES = json.load(f)


# Default options matching the JavaScript implementation
DEFAULT_OPTIONS = {
    "ditheringType": "errorDiffusion",
    "errorDiffusionMatrix": "floydSteinberg",
    "serpentine": False,
    "orderedDitheringType": "bayer",
    "orderedDitheringMatrix": [4, 4],
    "randomDitheringType": "blackAndWhite",
    "palette": "default",
    "sampleColorsFromImage": False,
    "numberOfSampleColors": 10,
}


def set_color_palette(palette: Union[str, List[str]]) -> List[List[int]]:
    """
    Convert a palette specification to a list of RGB values.

    Args:
        palette: Either a palette name (str) or a list of hex color strings

    Returns:
        List of [R, G, B] color values
    """
    if isinstance(palette, str):
        palette_array = PALETTES.get(palette, PALETTES["default"])
    else:
        palette_array = palette

    return [hex_to_rgb(color) for color in palette_array]


def get_pixel_color_values(pixel_index: int, data: np.ndarray) -> List[float]:
    """Extract RGBA values from image data at a given pixel index."""
    return [
        float(data[pixel_index]),
        float(data[pixel_index + 1]),
        float(data[pixel_index + 2]),
        float(data[pixel_index + 3]),
    ]


def clamp_uint8(value: float) -> float:
    """Clamp a value to mimic JavaScript's Uint8ClampedArray behavior.

    Uint8ClampedArray clamps to 0-255 on assignment. We keep float precision
    for intermediate calculations to match JavaScript's behavior.
    """
    if value < 0:
        return 0.0
    if value > 255:
        return 255.0
    return value


def set_pixel(data: np.ndarray, pixel_index: int, pixel: List[float]) -> None:
    """Set RGBA values in image data at a given pixel index.

    Values are clamped to 0-255 to match JavaScript's Uint8ClampedArray behavior.
    """
    data[pixel_index] = clamp_uint8(pixel[0])
    data[pixel_index + 1] = clamp_uint8(pixel[1])
    data[pixel_index + 2] = clamp_uint8(pixel[2])
    data[pixel_index + 3] = clamp_uint8(pixel[3])


def get_quant_error(old_pixel: List[float], new_pixel: List[float]) -> List[float]:
    """Calculate the quantization error between old and new pixel values."""
    return [old_pixel[i] - new_pixel[i] for i in range(len(old_pixel))]


def add_quant_error(
    pixel: List[float], quant_error: List[float], diffusion_factor: float
) -> List[float]:
    """Add weighted quantization error to a pixel."""
    return [pixel[i] + quant_error[i] * diffusion_factor for i in range(len(pixel))]


def random_dither_pixel_value(pixel: List[float]) -> List[float]:
    """Apply random dithering to RGB channels."""
    return [
        0.0 if color < random_integer(0, 255) else 255.0
        for color in pixel[:3]
    ] + [pixel[3] if len(pixel) > 3 else 255.0]


def random_dither_black_and_white_pixel_value(pixel: List[float]) -> List[float]:
    """Apply random dithering with black and white output."""
    average_rgb = (pixel[0] + pixel[1] + pixel[2]) / 3
    if average_rgb < random_integer(0, 255):
        return [0.0, 0.0, 0.0, 255.0]
    else:
        return [255.0, 255.0, 255.0, 255.0]


def ordered_dither_pixel_value(
    pixel: List[float],
    coordinates: List[int],
    threshold_map: List[List[int]],
    threshold: float,
) -> List[float]:
    """Apply ordered dithering using a threshold map."""
    map_height = len(threshold_map)
    map_width = len(threshold_map[0])

    factor = threshold_map[coordinates[1] % map_height][coordinates[0] % map_width] / (
        map_height * map_width
    )

    return [color + factor * threshold for color in pixel]


def pixel_xy(index: int, width: int) -> List[int]:
    """Convert a linear pixel index to x,y coordinates."""
    return [index % width, index // width]


def dither_image(
    source_image: Image.Image,
    options: Optional[Dict[str, Any]] = None,
) -> Image.Image:
    """
    Apply dithering to an image for e-paper display optimization.

    Args:
        source_image: PIL Image to dither
        options: Dithering options dictionary with keys:
            - ditheringType: 'errorDiffusion', 'ordered', 'random', or 'quantizationOnly'
            - errorDiffusionMatrix: 'floydSteinberg', 'jarvis', 'stucki', etc.
            - orderedDitheringMatrix: [width, height] of Bayer matrix
            - randomDitheringType: 'rgb' or 'blackAndWhite'
            - palette: palette name or list of hex colors

    Returns:
        A new PIL Image with dithering applied
    """
    if source_image is None:
        return None

    # Merge options with defaults
    opts = {**DEFAULT_OPTIONS, **(options or {})}

    # Convert image to RGBA
    if source_image.mode != "RGBA":
        source_image = source_image.convert("RGBA")

    # Get image data as numpy array
    width, height = source_image.size
    image_data = np.array(source_image, dtype=np.float64).flatten()

    # Set up color palette
    color_palette = set_color_palette(opts["palette"])

    # Create threshold map for ordered dithering
    threshold_map = create_bayer_matrix(
        (opts["orderedDitheringMatrix"][0], opts["orderedDitheringMatrix"][1])
    )

    # Process each pixel
    for current in range(0, len(image_data), 4):
        current_pixel = current
        old_pixel = get_pixel_color_values(current_pixel, image_data)

        # Quantization only
        if not opts["ditheringType"] or opts["ditheringType"] == "quantizationOnly":
            new_pixel = find_closest_palette_color(old_pixel, color_palette)
            set_pixel(image_data, current_pixel, new_pixel)

        # Random dithering - RGB mode
        if opts["ditheringType"] == "random" and opts["randomDitheringType"] == "rgb":
            new_pixel = random_dither_pixel_value(old_pixel)
            set_pixel(image_data, current_pixel, new_pixel)

        # Random dithering - Black and White mode
        if (
            opts["ditheringType"] == "random"
            and opts["randomDitheringType"] == "blackAndWhite"
        ):
            new_pixel = random_dither_black_and_white_pixel_value(old_pixel)
            set_pixel(image_data, current_pixel, new_pixel)

        # Ordered dithering
        if opts["ditheringType"] == "ordered":
            ordered_dither_threshold = 256 / 4
            new_pixel = ordered_dither_pixel_value(
                old_pixel,
                pixel_xy(current_pixel // 4, width),
                threshold_map,
                ordered_dither_threshold,
            )
            new_pixel = find_closest_palette_color(new_pixel, color_palette)
            set_pixel(image_data, current_pixel, new_pixel)

        # Error diffusion dithering
        if opts["ditheringType"] == "errorDiffusion":
            diffusion_map = get_diffusion_map(opts["errorDiffusionMatrix"])
            new_pixel = find_closest_palette_color(old_pixel, color_palette)
            set_pixel(image_data, current_pixel, new_pixel)

            quant_error = get_quant_error(old_pixel, new_pixel)

            for diffusion in diffusion_map:
                # Calculate current pixel's x,y coordinates
                current_x = (current_pixel // 4) % width
                current_y = (current_pixel // 4) // width

                # Calculate target pixel's x,y coordinates
                target_x = current_x + diffusion["offset"][0]
                target_y = current_y + diffusion["offset"][1]

                # Check if target pixel is within image bounds
                if target_x < 0 or target_x >= width or target_y < 0 or target_y >= height:
                    continue

                pixel_index = (target_y * width + target_x) * 4
                error_pixel = add_quant_error(
                    get_pixel_color_values(pixel_index, image_data),
                    quant_error,
                    diffusion["factor"],
                )
                set_pixel(image_data, pixel_index, error_pixel)

    # Convert back to PIL Image
    image_data = np.clip(image_data, 0, 255).astype(np.uint8)
    image_data = image_data.reshape((height, width, 4))
    return Image.fromarray(image_data, "RGBA")

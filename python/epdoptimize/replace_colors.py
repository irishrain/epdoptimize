"""Color replacement utilities for mapping dithered colors to device colors."""

import re
from typing import List

import numpy as np
from PIL import Image


def hex_to_rgb(hex_color: str) -> List[int]:
    """
    Convert a hex color string to RGB values.

    Handles both 3-digit and 6-digit hex formats.

    Args:
        hex_color: A hex color string like '#fff' or '#ffffff'

    Returns:
        A list of [R, G, B] values (0-255)
    """
    # Handle shorthand hex format
    shorthand_match = re.match(
        r"^#?([a-f\d])([a-f\d])([a-f\d])$", hex_color, re.IGNORECASE
    )
    if shorthand_match:
        r, g, b = shorthand_match.groups()
        hex_color = "#" + r + r + g + g + b + b

    # Remove # and parse
    hex_color = hex_color.lstrip("#")
    return [
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    ]


def replace_colors(
    source_image: Image.Image,
    original_colors: List[str],
    replace_colors_list: List[str],
) -> Image.Image:
    """
    Replace colors in an image from the original palette to device colors.

    Args:
        source_image: PIL Image with dithered colors
        original_colors: List of original hex colors to match
        replace_colors_list: List of replacement hex colors

    Returns:
        A new PIL Image with colors replaced
    """
    # Convert image to RGBA
    if source_image.mode != "RGBA":
        source_image = source_image.convert("RGBA")

    width, height = source_image.size
    image_data = np.array(source_image, dtype=np.uint8).flatten()

    # Convert colors to RGB
    original_colors_rgb = [hex_to_rgb(color) for color in original_colors]
    replace_colors_rgb = [hex_to_rgb(color) for color in replace_colors_list]

    error_colors = 0

    for i in range(0, len(image_data), 4):
        # Find matching original color
        color_rgb = None
        color_index = -1

        for idx, orig_color in enumerate(original_colors_rgb):
            if (
                image_data[i] == orig_color[0]
                and image_data[i + 1] == orig_color[1]
                and image_data[i + 2] == orig_color[2]
            ):
                color_rgb = orig_color
                color_index = idx
                break

        if color_rgb is not None:
            # Get the corresponding replacement color
            if color_index < len(replace_colors_rgb):
                color_map_rgb = replace_colors_rgb[color_index]
                image_data[i] = color_map_rgb[0]
                image_data[i + 1] = color_map_rgb[1]
                image_data[i + 2] = color_map_rgb[2]
            else:
                # No matching replacement color - return early like JS version
                return None
        else:
            error_colors += 1

    if error_colors > 0:
        print(
            f"replaceColors: {error_colors} pixels were not replaced. "
            "Check if the colors match exactly."
        )

    # Convert back to PIL Image
    image_data = image_data.reshape((height, width, 4))
    return Image.fromarray(image_data, "RGBA")

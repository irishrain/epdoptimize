"""Color quantization utilities for finding the closest palette color."""

import math
from typing import List


def distance_in_color_space(color1: List[float], color2: List[float]) -> float:
    """
    Calculate the Euclidean distance between two colors in RGB space.

    Args:
        color1: First color as [R, G, B] or [R, G, B, A]
        color2: Second color as [R, G, B] or [R, G, B, A]

    Returns:
        The Euclidean distance between the colors (ignores alpha)
    """
    r = color1[0] - color2[0]
    g = color1[1] - color2[1]
    b = color1[2] - color2[2]

    return math.sqrt(r * r + g * g + b * b)


def find_closest_palette_color(pixel: List[float], color_palette: List[List[int]]) -> List[float]:
    """
    Find the closest color in the palette to the given pixel.

    Args:
        pixel: The pixel color as [R, G, B] or [R, G, B, A]
        color_palette: List of palette colors as [[R, G, B], ...]

    Returns:
        The closest palette color as [R, G, B, A] (alpha is always 255)
    """
    # Calculate distances to all palette colors
    colors_with_distance = []
    for color in color_palette:
        colors_with_distance.append({
            "distance": distance_in_color_space(color, pixel),
            "color": list(color)  # Make a copy
        })

    # Find the closest color
    closest_color = None
    for color_entry in colors_with_distance:
        if closest_color is None:
            closest_color = color_entry
        else:
            if color_entry["distance"] < closest_color["distance"]:
                closest_color = color_entry

    # Ensure alpha value is present
    result = closest_color["color"]
    if len(result) < 4:
        result.append(255)

    return result

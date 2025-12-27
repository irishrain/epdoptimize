"""Color helper utilities for converting between color formats."""

import re
from typing import List, Optional


def hex_to_rgb(hex_color: str) -> Optional[List[int]]:
    """
    Convert a hex color string to RGB values.

    Supports both 3-digit (#RGB) and 6-digit (#RRGGBB) hex formats.
    The '#' prefix is optional.

    Args:
        hex_color: A hex color string like '#fff', '#ffffff', 'fff', or 'ffffff'

    Returns:
        A list of [R, G, B] values (0-255), or None if parsing fails
    """
    # Handle shorthand hex format (#RGB -> #RRGGBB)
    shorthand_regex = re.compile(r'^#?([a-f\d])([a-f\d])([a-f\d])$', re.IGNORECASE)
    match = shorthand_regex.match(hex_color)
    if match:
        r, g, b = match.groups()
        hex_color = r + r + g + g + b + b

    # Parse full hex format
    full_regex = re.compile(r'^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$', re.IGNORECASE)
    match = full_regex.match(hex_color)

    if match:
        return [
            int(match.group(1), 16),
            int(match.group(2), 16),
            int(match.group(3), 16)
        ]
    return None

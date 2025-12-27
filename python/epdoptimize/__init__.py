"""
epdoptimize - E-Paper Display Image Optimization Library

A Python library for optimizing and dithering images for electronic paper displays.
Provides color reduction, calibration, and various dithering algorithms to improve
visual quality on limited-color e-ink displays.
"""

import json
import os

from .dither import dither_image
from .replace_colors import replace_colors

# Load default palettes and device colors
_data_dir = os.path.join(os.path.dirname(__file__), "data")

with open(os.path.join(_data_dir, "default_palettes.json"), "r") as f:
    _PALETTES = json.load(f)

with open(os.path.join(_data_dir, "default_device_colors.json"), "r") as f:
    _DEVICE_COLORS = json.load(f)


def get_default_palettes(name: str) -> list:
    """
    Retrieve a named default palette (hex codes).

    This is used for dithering images to fit the eInk display and uses
    the real colors of the display.

    Args:
        name: Palette name ('default', 'gameboy', 'spectra6', 'acep')

    Returns:
        List of hex color strings
    """
    key = name.lower()
    return _PALETTES.get(key, _PALETTES["default"])


def get_device_colors(name: str) -> list:
    """
    Retrieve a named default device color set.

    This is used for displaying the colors on the eInk display.

    Args:
        name: Device color set name ('default', 'gameboy', 'spectra6', 'acep')

    Returns:
        List of hex color strings
    """
    key = name.lower()
    return _DEVICE_COLORS.get(key, _DEVICE_COLORS["default"])


__all__ = [
    "dither_image",
    "replace_colors",
    "get_default_palettes",
    "get_device_colors",
]

__version__ = "1.0.0"

"""Integration tests for full dithering pipeline."""

import os
import pytest
import numpy as np
from PIL import Image

from epdoptimize import (
    dither_image,
    replace_colors,
    get_default_palettes,
    get_device_colors,
)


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def create_test_image(width, height, pattern="gradient"):
    """Create a test image with specified pattern."""
    img = Image.new("RGBA", (width, height))
    pixels = img.load()

    if pattern == "gradient":
        # Create a grayscale gradient
        for y in range(height):
            for x in range(width):
                gray = int((x / width) * 255)
                pixels[x, y] = (gray, gray, gray, 255)
    elif pattern == "color_gradient":
        # Create a color gradient
        for y in range(height):
            for x in range(width):
                r = int((x / width) * 255)
                g = int((y / height) * 255)
                b = int(((width - x) / width) * 255)
                pixels[x, y] = (r, g, b, 255)
    elif pattern == "solid_red":
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (255, 0, 0, 255)
    elif pattern == "solid_white":
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (255, 255, 255, 255)
    elif pattern == "checkerboard":
        for y in range(height):
            for x in range(width):
                if (x + y) % 2 == 0:
                    pixels[x, y] = (0, 0, 0, 255)
                else:
                    pixels[x, y] = (255, 255, 255, 255)

    return img


class TestDitherImage:
    """Test dither_image function with various options."""

    def test_quantization_only(self):
        """Test quantization without dithering."""
        img = create_test_image(10, 10, "gradient")
        result = dither_image(img, {
            "ditheringType": "quantizationOnly",
            "palette": "default"
        })

        assert result is not None
        assert result.size == img.size

        # All pixels should be either black or white
        pixels = np.array(result)
        for y in range(10):
            for x in range(10):
                pixel = pixels[y, x]
                is_black = all(pixel[:3] == [0, 0, 0])
                is_white = all(pixel[:3] == [255, 255, 255])
                assert is_black or is_white, f"Pixel at ({x},{y}) is not black or white: {pixel}"

    def test_error_diffusion_floyd_steinberg(self):
        """Test Floyd-Steinberg error diffusion dithering."""
        img = create_test_image(20, 20, "gradient")
        result = dither_image(img, {
            "ditheringType": "errorDiffusion",
            "errorDiffusionMatrix": "floydSteinberg",
            "palette": "default"
        })

        assert result is not None
        assert result.size == img.size

        # All pixels should be either black or white
        pixels = np.array(result)
        unique_colors = set()
        for y in range(20):
            for x in range(20):
                unique_colors.add(tuple(pixels[y, x][:3]))

        assert unique_colors <= {(0, 0, 0), (255, 255, 255)}

    def test_error_diffusion_jarvis(self):
        """Test Jarvis error diffusion dithering."""
        img = create_test_image(20, 20, "gradient")
        result = dither_image(img, {
            "ditheringType": "errorDiffusion",
            "errorDiffusionMatrix": "jarvis",
            "palette": "default"
        })

        assert result is not None
        assert result.size == img.size

    def test_error_diffusion_all_kernels(self):
        """Test all error diffusion kernels produce valid output."""
        kernels = [
            "floydSteinberg",
            "falseFloydSteinberg",
            "jarvis",
            "stucki",
            "burkes",
            "sierra3",
            "sierra2",
            "Sierra2-4A",
        ]

        img = create_test_image(15, 15, "gradient")

        for kernel in kernels:
            result = dither_image(img, {
                "ditheringType": "errorDiffusion",
                "errorDiffusionMatrix": kernel,
                "palette": "default"
            })
            assert result is not None, f"Kernel {kernel} returned None"
            assert result.size == img.size, f"Kernel {kernel} changed image size"

    def test_ordered_dithering(self):
        """Test ordered (Bayer) dithering."""
        img = create_test_image(16, 16, "gradient")
        result = dither_image(img, {
            "ditheringType": "ordered",
            "orderedDitheringMatrix": [4, 4],
            "palette": "default"
        })

        assert result is not None
        assert result.size == img.size

        # All pixels should be palette colors
        pixels = np.array(result)
        unique_colors = set()
        for y in range(16):
            for x in range(16):
                unique_colors.add(tuple(pixels[y, x][:3]))

        assert unique_colors <= {(0, 0, 0), (255, 255, 255)}

    def test_ordered_dithering_different_matrix_sizes(self):
        """Test ordered dithering with different matrix sizes."""
        img = create_test_image(20, 20, "gradient")

        for size in [(2, 2), (4, 4), (8, 8)]:
            result = dither_image(img, {
                "ditheringType": "ordered",
                "orderedDitheringMatrix": list(size),
                "palette": "default"
            })
            assert result is not None

    def test_color_palette_spectra6(self):
        """Test dithering with Spectra 6 color palette."""
        img = create_test_image(20, 20, "color_gradient")
        palette = get_default_palettes("spectra6")

        result = dither_image(img, {
            "ditheringType": "errorDiffusion",
            "errorDiffusionMatrix": "floydSteinberg",
            "palette": palette
        })

        assert result is not None

        # Convert palette hex to RGB for comparison
        from epdoptimize.color_helpers import hex_to_rgb
        palette_rgb = set(tuple(hex_to_rgb(c)) for c in palette)

        pixels = np.array(result)
        unique_colors = set()
        for y in range(20):
            for x in range(20):
                unique_colors.add(tuple(pixels[y, x][:3]))

        # All unique colors should be in the palette
        assert unique_colors <= palette_rgb

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        result = dither_image(None, {})
        assert result is None

    def test_preserves_image_dimensions(self):
        """Test that various image dimensions are preserved."""
        for width, height in [(10, 10), (100, 50), (50, 100), (1, 100), (100, 1)]:
            img = create_test_image(width, height, "gradient")
            result = dither_image(img, {"palette": "default"})
            assert result.size == (width, height)


class TestReplaceColors:
    """Test replace_colors function."""

    def test_replace_black_white(self):
        """Test replacing black and white with device colors."""
        # Create a simple black and white image
        img = create_test_image(10, 10, "checkerboard")

        original = ["#000", "#fff"]
        replacement = ["#e6e6e6", "#212121"]

        result = replace_colors(img, original, replacement)

        assert result is not None
        assert result.size == img.size

        # Check that colors were replaced
        from epdoptimize.replace_colors import hex_to_rgb
        expected_colors = {tuple(hex_to_rgb(c)) for c in replacement}

        pixels = np.array(result)
        actual_colors = set()
        for y in range(10):
            for x in range(10):
                actual_colors.add(tuple(pixels[y, x][:3]))

        assert actual_colors <= expected_colors

    def test_replace_with_spectra6(self):
        """Test replacing Spectra6 palette with device colors."""
        # Create a dithered image first
        img = create_test_image(20, 20, "color_gradient")
        palette = get_default_palettes("spectra6")
        device_colors = get_device_colors("spectra6")

        dithered = dither_image(img, {
            "ditheringType": "errorDiffusion",
            "palette": palette
        })

        result = replace_colors(dithered, palette, device_colors)
        assert result is not None


class TestGetDefaultPalettes:
    """Test get_default_palettes function."""

    def test_default_palette(self):
        """Test default black and white palette."""
        palette = get_default_palettes("default")
        assert len(palette) == 2
        assert "#000" in palette
        assert "#fff" in palette

    def test_gameboy_palette(self):
        """Test Game Boy palette."""
        palette = get_default_palettes("gameboy")
        assert len(palette) == 4

    def test_spectra6_palette(self):
        """Test Spectra 6 palette."""
        palette = get_default_palettes("spectra6")
        assert len(palette) == 6

    def test_acep_palette(self):
        """Test AcEP palette."""
        palette = get_default_palettes("acep")
        assert len(palette) == 7

    def test_case_insensitive(self):
        """Test that palette names are case insensitive."""
        assert get_default_palettes("SPECTRA6") == get_default_palettes("spectra6")
        assert get_default_palettes("Gameboy") == get_default_palettes("gameboy")

    def test_unknown_palette_returns_default(self):
        """Test that unknown palette name returns default."""
        result = get_default_palettes("nonexistent")
        assert result == get_default_palettes("default")


class TestGetDeviceColors:
    """Test get_device_colors function."""

    def test_default_device_colors(self):
        """Test default device colors."""
        colors = get_device_colors("default")
        assert len(colors) == 2

    def test_spectra6_device_colors(self):
        """Test Spectra 6 device colors."""
        colors = get_device_colors("spectra6")
        assert len(colors) == 6

    def test_case_insensitive(self):
        """Test that device color names are case insensitive."""
        assert get_device_colors("SPECTRA6") == get_device_colors("spectra6")

    def test_unknown_returns_default(self):
        """Test that unknown name returns default."""
        result = get_device_colors("nonexistent")
        assert result == get_device_colors("default")


class TestFullPipeline:
    """Test the complete dithering pipeline."""

    def test_full_workflow(self):
        """Test complete workflow: load -> dither -> replace colors."""
        # Create a color image
        img = create_test_image(50, 50, "color_gradient")

        # Get palettes
        palette = get_default_palettes("spectra6")
        device_colors = get_device_colors("spectra6")

        # Dither
        dithered = dither_image(img, {
            "ditheringType": "errorDiffusion",
            "errorDiffusionMatrix": "floydSteinberg",
            "palette": palette
        })

        assert dithered is not None
        assert dithered.size == img.size

        # Replace colors
        final = replace_colors(dithered, palette, device_colors)

        assert final is not None
        assert final.size == img.size

    def test_all_palettes_with_error_diffusion(self):
        """Test all palettes work with error diffusion."""
        img = create_test_image(30, 30, "color_gradient")

        for palette_name in ["default", "gameboy", "spectra6", "acep"]:
            palette = get_default_palettes(palette_name)
            device_colors = get_device_colors(palette_name)

            dithered = dither_image(img, {
                "ditheringType": "errorDiffusion",
                "palette": palette
            })

            assert dithered is not None, f"Dithering failed for {palette_name}"

            final = replace_colors(dithered, palette, device_colors)
            assert final is not None, f"Color replacement failed for {palette_name}"

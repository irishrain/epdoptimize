"""Unit tests for dither module, comparing with JavaScript implementation."""

import json
import os
import pytest

from epdoptimize.dither import (
    get_pixel_color_values,
    get_quant_error,
    add_quant_error,
    pixel_xy,
    ordered_dither_pixel_value,
    set_color_palette,
)
from epdoptimize.bayer_matrix import create_bayer_matrix

import numpy as np


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestGetPixelColorValues:
    """Test get_pixel_color_values function."""

    def test_extracts_rgba(self):
        """Test extracting RGBA values from array."""
        data = np.array([100, 150, 200, 255, 50, 100, 150, 128], dtype=np.float64)
        result = get_pixel_color_values(0, data)
        assert result == [100.0, 150.0, 200.0, 255.0]

        result2 = get_pixel_color_values(4, data)
        assert result2 == [50.0, 100.0, 150.0, 128.0]


class TestQuantError:
    """Test quant error calculations against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "quant_error.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_quant_error_matches_javascript(self, js_fixtures):
        """Test that get_quant_error produces identical results to JavaScript."""
        for fixture in js_fixtures:
            old_pixel = fixture["input"]["oldPixel"]
            new_pixel = fixture["input"]["newPixel"]
            expected = fixture["output"]
            result = get_quant_error(old_pixel, new_pixel)
            assert result == expected, f"get_quant_error: expected {expected}, got {result}"

    def test_no_error_same_pixels(self):
        """Test that identical pixels have zero error."""
        pixel = [100.0, 150.0, 200.0, 255.0]
        result = get_quant_error(pixel, pixel)
        assert result == [0.0, 0.0, 0.0, 0.0]

    def test_positive_error(self):
        """Test positive error when old > new."""
        old = [200.0, 200.0, 200.0, 255.0]
        new = [100.0, 100.0, 100.0, 255.0]
        result = get_quant_error(old, new)
        assert result == [100.0, 100.0, 100.0, 0.0]

    def test_negative_error(self):
        """Test negative error when old < new."""
        old = [100.0, 100.0, 100.0, 255.0]
        new = [200.0, 200.0, 200.0, 255.0]
        result = get_quant_error(old, new)
        assert result == [-100.0, -100.0, -100.0, 0.0]


class TestAddQuantError:
    """Test add_quant_error function against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "add_quant_error.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_add_quant_error_matches_javascript(self, js_fixtures):
        """Test that add_quant_error produces identical results to JavaScript."""
        for fixture in js_fixtures:
            pixel = fixture["input"]["pixel"]
            quant_error = fixture["input"]["quantError"]
            factor = fixture["input"]["factor"]
            expected = fixture["output"]
            result = add_quant_error(pixel, quant_error, factor)
            for i in range(len(result)):
                assert abs(result[i] - expected[i]) < 0.0001, \
                    f"add_quant_error: expected {expected}, got {result}"


class TestPixelXY:
    """Test pixel_xy function against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "pixel_xy.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_pixel_xy_matches_javascript(self, js_fixtures):
        """Test that pixel_xy produces identical results to JavaScript."""
        for fixture in js_fixtures:
            index = fixture["input"]["index"]
            width = fixture["input"]["width"]
            expected = fixture["output"]
            result = pixel_xy(index, width)
            assert result == expected, f"pixel_xy({index}, {width}): expected {expected}, got {result}"

    def test_first_pixel(self):
        """Test first pixel is at (0, 0)."""
        assert pixel_xy(0, 100) == [0, 0]

    def test_end_of_row(self):
        """Test last pixel of first row."""
        assert pixel_xy(9, 10) == [9, 0]

    def test_start_of_second_row(self):
        """Test first pixel of second row."""
        assert pixel_xy(10, 10) == [0, 1]


class TestOrderedDitherPixelValue:
    """Test ordered_dither_pixel_value function against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "ordered_dither.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_ordered_dither_matches_javascript(self, js_fixtures):
        """Test that ordered_dither_pixel_value produces identical results to JavaScript."""
        for fixture in js_fixtures:
            pixel = fixture["input"]["pixel"]
            coordinates = fixture["input"]["coordinates"]
            matrix_size = tuple(fixture["input"]["matrixSize"])
            threshold = fixture["input"]["threshold"]
            expected = fixture["output"]

            threshold_map = create_bayer_matrix(matrix_size)
            result = ordered_dither_pixel_value(pixel, coordinates, threshold_map, threshold)

            for i in range(len(result)):
                assert abs(result[i] - expected[i]) < 0.0001, \
                    f"ordered_dither_pixel_value: expected {expected}, got {result}"


class TestSetColorPalette:
    """Test set_color_palette function."""

    def test_string_palette_name(self):
        """Test loading palette by name."""
        result = set_color_palette("default")
        assert len(result) == 2
        assert result[0] == [0, 0, 0]  # Black
        assert result[1] == [255, 255, 255]  # White

    def test_list_palette(self):
        """Test loading palette from list of hex colors."""
        palette = ["#ff0000", "#00ff00", "#0000ff"]
        result = set_color_palette(palette)
        assert len(result) == 3
        assert result[0] == [255, 0, 0]
        assert result[1] == [0, 255, 0]
        assert result[2] == [0, 0, 255]

    def test_unknown_palette_defaults(self):
        """Test that unknown palette name falls back to default."""
        result = set_color_palette("nonexistent")
        default = set_color_palette("default")
        assert result == default

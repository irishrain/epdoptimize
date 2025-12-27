"""Unit tests for find_closest_color module, comparing with JavaScript implementation."""

import json
import math
import os
import pytest

from epdoptimize.find_closest_color import find_closest_palette_color, distance_in_color_space


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestDistanceInColorSpace:
    """Test distance_in_color_space function."""

    def test_same_color(self):
        """Test distance between identical colors is 0."""
        assert distance_in_color_space([100, 100, 100], [100, 100, 100]) == 0

    def test_black_white_distance(self):
        """Test distance between black and white."""
        distance = distance_in_color_space([0, 0, 0], [255, 255, 255])
        expected = math.sqrt(255**2 + 255**2 + 255**2)
        assert abs(distance - expected) < 0.001

    def test_primary_colors(self):
        """Test distances between primary colors."""
        # Red to green
        rg_dist = distance_in_color_space([255, 0, 0], [0, 255, 0])
        expected_rg = math.sqrt(255**2 + 255**2)
        assert abs(rg_dist - expected_rg) < 0.001

        # Red to blue
        rb_dist = distance_in_color_space([255, 0, 0], [0, 0, 255])
        assert abs(rb_dist - expected_rg) < 0.001  # Same distance

    def test_symmetric(self):
        """Test that distance is symmetric."""
        c1 = [100, 150, 200]
        c2 = [50, 100, 150]
        assert distance_in_color_space(c1, c2) == distance_in_color_space(c2, c1)


class TestFindClosestPaletteColor:
    """Test find_closest_palette_color function against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "find_closest_color.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_find_closest_matches_javascript(self, js_fixtures):
        """Test that find_closest_palette_color produces identical results to JavaScript."""
        for fixture in js_fixtures:
            pixel = fixture["input"]["pixel"]
            palette = fixture["input"]["palette"]
            expected = fixture["output"]
            result = find_closest_palette_color(pixel, palette)
            assert result == expected, f"find_closest_palette_color({pixel}, ...): expected {expected}, got {result}"

    def test_exact_match(self):
        """Test finding an exact color match."""
        palette = [[0, 0, 0], [255, 255, 255], [255, 0, 0]]
        result = find_closest_palette_color([255, 0, 0, 255], palette)
        assert result[:3] == [255, 0, 0]

    def test_black_white_palette(self):
        """Test with simple black and white palette."""
        palette = [[0, 0, 0], [255, 255, 255]]

        # Dark gray should match black
        result = find_closest_palette_color([50, 50, 50, 255], palette)
        assert result[:3] == [0, 0, 0]

        # Light gray should match white
        result = find_closest_palette_color([200, 200, 200, 255], palette)
        assert result[:3] == [255, 255, 255]

    def test_adds_alpha_channel(self):
        """Test that alpha channel is added if not present in palette."""
        palette = [[0, 0, 0], [255, 255, 255]]  # No alpha in palette
        result = find_closest_palette_color([100, 100, 100, 255], palette)
        assert len(result) == 4
        assert result[3] == 255

    def test_preserves_existing_alpha(self):
        """Test that existing alpha is preserved if present."""
        palette = [[0, 0, 0, 128]]  # Alpha present
        result = find_closest_palette_color([50, 50, 50, 255], palette)
        assert len(result) == 4

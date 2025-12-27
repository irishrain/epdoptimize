"""Unit tests for color_helpers module, comparing with JavaScript implementation."""

import json
import os
import pytest

from epdoptimize.color_helpers import hex_to_rgb


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestHexToRgb:
    """Test hex_to_rgb function against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "hex_to_rgb.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_hex_to_rgb_matches_javascript(self, js_fixtures):
        """Test that hex_to_rgb produces identical results to JavaScript."""
        for fixture in js_fixtures:
            hex_input = fixture["input"]
            expected = fixture["output"]
            result = hex_to_rgb(hex_input)
            assert result == expected, f"hex_to_rgb('{hex_input}'): expected {expected}, got {result}"

    def test_shorthand_hex(self):
        """Test 3-digit hex colors."""
        assert hex_to_rgb("#fff") == [255, 255, 255]
        assert hex_to_rgb("#000") == [0, 0, 0]
        assert hex_to_rgb("#f00") == [255, 0, 0]
        assert hex_to_rgb("#0f0") == [0, 255, 0]
        assert hex_to_rgb("#00f") == [0, 0, 255]

    def test_full_hex(self):
        """Test 6-digit hex colors."""
        assert hex_to_rgb("#ffffff") == [255, 255, 255]
        assert hex_to_rgb("#000000") == [0, 0, 0]
        assert hex_to_rgb("#ff0000") == [255, 0, 0]
        assert hex_to_rgb("#00ff00") == [0, 255, 0]
        assert hex_to_rgb("#0000ff") == [0, 0, 255]

    def test_case_insensitive(self):
        """Test that hex parsing is case insensitive."""
        assert hex_to_rgb("#FFF") == hex_to_rgb("#fff")
        assert hex_to_rgb("#ABCDEF") == hex_to_rgb("#abcdef")

    def test_without_hash(self):
        """Test hex colors without # prefix."""
        assert hex_to_rgb("fff") == [255, 255, 255]
        assert hex_to_rgb("123456") == [18, 52, 86]

    def test_invalid_hex(self):
        """Test that invalid hex returns None."""
        assert hex_to_rgb("invalid") is None
        assert hex_to_rgb("#gg0000") is None
        assert hex_to_rgb("#12345") is None  # 5 digits

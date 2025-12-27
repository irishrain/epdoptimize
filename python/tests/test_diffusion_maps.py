"""Unit tests for diffusion_maps module, comparing with JavaScript implementation."""

import json
import os
import pytest

from epdoptimize.diffusion_maps import (
    floyd_steinberg,
    false_floyd_steinberg,
    jarvis,
    stucki,
    burkes,
    sierra3,
    sierra2,
    sierra2_4a,
    get_diffusion_map,
    DIFFUSION_MAPS,
)


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def approx_equal_map(map1, map2, tolerance=1e-10):
    """Compare two diffusion maps with floating point tolerance."""
    if len(map1) != len(map2):
        return False
    for entry1, entry2 in zip(map1, map2):
        if entry1["offset"] != entry2["offset"]:
            return False
        if abs(entry1["factor"] - entry2["factor"]) > tolerance:
            return False
    return True


class TestDiffusionMaps:
    """Test diffusion maps against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "diffusion_maps.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_floyd_steinberg_matches_javascript(self, js_fixtures):
        """Test Floyd-Steinberg kernel matches JavaScript."""
        result = floyd_steinberg()
        expected = js_fixtures["floydSteinberg"]
        assert approx_equal_map(result, expected)

    def test_false_floyd_steinberg_matches_javascript(self, js_fixtures):
        """Test False Floyd-Steinberg kernel matches JavaScript."""
        result = false_floyd_steinberg()
        expected = js_fixtures["falseFloydSteinberg"]
        assert approx_equal_map(result, expected)

    def test_jarvis_matches_javascript(self, js_fixtures):
        """Test Jarvis kernel matches JavaScript."""
        result = jarvis()
        expected = js_fixtures["jarvis"]
        assert approx_equal_map(result, expected)

    def test_stucki_matches_javascript(self, js_fixtures):
        """Test Stucki kernel matches JavaScript."""
        result = stucki()
        expected = js_fixtures["stucki"]
        assert approx_equal_map(result, expected)

    def test_burkes_matches_javascript(self, js_fixtures):
        """Test Burkes kernel matches JavaScript."""
        result = burkes()
        expected = js_fixtures["burkes"]
        assert approx_equal_map(result, expected)

    def test_sierra3_matches_javascript(self, js_fixtures):
        """Test Sierra-3 kernel matches JavaScript."""
        result = sierra3()
        expected = js_fixtures["sierra3"]
        assert approx_equal_map(result, expected)

    def test_sierra2_matches_javascript(self, js_fixtures):
        """Test Sierra-2 kernel matches JavaScript."""
        result = sierra2()
        expected = js_fixtures["sierra2"]
        assert approx_equal_map(result, expected)

    def test_sierra2_4a_matches_javascript(self, js_fixtures):
        """Test Sierra-2-4A kernel matches JavaScript."""
        result = sierra2_4a()
        expected = js_fixtures["Sierra2-4A"]
        assert approx_equal_map(result, expected)

    def test_factors_sum_reasonable(self):
        """Test that all diffusion factors sum to a reasonable amount (~0.75 to 1.0).

        Note: Some algorithms like Jarvis intentionally don't sum to exactly 1.0.
        Jarvis sums to 47/48 ≈ 0.979, which matches the JavaScript implementation.
        """
        for name, func in DIFFUSION_MAPS.items():
            diffusion_map = func()
            total = sum(entry["factor"] for entry in diffusion_map)
            assert 0.75 <= total <= 1.01, f"{name}: factors sum to {total}, expected 0.75-1.0"

    def test_get_diffusion_map_valid(self):
        """Test get_diffusion_map returns correct map for valid names."""
        assert get_diffusion_map("floydSteinberg") == floyd_steinberg()
        assert get_diffusion_map("jarvis") == jarvis()
        assert get_diffusion_map("Sierra2-4A") == sierra2_4a()

    def test_get_diffusion_map_invalid_defaults_to_floyd_steinberg(self):
        """Test get_diffusion_map defaults to Floyd-Steinberg for invalid names."""
        result = get_diffusion_map("nonexistent")
        expected = floyd_steinberg()
        assert result == expected

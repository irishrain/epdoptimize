"""Unit tests for bayer_matrix module, comparing with JavaScript implementation."""

import json
import os
import pytest

from epdoptimize.bayer_matrix import create_bayer_matrix


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestBayerMatrix:
    """Test create_bayer_matrix function against JavaScript implementation."""

    @pytest.fixture
    def js_fixtures(self):
        """Load JavaScript test fixtures."""
        fixture_path = os.path.join(FIXTURES_DIR, "bayer_matrix.json")
        if not os.path.exists(fixture_path):
            pytest.skip("Fixtures not generated. Run: node tests/generate-fixtures.js")
        with open(fixture_path) as f:
            return json.load(f)

    def test_bayer_matrix_matches_javascript(self, js_fixtures):
        """Test that create_bayer_matrix produces identical results to JavaScript."""
        for fixture in js_fixtures:
            size = tuple(fixture["input"])
            expected = fixture["output"]
            result = create_bayer_matrix(size)
            assert result == expected, f"create_bayer_matrix({size}): expected {expected}, got {result}"

    def test_1x1_matrix(self):
        """Test 1x1 Bayer matrix."""
        result = create_bayer_matrix((1, 1))
        assert len(result) == 1
        assert len(result[0]) == 1
        assert result[0][0] == 0  # Single element should be 0

    def test_2x2_matrix(self):
        """Test 2x2 Bayer matrix."""
        result = create_bayer_matrix((2, 2))
        assert len(result) == 2
        assert len(result[0]) == 2
        # Values should be 0-3 after re-indexing
        flat = [val for row in result for val in row]
        assert sorted(flat) == [0, 1, 2, 3]

    def test_4x4_matrix(self):
        """Test 4x4 Bayer matrix."""
        result = create_bayer_matrix((4, 4))
        assert len(result) == 4
        assert len(result[0]) == 4
        # Values should be 0-15 after re-indexing
        flat = [val for row in result for val in row]
        assert sorted(flat) == list(range(16))

    def test_8x8_matrix(self):
        """Test 8x8 Bayer matrix returns the full pre-computed matrix."""
        result = create_bayer_matrix((8, 8))
        assert len(result) == 8
        assert len(result[0]) == 8
        # The 8x8 matrix should have values from the pre-computed big matrix

    def test_asymmetric_matrix(self):
        """Test asymmetric Bayer matrices."""
        result_2x4 = create_bayer_matrix((2, 4))
        assert len(result_2x4) == 4
        assert len(result_2x4[0]) == 2

        result_4x2 = create_bayer_matrix((4, 2))
        assert len(result_4x2) == 2
        assert len(result_4x2[0]) == 4

    def test_max_size_clamping(self):
        """Test that sizes > 8 are clamped to 8."""
        result = create_bayer_matrix((10, 10))
        assert len(result) == 8
        assert len(result[0]) == 8

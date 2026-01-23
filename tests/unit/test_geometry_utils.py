"""
Unit tests for geometry utilities.

Tests the Bresenham line algorithm implementation for correctness
across various edge cases and scenarios.
"""

import pytest

from sj_das.utils.geometry_utils import bresenham_line


class TestBresenhamLine:
    """Test suite for Bresenham line algorithm."""

    def test_horizontal_line(self):
        """Test horizontal line generation."""
        points = bresenham_line(0, 0, 5, 0)
        expected = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
        assert points == expected

    def test_vertical_line(self):
        """Test vertical line generation."""
        points = bresenham_line(0, 0, 0, 5)
        expected = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
        assert points == expected

    def test_diagonal_line(self):
        """Test 45-degree diagonal line."""
        points = bresenham_line(0, 0, 3, 3)
        expected = [(0, 0), (1, 1), (2, 2), (3, 3)]
        assert points == expected

    def test_negative_slope(self):
        """Test line with negative slope."""
        points = bresenham_line(0, 5, 5, 0)
        assert len(points) == 6
        assert points[0] == (0, 5)
        assert points[-1] == (5, 0)

    def test_single_point(self):
        """Test line with same start and end point."""
        points = bresenham_line(3, 3, 3, 3)
        assert points == [(3, 3)]

    def test_steep_line(self):
        """Test steep line (dy > dx)."""
        points = bresenham_line(0, 0, 2, 5)
        assert len(points) == 6
        assert points[0] == (0, 0)
        assert points[-1] == (2, 5)

    def test_reverse_direction(self):
        """Test line drawn in reverse direction."""
        forward = bresenham_line(0, 0, 5, 3)
        backward = bresenham_line(5, 3, 0, 0)
        # Lines should have same length
        assert len(forward) == len(backward)

    def test_large_coordinates(self):
        """Test with large coordinate values."""
        points = bresenham_line(0, 0, 1000, 1000)
        assert len(points) == 1001
        assert points[0] == (0, 0)
        assert points[-1] == (1000, 1000)

    def test_negative_coordinates(self):
        """Test with negative coordinates."""
        points = bresenham_line(-5, -5, 5, 5)
        assert len(points) == 11
        assert points[0] == (-5, -5)
        assert points[-1] == (5, 5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

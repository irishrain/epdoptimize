"""Bayer matrix generation for ordered dithering."""

from typing import List, Tuple


def create_bayer_matrix(size: Tuple[int, int]) -> List[List[int]]:
    """
    Create a Bayer threshold matrix for ordered dithering.

    Args:
        size: Tuple of (width, height), max 8x8

    Returns:
        A 2D list representing the Bayer matrix
    """
    width = min(size[0], 8) if size[0] < 8 else 8
    height = min(size[1], 8) if size[1] < 8 else 8

    # Pre-computed 8x8 Bayer matrix
    big_matrix = [
        [0, 48, 12, 60, 3, 51, 15, 63],
        [32, 16, 44, 28, 35, 19, 47, 31],
        [8, 56, 4, 52, 11, 59, 7, 55],
        [40, 24, 36, 20, 43, 27, 39, 32],
        [2, 50, 14, 62, 1, 49, 13, 61],
        [34, 18, 46, 30, 33, 17, 45, 29],
        [10, 58, 6, 54, 9, 57, 5, 53],
        [42, 26, 38, 22, 41, 25, 37, 21],
    ]

    # If using full 8x8, return the big matrix directly
    if width == 8 and height == 8:
        return big_matrix

    # Create a smaller matrix by extracting the needed portion
    matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            # Note: JavaScript code uses bigMatrix[x][y] which is transposed access
            row.append(big_matrix[x][y])
        matrix.append(row)

    # Re-index the matrix values to be sequential 0 to (width*height - 1)
    # Flatten, sort, create index mapping
    flat_values = []
    for row in matrix:
        flat_values.extend(row)

    sorted_values = sorted(flat_values)
    index_map = {v: i for i, v in enumerate(sorted_values)}

    # Apply the new indices
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            matrix[y][x] = index_map[matrix[y][x]]

    return matrix

"""Utility functions for the epdoptimize library."""

import random


def random_integer(min_val: int, max_val: int) -> int:
    """
    Generate a random integer between min_val and max_val (inclusive).

    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        A random integer in the range [min_val, max_val]
    """
    return random.randint(min_val, max_val)

"""Error diffusion maps for dithering algorithms."""

from typing import List, Dict, Any


def floyd_steinberg() -> List[Dict[str, Any]]:
    """Floyd-Steinberg error diffusion kernel."""
    return [
        {"offset": [1, 0], "factor": 7 / 16},
        {"offset": [-1, 1], "factor": 3 / 16},
        {"offset": [0, 1], "factor": 5 / 16},
        {"offset": [1, 1], "factor": 1 / 16},
    ]


def false_floyd_steinberg() -> List[Dict[str, Any]]:
    """False Floyd-Steinberg error diffusion kernel (simplified)."""
    return [
        {"offset": [1, 0], "factor": 3 / 8},
        {"offset": [0, 1], "factor": 3 / 8},
        {"offset": [1, 1], "factor": 2 / 8},
    ]


def jarvis() -> List[Dict[str, Any]]:
    """Jarvis-Judice-Ninke error diffusion kernel."""
    return [
        {"offset": [1, 0], "factor": 7 / 48},
        {"offset": [2, 0], "factor": 5 / 48},
        {"offset": [-2, 1], "factor": 3 / 48},
        {"offset": [-1, 1], "factor": 5 / 48},
        {"offset": [0, 1], "factor": 7 / 48},
        {"offset": [1, 1], "factor": 5 / 48},
        {"offset": [2, 1], "factor": 3 / 48},
        {"offset": [-2, 2], "factor": 1 / 48},
        {"offset": [-1, 2], "factor": 3 / 48},
        {"offset": [0, 2], "factor": 4 / 48},
        {"offset": [1, 2], "factor": 3 / 48},
        {"offset": [2, 2], "factor": 1 / 48},
    ]


def stucki() -> List[Dict[str, Any]]:
    """Stucki error diffusion kernel."""
    return [
        {"offset": [1, 0], "factor": 8 / 42},
        {"offset": [2, 0], "factor": 4 / 42},
        {"offset": [-2, 1], "factor": 2 / 42},
        {"offset": [-1, 1], "factor": 4 / 42},
        {"offset": [0, 1], "factor": 8 / 42},
        {"offset": [1, 1], "factor": 4 / 42},
        {"offset": [2, 1], "factor": 2 / 42},
        {"offset": [-2, 2], "factor": 1 / 42},
        {"offset": [-1, 2], "factor": 2 / 42},
        {"offset": [0, 2], "factor": 4 / 42},
        {"offset": [1, 2], "factor": 2 / 42},
        {"offset": [2, 2], "factor": 1 / 42},
    ]


def burkes() -> List[Dict[str, Any]]:
    """Burkes error diffusion kernel."""
    return [
        {"offset": [1, 0], "factor": 8 / 32},
        {"offset": [2, 0], "factor": 4 / 32},
        {"offset": [-2, 1], "factor": 2 / 32},
        {"offset": [-1, 1], "factor": 4 / 32},
        {"offset": [0, 1], "factor": 8 / 32},
        {"offset": [1, 1], "factor": 4 / 32},
        {"offset": [2, 1], "factor": 2 / 32},
    ]


def sierra3() -> List[Dict[str, Any]]:
    """Sierra-3 error diffusion kernel."""
    return [
        {"offset": [1, 0], "factor": 5 / 32},
        {"offset": [2, 0], "factor": 3 / 32},
        {"offset": [-2, 1], "factor": 2 / 32},
        {"offset": [-1, 1], "factor": 4 / 32},
        {"offset": [0, 1], "factor": 5 / 32},
        {"offset": [1, 1], "factor": 4 / 32},
        {"offset": [2, 1], "factor": 2 / 32},
        {"offset": [-1, 2], "factor": 2 / 32},
        {"offset": [0, 2], "factor": 3 / 32},
        {"offset": [1, 2], "factor": 2 / 32},
    ]


def sierra2() -> List[Dict[str, Any]]:
    """Sierra-2 error diffusion kernel."""
    return [
        {"offset": [1, 0], "factor": 4 / 16},
        {"offset": [2, 0], "factor": 3 / 16},
        {"offset": [-2, 1], "factor": 1 / 16},
        {"offset": [-1, 1], "factor": 2 / 16},
        {"offset": [0, 1], "factor": 3 / 16},
        {"offset": [1, 1], "factor": 2 / 16},
        {"offset": [2, 1], "factor": 1 / 16},
    ]


def sierra2_4a() -> List[Dict[str, Any]]:
    """Sierra-2-4A error diffusion kernel (lightweight)."""
    return [
        {"offset": [1, 0], "factor": 2 / 4},
        {"offset": [-2, 1], "factor": 1 / 4},
        {"offset": [-1, 1], "factor": 1 / 4},
    ]


# Map of diffusion kernel names to their functions
DIFFUSION_MAPS = {
    "floydSteinberg": floyd_steinberg,
    "falseFloydSteinberg": false_floyd_steinberg,
    "jarvis": jarvis,
    "stucki": stucki,
    "burkes": burkes,
    "sierra3": sierra3,
    "sierra2": sierra2,
    "Sierra2-4A": sierra2_4a,
}


def get_diffusion_map(name: str) -> List[Dict[str, Any]]:
    """
    Get a diffusion map by name.

    Args:
        name: Name of the diffusion kernel

    Returns:
        The diffusion map as a list of offset/factor dictionaries
    """
    if name in DIFFUSION_MAPS:
        return DIFFUSION_MAPS[name]()
    return floyd_steinberg()  # Default to Floyd-Steinberg

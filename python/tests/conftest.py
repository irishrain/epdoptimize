"""Pytest configuration and fixtures."""

import os
import sys

# Add the parent directory to the path so we can import epdoptimize
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

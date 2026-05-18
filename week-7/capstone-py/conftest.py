"""Root conftest.py — ensures the project root is on sys.path.

This file makes `pytest` work correctly from any working directory
and ensures `from src.xxx import yyy` resolves in all test files.
"""
import sys
import os

# Add project root to sys.path so `src` is importable
sys.path.insert(0, os.path.dirname(__file__))

"""
.. module:: python_minimizer
	:author: Alexander S. Groden
	:synopsis: Functional code for the python-minimizer.
"""


import types
import logging
from .minimizer import minimize
from .obfuscator import obfuscate


__all__ = [
	"minimizer",
	"obfuscator"
]

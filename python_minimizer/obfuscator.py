"""
.. module:: obfuscator
	:author: Alexander S. Groden
	:synopsis: Obfuscates Python code.
"""


import logging
from io import StringIO
from tokenize import generate_tokens


logger = logging.getLogger("python-minimizer.obfuscator")


# module functions #############################################################
def find_functions(sbuf):
	io_wrapper = StringIO(sbuf)
	for tok in generate_tokens(io_wrapper.readline):
		pass


def obfuscate():
	pass
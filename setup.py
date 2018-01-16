"""
"""


from setuptools import setup
import os.path


base = os.path.dirname(__file__)
with open(os.path.join(base, 'README.md'), 'r') as f:
	desc = f.read()


setup(
  name = 'python-minimizer',
  version = '1.0.2',
  description = "Minimizes Python code using Python's lexical scanning tokenize module.",
  long_description=desc,
  url = 'https://github.com/agroden/python-minimizer',
  author = 'Alexander Groden',
  author_email = 'alexander.groden@gmail.com',
  classifiers = [
  	'Development Status :: 5 - Production/Stable',
  	'Intended Audience :: Developers',
  	'Environment :: Console',
  	'Topic :: Software Development :: Build Tools', # sorta...
  	'Topic :: Software Development :: Libraries :: Python Modules',
  	'License :: OSI Approved :: MIT License',
  	'Programming Language :: Python :: 2',
  	'Programming Language :: Python :: 2.6',
  	'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4'
  ],
  keywords = 'minimization minification minimize minify mit-license',
  py_modules = ['minimizer'],
  entry_points={
  	'console_scripts': [
  		'python-minimizer=minimizer:main',
  	]
  }
)


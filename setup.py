"""
"""


from setuptools import setup
import os.path


base = os.path.dirname(__file__)
with open(os.path.join(base, 'README.md'), 'r') as f:
	desc = f.read()


setup(
  name = 'python-minimizer',
  version = '2.0.1',
  description = "Minimizes Python code using Python's lexical scanning tokenize module.",
  long_description=desc,
  long_description_content_type="text/markdown",
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
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8'
  ],
  keywords = 'minimization minification minimize minify mit-license',
  py_modules = ['minimizer'],
  entry_points={
  	'console_scripts': [
  		'python-minimizer=minimizer:main',
  	]
  }
)


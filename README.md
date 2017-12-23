# python-minimizer
Minimizes Python code using Python's lexical scanning tokenize module.
## Command-line usage
Currently python-minimizer supports the following options:
```sh
$ python minimizer.py -h
usage: minimizer.py [-h] [-o OUTPATH] [-b] [-c] [-d] [-s] [-w WHITESPACE_CHAR]
                    [-i INDENT_CHAR]
                    inpath

Minimizes Python code using Python's lexical scanning tokenize module.

positional arguments:
  inpath                The file to minimize

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPATH, --outpath OUTPATH
                        When specified, minimizer will output to the path
                        instead of stdout
  -b, --keep_blank_lines
                        When set, minimizer will not remove blank lines.
  -c, --keep_comments   When set, minimizer will not remove comment lines and
                        inline comments
  -d, --keep_docstrings
                        When set, minimizer will not remove docstrings
  -s, --keep_whitespace
                        When set, minimizer will not remove extraneous
                        whitespace
  -w WHITESPACE_CHAR, --whitespace_char WHITESPACE_CHAR
                        Set the whitespace character to use. Defaults to space
                        (" ")
  -i INDENT_CHAR, --indent_char INDENT_CHAR
                        Set the indentation character to use. Defaults to tab
                        ("\t")
  -r, --recursive       Treat the in-path and --out-path as directories to
                        minimize recursively

By default, the minimizer removes blank lines, comments, docstrings, and
extraneous whitespace. Where needed, it will insert a space (" ") for
whitespace between operators and use a tab ("\t") for indentation. Use the
command line switches to change any of the defaults.
```
## Library usage
Of course, you can also import the minimizer module and use it as follows:
```python
from minimizer import minimize
with open(code_file, 'r') as f:
    code = f.read()
minimized_code = minimize(code)
with open(minimized_file, 'w') as f:
    f.write(minimized_code)
```
By default, the ```minimize``` function will remove blank lines, comments, docstrings, and whitespace between operators and uses a space (" ") for the whitespace character and a tab ("\t") for the indent character, but accepts keyword arguments to change these options.

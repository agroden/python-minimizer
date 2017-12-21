# python-minimizer
Minimizes Python code using Python's lexical scanning tokenize module.
## Command-line usage
Currently python-minimizer supports the following options:
```sh
$ python minimizer.py -h
usage: minimizer.py [-h] [-o OUTPATH] [-b] [-c] [-d] [-s] [-w WHITESPACE_CHAR]
                    [-i INDENT_CHAR]
                    inpath
                    
positional arguments:
  inpath

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPATH, --outpath OUTPATH
  -b, --keep_blank_lines
  -c, --keep_comments
  -d, --keep_docstrings
  -s, --keep_whitespace
  -w WHITESPACE_CHAR, --whitespace_char WHITESPACE_CHAR
  -i INDENT_CHAR, --indent_char INDENT_CHAR
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

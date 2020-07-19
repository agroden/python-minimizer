"""
.. module:: main
	:author: Alexander S. Groden
	:synopsis: Drives the minimizer.
"""


import logging
from python_minimizer import (
	minimize,
	obfuscate
)


logger = logging.getLogger("python-minimizer")


def main():
	from argparse import ArgumentParser
	import os
	from shutil import copy2
	import sys
	parser = ArgumentParser(
		description='Minimizes Python code using Python\'s lexical scanning tokenize module.''',
		epilog='By default, the minimizer removes blank lines, comments, docstrings, and extraneous whitespace. Where needed, it will insert a space (\" \") for whitespace between operators and use a tab (\"\\t\") for indentation. Use the command line switches to change any of the defaults.'
	)
	parser.add_argument('in_path', help='The file to minimize')
	parser.add_argument('-o', '--out-path', default=None,
		help='When specified, minimizer will output to the path instead of stdout')
	parser.add_argument('-b', '--keep-blank-lines', default=True,
		action='store_false', help='When set, minimizer will not remove blank lines.')
	parser.add_argument('-c', '--keep-comments', default=True,
		action='store_false', help='When set, minimizer will not remove comment lines and inline comments')
	parser.add_argument('-d', '--keep-docstrings', default=True,
		action='store_false', help='When set, minimizer will not remove docstrings')
	parser.add_argument('-s', '--keep-whitespace', default=True,
		action='store_false', help='When set, minimizer will not remove extraneous whitespace')
	parser.add_argument('-w', '--whitespace-char', default=' ', type=str,
		help='Set the whitespace character to use. Defaults to space (\" \")')
	parser.add_argument('-i', '--indent-char', default='\t', type=str,
		help='Set the indentation character to use. Defaults to tab (\"\\t\")')
	parser.add_argument('-r', '--recursive', default=False, action='store_true',
		help='Treat the in-path and --out-path as directories to minimize recursively')
	parser.add_argument('-v', '--verbose', default=0, action='count',
		help='Explain what we are doing as we do it, higher levels are useful for debugging')
	args = parser.parse_args()

	logging.basicConfig(format='%(levelname)s: %(message)s')
	logger.setLevel(logging.INFO)
	if args.verbose > 1:
		logger.setLevel(logging.DEBUG)

	def minimize_file(path, args):
		sbuf = ''
		with open(path, 'r') as f:
			sbuf = f.read()
		return minimize(
			sbuf,
			args.keep_blank_lines,
			args.keep_comments,
			args.keep_docstrings,
			args.keep_whitespace,
			args.whitespace_char,
			args.indent_char
		)
	
	if args.recursive: # in_path is a directory
		if not os.path.exists(args.in_path):
			print('ERROR: Given in path does not exist')
			sys.exit(-1)
		if not os.path.isdir(args.in_path):
			print('ERROR: Given in path is not a directory')
			sys.exit(-1)
		args.in_path = os.path.normpath(args.in_path + os.sep)
		if args.out_path:
			if os.path.exists(args.out_path) and not os.path.isdir(args.out_path):
				print('ERROR: Given out path is not a directory')
				sys.exit(-1)
			args.out_path = os.path.normpath(args.out_path + os.sep)
		for root, _, fnames in os.walk(args.in_path):
			for fname in fnames:
				src_path = os.path.join(root, fname)
				if args.out_path:
					if os.path.exists(args.out_path) and not os.path.isdir(args.out_path):
						print('ERROR: Given out path is not a directory')
						sys.exit(-1)
					out_root = root.replace(args.in_path, args.out_path)
					dst_path = os.path.join(out_root, fname)
					if not os.path.exists(os.path.join(out_root)):
						os.makedirs(out_root)
					if fname.lower().endswith('.py'):
						mini = minimize_file(src_path, args)
						with open(dst_path, 'w') as f:
							f.write(mini)
					else:
						copy2(src_path, dst_path)
				elif fname.lower().endswith('.py'):
					print('{}:'.format(src_path))
					mini = minimize_file(src_path, args)
					print('{}\n'.format(mini))
	else: # in_path is a single file
		if not os.path.exists(args.in_path):
			print('ERROR: Given in path does not exist')
			sys.exit(-1)
		if not os.path.isfile(args.in_path):
			print('ERROR: Given in path is not a file')
			sys.exit(-1)
		mini = minimize_file(args.in_path, args)
		if args.out_path:
			if os.path.exists(args.out_path) and not os.path.isfile(args.out_path):
				print('ERROR: Given out path is not a file')
				sys.exit(-1)
			with open(args.out_path, 'w') as f:
				f.write(mini)
		else:
			print(mini)
			

if __name__ == '__main__':
	main()
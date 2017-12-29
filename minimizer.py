"""
.. module:: minimizer
	:author: Alexander S. Groden
	:synopsis: Minimizes Python code using Python's lexical scanning tokenize module.
"""


from __future__ import print_function
import logging
from token import *
from tokenize import *
from StringIO import StringIO


logger = logging.getLogger(__name__)


# classes / helpers ############################################################
def enum(*sequential, **named):
	"""Makes an enum type with a reverse mapping for lookup of the enum string.
	Included for portability sake.
	Taken from: https://stackoverflow.com/a/1695250
	"""
	enums = dict(zip(sequential, range(len(sequential))), **named)
	reverse = dict((value, key) for key, value in enums.iteritems())
	enums['reverse_mapping'] = reverse
	return type('Enum', (), enums)
	

class TokenGroup(object):
	"""A class for keeping track of a group of tokens.
	Token groups are meant to be a collection of tokens that are lexagraphically 
	adjacent on a line. This helps to easily remove comments, docstrings, and 
	blank lines.
	"""
	Type = enum('UNKNOWN', 'CODE', 'CODE_INLINE_COMMENT', 'COMMENT', 'DOCSTRING',
		'BLANK_LINE', 'SHEBANG', 'INDENT', 'DEDENT', 'EOF')
	
	_WORD_OPS = ('and', 'or', 'not', 'is', 'in', 'for', 'while', 'return')
	def __init__(self):
		self._tokens = []
		self._finalized = False
		self.type = TokenGroup.Type.UNKNOWN
		
	def untokenize(self, rmwspace=False, wspace_char=' '):
		"""Untokenize this group.
		"""
		ret = ''
		prev = None
		for tok in self._tokens:
			if tok[0] != NEWLINE and tok[0] != NL:
				if prev:
					if rmwspace:
						if (prev[0] == NAME and tok[0] == NAME) or \
							 (prev[0] == OP and tok[1] in self._WORD_OPS) or \
							 (tok[0] in (OP, STRING) and prev[1] in self._WORD_OPS):
							ret = ''.join([ret, wspace_char])
					else:
						# tok[2][1]: start column, prev[3][1]: end column
						# the difference between the two indicates whitespace
						if prev and tok[2][1] > prev[3][1]:
							ret = ''.join([ret, wspace_char * (tok[2][1] - prev[3][1])])
				ret = ''.join([ret, tok[1].rstrip()])
			prev = tok
		return ret
		
	def append(self, tok):
		"""Append a token to this group. Will update the group type as needed.
		"""
		def get_type(t):
			if t[0] == NAME or tok[0] == OP:
				return TokenGroup.Type.CODE
			elif t[0] == COMMENT:
				if t[1].startswith('#!'):
					return TokenGroup.Type.SHEBANG
				return TokenGroup.Type.COMMENT
			elif t[0] == STRING:
				return TokenGroup.Type.DOCSTRING
			elif t[0] == NL:
				return TokenGroup.Type.BLANK_LINE
			elif t[0] == INDENT:
				return TokenGroup.Type.INDENT
			elif t[0] == DEDENT:
				return TokenGroup.Type.DEDENT
			elif t[0] == ENDMARKER:
				return TokenGroup.Type.EOF
		# function body #
		self._tokens.append(tok)
		if self.type == TokenGroup.Type.UNKNOWN:
			self.type = get_type(tok)
		elif self.type == TokenGroup.Type.CODE and tok[0] == COMMENT:
			self.type = TokenGroup.Type.CODE_INLINE_COMMENT
		elif self.type == TokenGroup.Type.BLANK_LINE:
			self.type = get_type(tok)
		elif self.type == TokenGroup.Type.DOCSTRING and tok[0] not in (STRING, NEWLINE):
			self.type = get_type(tok)
			
	def __str__(self):
		"""Prints TokenGroup information for easier debugging.
		"""
		def readable_token(tok):
			return '({}, {}, {}, {}, {})'.format(
				tok_name[tok[0]], repr(tok[1]), tok[2], tok[3], repr(tok[4])
			)
		# function body #
		return 'TokenGroup {{ type: {}, tokens: [{}] }}'.format(
			TokenGroup.Type.reverse_mapping[self.type],
			', '.join([readable_token(tok) for tok in self._tokens])
		)
		

# module functions #############################################################
def group_tokens(sbuf):
	"""Groups tokens by line. Splits indents and dedents into their own group.
	"""
	io_wrapper = StringIO(sbuf)
	groups = []
	group = TokenGroup()
	bracket_ctr = 0
	for tok in generate_tokens(io_wrapper.readline):
		if tok[0] == OP and tok[1] in ('(', '[', '{'):
			bracket_ctr += 1
		elif tok[0] == OP and tok[1] in (')', ']', '}'):
			bracket_ctr -= 1
		# if we have a bracket that isn't closed, keep the group open
		if tok[0] in (NEWLINE, NL, ENDMARKER, INDENT, DEDENT) and bracket_ctr == 0:
			group.append(tok)
			groups.append(group)
			if verbose > 1:
				logger.debug('Closed token group: {}'.format(group))
			group = TokenGroup()
		else:
			group.append(tok)
	return groups
	

def untokenize(tgroups, rmwspace=False, wspace_char = ' ', indent_char='\t'):
	"""Untokenizes groups of tokens into a string.
	Can optionally remove whitespace and change the whitespace and indent character.
	"""
	ret = []
	indent_lvl = 0
	for grp in tgroups:
		if grp.type == TokenGroup.Type.INDENT:
			indent_lvl += 1
			continue
		elif grp.type == TokenGroup.Type.DEDENT:
			indent_lvl -= 1
			continue
		elif grp.type == TokenGroup.Type.EOF:
			continue
		ret.append(
			''.join([indent_char*indent_lvl, grp.untokenize(rmwspace, wspace_char)])
		)
	return '\n'.join(ret)
	

def remove_blank_lines(token_groups):
	"""Removes blank lines from the token groups.
	"""
	base_len = len(token_groups)
	ret = [grp for grp in token_groups if grp.type != TokenGroup.Type.BLANK_LINE]
	if verbose > 0:
		logger.info('Removed {} blank lines'.format(base_len - len(ret)))
	return ret
	

def remove_docstrings(token_groups):
	"""Removes docstrings from the token groups.
	"""
	base_len = len(token_groups)
	ret = [grp for grp in token_groups if grp.type != TokenGroup.Type.DOCSTRING]
	if verbose > 0:
		logger.info('Removed {} docstrings'.format(base_len - len(ret)))
	return ret
	

def remove_comments(token_groups):
	"""Removes comment lines and inline comments from the token groups.
	"""
	base_len = len(token_groups)
	inline_comment_ctr = 0
	tmp = []
	for grp in token_groups:
		if grp.type == TokenGroup.Type.CODE_INLINE_COMMENT:
			group = TokenGroup()
			for tok in grp._tokens:
				if tok[0] != COMMENT:
					group.append(tok)
					inline_comment_ctr += 1
			tmp.append(group)
		else:
			tmp.append(grp)
	ret = [grp for grp in tmp if grp.type != TokenGroup.Type.COMMENT]
	if verbose > 0:
		logger.info('Removed {} comments and {} inline comments'.format(
			base_len - len(ret), inline_comment_ctr))
	return ret
	

def minimize(sbuf, rm_blank_lines=True, rm_comments=True, rm_docstrings=True, rm_whitespace=True, whitespace_char=' ', indent_char='\t'):
	"""Convenience function for performing all the possible minimization functions.
	"""
	grps = group_tokens(sbuf)
	if rm_blank_lines:
		grps = remove_blank_lines(grps)
	if rm_comments:
		grps = remove_comments(grps)
	if rm_docstrings:
		grps = remove_docstrings(grps)
	return untokenize(grps, rm_whitespace, whitespace_char, indent_char)
	

# execution ####################################################################
def main():
	from argparse import ArgumentParser
	import os
	from shutil import copy2
	import sys
	global verbose
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
	verbose = args.verbose
	logging.basicConfig(format='%(levelname)s: %(message)s')
	logger.setLevel(logging.INFO)
	if verbose > 1:
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
		for root, dirs, fnames in os.walk(args.in_path):
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
	


"""
.. module:: minimizer
	:author: Alexander S. Groden
	:synopsis: Minimizes Python code using Python's lexical scanning tokenize module.
"""

from __future__ import print_function
from token import *
from tokenize import *
from StringIO import StringIO


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
				if prev and tok[2][1] > prev[3][1]:
					if (prev and prev[0] == NAME and tok[0] == NAME) or not rmwspace:
						ret = ''.join([ret, wspace_char])
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
		self._tokens.append(tok)
		if self.type == TokenGroup.Type.UNKNOWN:
			self.type = get_type(tok)
		elif self.type == TokenGroup.Type.CODE and tok[0] == COMMENT:
			self.type = TokenGroup.Type.CODE_INLINE_COMMENT
		elif self.type == TokenGroup.Type.BLANK_LINE:
			self.type = get_type(tok)
		elif self.type == TokenGroup.Type.DOCSTRING and tok[0] != STRING and tok[0] != NEWLINE:
			self.type = get_type(tok)
			
	def _readable_token(self, tok):
		return '({}, {}, {}, {}, {})'.format(
			tok_name[tok[0]], repr(tok[1]), tok[2], tok[3], repr(tok[4])
		)
			
	def __str__(self):
		def readable_token(self, tok):
			return '({}, {}, {}, {}, {})'.format(
				tok_name[tok[0]], repr(tok[1]), tok[2], tok[3], repr(tok[4])
			)
		return 'TokenGroup {{ type: {}, tokens: [{}] }}'.format(
			TokenGroup.Type.reverse_mapping[self.type],
			', '.join([readable_token(tok) for tok in self._tokens])
		)


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


def group_tokens(sbuf):
	"""Groups tokens by line. Splits indents and dedents into their own group.
	"""
	io_wrapper = StringIO(sbuf)
	groups = []
	group = TokenGroup()
	for tok in generate_tokens(io_wrapper.readline):
		if tok[0] == NEWLINE or tok[0] == NL or tok[0] == ENDMARKER or tok[0] == INDENT or tok[0] == DEDENT:
			group.append(tok)
			groups.append(group)
			group = TokenGroup()
		else:
			group.append(tok)
	return groups


def remove_blank_lines(tokens):
	"""Removes blank lines from the token groups.
	"""
	return [grp for grp in tokens if grp.type != TokenGroup.Type.BLANK_LINE]
	

def remove_docstrings(tokens):
	"""Removes docstrings from the token groups.
	"""
	return [grp for grp in tokens if grp.type != TokenGroup.Type.DOCSTRING]
	

def remove_comments(tokens):
	"""Removes comment lines and inline comments from the token groups.
	"""
	ret = []
	for grp in tokens:
		if grp.type == TokenGroup.Type.CODE_INLINE_COMMENT:
			group = TokenGroup()
			for tok in grp._tokens:
				if tok[0] != COMMENT:
					group.append(tok)
			ret.append(group)
		else:
			ret.append(grp)
	return [grp for grp in ret if grp.type != TokenGroup.Type.COMMENT]
	

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
	

if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('inpath')
	parser.add_argument('-o', '--outpath', default=None)
	parser.add_argument('-b', '--keep_blank_lines', default=True,
		action='store_false')
	parser.add_argument('-c', '--keep_comments', default=True,
		action='store_false')
	parser.add_argument('-d', '--keep_docstrings', default=True,
		action='store_false')
	parser.add_argument('-s', '--keep_whitespace', default=True,
		action='store_false')
	parser.add_argument('-w', '--whitespace_char', default=' ', type=str)
	parser.add_argument('-i', '--indent_char', default='\t', type=str)
	args = parser.parse_args()
	sbuf = ''
	with open(args.inpath, 'r') as f:
		sbuf = f.read()
	ret = minimize(
		sbuf,
		args.keep_blank_lines,
		args.keep_comments,
		args.keep_docstrings,
		args.keep_whitespace,
		args.whitespace_char,
		args.indent_char
	)
	# TODO: check if this is a valid path herr durr
	if args.outpath:
		with open(args.outpath, 'w') as f:
			f.write(ret)
	else:
		print(ret)
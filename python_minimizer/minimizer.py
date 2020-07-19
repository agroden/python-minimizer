"""
.. module:: minimizer
	:author: Alexander S. Groden
	:synopsis: Minimizes Python code using Python's lexical scanning tokenize module.
"""


import logging
from typing import Tuple, Iterable, List
from token import (
	COMMENT,
	DEDENT,
	ENDMARKER,
	INDENT,
	NEWLINE,
	NL,
	NAME,
	NUMBER,
	OP,
	STRING,
	tok_name
)
from tokenize import generate_tokens
from io import StringIO
from enum import Enum, auto


logger = logging.getLogger("python-minimizer.minimizer")


# type hint types #############################################################
# this is based on the return type as specified here:
# https://docs.python.org/3/library/tokenize.html#tokenize.tokenize
TokenType = Tuple[int, str, Tuple[int, int], Tuple[int, int], int]


# classes / helpers ###########################################################
class TokenGroup:
	"""A class for keeping track of a group of tokens.
	Token groups are meant to be a collection of tokens that are lexagraphically 
	adjacent on a line. This helps to easily remove comments, docstrings, and 
	blank lines.
	"""
	class Type(Enum):
		UNKNOWN = auto()
		CODE = auto()
		CODE_INLINE_COMMENT = auto()
		COMMENT = auto()
		DOCSTRING = auto()
		BLANK_LINE = auto()
		SHEBANG = auto()
		INDENT = auto()
		DEDENT = auto()
		EOF = auto()
	
	_WORD_OPS = ('and', 'or', 'not', 'is', 'in', 'for', 'while', 'return')
	def __init__(self):
		self._tokens = []
		self._finalized = False
		self.type = TokenGroup.Type.UNKNOWN

	def untokenize(self, rmwspace: bool = False, wspace_char: str = ' ') -> str:
		"""Untokenize this group.
		"""
		ret = ''
		prev = []
		for tok in self._tokens:
			if tok[0] != NEWLINE and tok[0] != NL:
				if len(prev) != 0:
					if rmwspace:
						if (prev[0] in (NAME, NUMBER) and tok[0] in (NAME, NUMBER)) or \
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
		
	def append(self, tok: TokenType) -> None:
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
			
	def __str__(self) -> str:
		"""Prints TokenGroup information for easier debugging.
		"""
		def readable_token(tok):
			return '({}, {}, {}, {}, {})'.format(
				tok_name[tok[0]], repr(tok[1]), tok[2], tok[3], repr(tok[4])
			)
		# function body #
		return 'TokenGroup {{ type: {}, tokens: [{}] }}'.format(
			self.type.name,
			', '.join([readable_token(tok) for tok in self._tokens])
		)
		

# module functions ############################################################
def group_tokens(sbuf: str) -> List[TokenGroup]:
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
			logger.debug('Closed token group: {}'.format(group))
			group = TokenGroup()
		else:
			group.append(tok)
	return groups
	

def untokenize(tgroups: Iterable[TokenGroup], rmwspace: bool = False,
		wspace_char: str = ' ', indent_char:str = '\t') -> str:
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
			''.join([indent_char * indent_lvl, grp.untokenize(rmwspace, wspace_char)])
		)
	return '\n'.join(ret)
	

def remove_blank_lines(token_groups: Iterable[TokenGroup]) -> List[TokenGroup]:
	"""Removes blank lines from the token groups.
	"""
	base_len = len(token_groups)
	ret = [grp for grp in token_groups if grp.type != TokenGroup.Type.BLANK_LINE]
	logger.info('Removed {} blank lines'.format(base_len - len(ret)))
	return ret
	

def remove_docstrings(token_groups: Iterable[TokenGroup]) -> List[TokenGroup]:
	"""Removes docstrings from the token groups.
	"""
	base_len = len(token_groups)
	ret = [grp for grp in token_groups if grp.type != TokenGroup.Type.DOCSTRING]
	logger.info('Removed {} docstrings'.format(base_len - len(ret)))
	return ret
	

def remove_comments(token_groups: Iterable[TokenGroup]) -> List[TokenGroup]:
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
	logger.info('Removed {} comments and {} inline comments'.format(
		base_len - len(ret),
		inline_comment_ctr
	))
	return ret
	

def minimize(sbuf: str, rm_blank_lines: bool = True, rm_comments: bool = True,
		rm_docstrings: bool = True, rm_whitespace: bool = True, whitespace_char: str = ' ',
		indent_char: str = '\t') -> str:
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

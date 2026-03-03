import re
import sys
from typing import Generator, NamedTuple, List

# v1.1.2 Lexer: Comprehensive tokenization with enhanced error handling for Solas v1.1 compliance.
# Bracket Awareness: LBRACKET and RBRACKET tokens enable the Lexer to recognize evolution sets and nested structures.
# Quote Handling: The STRING rule supports both single and double quote literals.
# Resource Priority and Validation: The RESOURCE rule ensures @ prefix and valid naming.
# Filter Logic: It explicitly flags if, else, or, and and as ILLEGAL_LOG

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

class SolasLexicalError(Exception):
    pass

class SolasLexer:
    def __init__(self):
        self.indent_stack = [0]
        # v1.1.2 Patterns: Aligned with EBNF Atomic requirements
        self.rules = [
            ('COMMENT',    r'//.*'),
            ('RESOURCE',   r'@[a-zA-Z_][\w]*'),        # EBNF: @prefix
            ('KEYWORD',    r'\b(stream|shape|as|emit|refract|on|evolve|logic|drift|to|grow|init|step|is)\b'),
            ('ILLEGAL_LOG', r'\b(if|else|or|and|not|while|for)\b'), # Dark Logic Gate
            ('TYPE',       r'\b(UUID|String|Number|Boolean|Timestamp)\b'),
            ('ID',         r'[a-zA-Z_][\w]*'),
            ('NUMBER',     r'\d+(\.\d+)?([eE][+-]?\d+)?'),
            ('STRING',     r'["\'](.*?)["\']'),        # Support for ' and "
            ('OP',         r'->|==|!=|>=|<=|[+*/%><=-]'),
            ('LBRACKET',   r'\['),                     # EBNF: Evolution Sets
            ('RBRACKET',   r'\]'),
            ('COLON',      r':'),
            ('DOT',        r'\.'),
            ('COMMA',      r','),
            ('NEWLINE',    r'\n'),
            ('SKIP',       r'[ \t]+'),
            ('DEPRECATED', r'[{}]'),                   # Braces are Dark Logic
            ('MISMATCH',   r'.'),                      # Catch-all for illegal atoms
        ]
        self.master_pattern = re.compile('|'.join(f'(?P<{k}>{p})' for k, p in self.rules))

    def _sync_depth(self, line: str, line_num: int) -> Generator[Token, None, None]:
        """Calculates Indent/Dedent tokens based on leading whitespace."""
        whitespace = len(line) - len(line.lstrip(' '))
        if whitespace > self.indent_stack[-1]:
            self.indent_stack.append(whitespace)
            yield Token('INDENT', ' ' * whitespace, line_num, 0)
        elif whitespace < self.indent_stack[-1]:
            while whitespace < self.indent_stack[-1]:
                self.indent_stack.pop()
                yield Token('DEDENT', '', line_num, 0)
            if whitespace != self.indent_stack[-1]:
                raise SolasLexicalError(f"Line {line_num}: Inconsistent indentation.")

    def tokenize(self, code: str) -> Generator[Token, None, None]:
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                if not stripped: yield Token('NEWLINE', '\n', i, 0)
                continue

            yield from self._sync_depth(line, i)

            for match in self.master_pattern.finditer(line.lstrip(' ')):
                kind = match.lastgroup
                val = match.group()
                col = match.start() + (len(line) - len(line.lstrip(' ')))

                if kind == 'SKIP' or kind == 'COMMENT': continue
                if kind == 'DEPRECATED': raise SolasLexicalError(f"Line {i}: Braces deprecated.")
                if kind == 'ILLEGAL_LOG': raise SolasLexicalError(f"Line {i}: Dark Logic '{val}' detected.")
                if kind == 'MISMATCH': raise SolasLexicalError(f"Line {i}: Illegal character '{val}'.")

                yield Token(kind, val, i, col)
            yield Token('NEWLINE', '\n', i, len(line))

        # Finalize structural scope
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            yield Token('DEDENT', '', len(lines), 0)
        yield Token('EOF', '', len(lines), 0)
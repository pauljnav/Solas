import re
import sys
from typing import Generator, NamedTuple, List

# v1.1.3 Lexer: Pure Identity Machine
# Reclassification: All keywords (Dark or Light) are now identified as KEYWORD.
# Parser Empowerment: By reporting forbidden keywords, it allows the Parser to enforce philosophical guards.
# Mechanical Robustness: Fixed the OP regex to prevent range errors and added LPAREN/RPAREN.
# EBNF Parity: Full atomic recognition for [], (), @, and both quote types.

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
        # v1.1.3 Rules: Ordered for maximum specificity and mechanical safety
        self.rules = [
            ('COMMENT',     r'//.*'),
            ('RESOURCE',    r'@[a-zA-Z_][\w]*'),        # EBNF: @resource pointers
            ('KEYWORD',     r'\b(stream|shape|as|emit|refract|on|evolve|logic|drift|to|grow|init|step|is|and|if|else|or|not|while|for)\b'),
            ('TYPE',        r'\b(UUID|String|Number|Boolean|Timestamp)\b'),
            ('ID',          r'[a-zA-Z_][\w]*'),
            ('NUMBER',      r'\d+(\.\d+)?([eE][+-]?\d+)?'),
            ('STRING',      r'["\'](.*?)["\']'),        # Captured for Parser interpretation
            ('OP',          r'->|==|!=|>=|<=|[+*/%><=]|-(?!>)'), # Robust hyphen vs arrow handling
            ('LPAREN',      r'\('),
            ('RPAREN',      r'\)'),
            ('LBRACKET',    r'\['),                     # Evolution/Collection sets
            ('RBRACKET',    r'\]'),
            ('COLON',       r':'),
            ('DOT',         r'\.'),
            ('COMMA',       r','),
            ('NEWLINE',     r'\n'),
            ('SKIP',        r'[ \t]+'),
            ('MISMATCH',    r'.'),
        ]
        self.master_pattern = re.compile('|'.join(f'(?P<{k}>{p})' for k, p in self.rules))

    def _sync_depth(self, line: str, line_num: int) -> Generator[Token, None, None]:
        """Manages the off-side rule for Solas' linear structural flow."""
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
            # Handle empty lines and standalone comments
            if not stripped or stripped.startswith('//'):
                yield Token('NEWLINE', '\n', i, 0)
                continue

            yield from self._sync_depth(line, i)

            # Tokenize the actual content
            for match in self.master_pattern.finditer(line.lstrip(' ')):
                kind = match.lastgroup
                val = match.group()
                col = match.start() + (len(line) - len(line.lstrip(' ')))

                if kind == 'SKIP' or kind == 'COMMENT':
                    continue

                # The Lexer identifies atoms; the Parser will now judge them.
                if kind == 'MISMATCH':
                    raise SolasLexicalError(f"Line {i}: Illegal character '{val}'.")

                yield Token(kind, val, i, col)
            yield Token('NEWLINE', '\n', i, len(line))

        # Close all open structural scopes
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            yield Token('DEDENT', '', len(lines), 0)
        yield Token('EOF', '', len(lines), 0)
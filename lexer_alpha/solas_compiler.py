import re
import sys
from typing import NamedTuple, Generator

class SolasLexer:
    """
    Solas Alpha Lexer v0.2
    Enforces: Intent-driven tokens, @resource mapping, and complexity limits.
    and
    """
    def __init__(self):
        self.rules = [
            # 1. HIGH PRIORITY: PROHIBITED (Dark Logic)
            ('ILLEGAL_OR',      r'\bor\b'),
            ('ILLEGAL_STATE',   r'\+\+|--|[+\-*/%&|^]='),
            ('ILLEGAL_BRANCH',  r'\?'),
            ('ILLEGAL_BITWISE', r'[&|^~]|<<|>>'),

            # 2. STRINGS & COMMENTS (Literal isolation)
            ('COMMENT',         r'//.*'),
            ('STRING',          r'"[^"]*"'), # [cite: 83]

            # 3. RESOURCE POINTERS (EBNF Sec 8)
            ('RESOURCE_ROOT',   r'@(net|data|math|core|env|cache)\b'), # [cite: 41-46]

            # 4. KEYWORDS & TYPES (EBNF Sec 11)
            ('KEYWORD',         r'\b(stream|emit|grow|refract|shape|drift|if|on|to|as|init|step|while|evolve|logic|and)\b'), # [cite: 73-75]
            ('TYPE',            r'\b(String|Number|Boolean|UUID|Blob)\b'), # [cite: 32-36]

            # 5. OPERATORS & PUNCTUATION (EBNF Sec 10)
            ('NUMBER',          r'\d+(\.\d+)?([eE][+-]?\d+)?'), # [cite: 84 extended]
            ('FLOW_OP',         r'->'), # [cite: 85]
            ('COMPARATOR',      r'==|!=|>=|<=|>|<|\bis\b(\s+not)?'), # [cite: 65, 78-79]
            ('IDENTIFIER',      r'[a-zA-Z_][a-zA-Z0-9_]*'), #

            # 6. STRUCTURAL TOKENS
            ('LBRACE',          r'\{'),
            ('RBRACE',          r'\}'),
            ('LPAREN',          r'\('),
            ('RPAREN',          r'\)'),
            ('LBRACKET',        r'\['),
            ('RBRACKET',        r'\]'),
            ('COLON',           r':'), # [cite: 85]
            ('COMMA',           r','), # [cite: 85]
            ('DOT',             r'\.'), # [cite: 85]

            # 7. WHITESPACE (Significant for INDENT/DEDENT)
            ('NEWLINE',         r'\n'),
            ('SKIP',            r'[ \t]+'),

            # 8. THE LOCKDOWN: Anything else is a Hard Mismatch
            ('MISMATCH',        r'.'),
        ]
        self.regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in self.rules))

    def tokenize(self, code):
        for match in self.regex.finditer(code):
            kind = match.lastgroup
            value = match.group()
            if kind in ('SKIP', 'COMMENT', 'NEWLINE'): continue
            yield kind, value

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solas_compiler.py <file.solas>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        content = f.read()
        lexer = SolasLexer()
        print(f"{'TOKEN TYPE':<15} | {'VALUE'}")
        print("-" * 30)
        for kind, val in lexer.tokenize(content):
            print(f"{kind:<15} | {val}")
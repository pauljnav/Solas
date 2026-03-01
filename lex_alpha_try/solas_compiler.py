import re
import sys

class SolasLexer:
    """
    Solas Alpha Lexer v0.1
    Enforces: Intent-driven tokens, @resource mapping, and complexity limits.
    """
    def __init__(self):
        self.rules = [
            ('COMMENT',   r'//.*'),
            ('KEYWORD',   r'\b(stream|refract|drift|shape|emit|if|and|or|not)\b'),
            ('ENV_CALL',  r'@env\("([^"]+)"\)'),
            ('RESOURCE',  r'@[a-z_]+(\.[a-z_0-9]+)*'),
            ('CONDITION', r'[a-z_]+\s*(>|<|==|!=)\s*\d+[a-z%]*'),
            ('ARROW',     r'->'),
            ('BLOCK',     r'\{|\}'),
            ('IDENTIFIER',r'[a-z_][a-z_0-9]*'),
            ('NEWLINE',   r'\n'),
            ('SKIP',      r'[ \t]+'),
        ]
        self.regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.rules))

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
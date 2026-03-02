import re
import sys
from typing import NamedTuple, Generator, List, Final

class SolasLexicalError(Exception):
    """Total Lockdown violation."""
    pass

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

class SolasLexer:
    """
    Solas Lexer v1.1 - Depth-Sync Implementation.
    Mathematically synchronizes block depth to the 4-space mandate.
    """
    INDENT_SIZE: Final[int] = 4

    def __init__(self):
        self.indent_stack: List[int] = [0] # Stack stores 'depth' levels (0, 1, 2...)

        self.rules = [
            ('DEPRECATED',  r'[\{\}]'),
            ('ILLEGAL_LOG', r'\b(or|if|else|elif)\b|\?|\+\+|--|[+\-*/%&|^]='),
            ('COMMENT',     r'//.*'),
            ('STRING',      r'"[^"]*"'),
            ('RESOURCE',    r'@(net|data|math|core|env|cache)\b'),
            ('KEYWORD',     r'\b(stream|emit|grow|refract|shape|drift|on|error|to|as|init|step|while|evolve|logic|and)\b'),
            ('TYPE',        r'\b(String|Number|Boolean|UUID|Blob)\b'),
            ('NUMBER',      r'\d+(\.\d+)?([eE][+-]?\d+)?'),
            ('COMPARATOR',  r'==|!=|>=|<=|>|<|\bis\b(\s+not)?'),
            ('FLOW_OP',     r'->'),
            ('ID',          r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('LPAREN',      r'\('),
            ('RPAREN',      r'\)'),
            ('COLON',       r':'),
            ('COMMA',       r','),
            ('DOT',         r'\.'),
            ('NEWLINE',     r'\n'),
            ('SKIP',        r'[ ]+'),
            ('MISMATCH',    r'.'),
        ]
        self.master_pattern = re.compile('|'.join(f'(?P<{n}>{p})' for n, p in self.rules))

    def _sync_depth(self, line: str, line_num: int) -> Generator[Token, None, None]:
        """Synchronizes current line indentation depth with the stack."""
        if '\t' in line:
            raise SolasLexicalError(f"Line {line_num}: Tabs are forbidden.")

        # Calculate depth index
        leading_spaces = len(re.match(r'^[ ]*', line).group(0))
        depth, partial = divmod(leading_spaces, self.INDENT_SIZE)

        if partial:
            raise SolasLexicalError(f"Line {line_num}: Indent ({leading_spaces}) is not a multiple of {self.INDENT_SIZE}.")

        current_depth = len(self.indent_stack) - 1

        # Level Sync: INDENT
        while depth > current_depth:
            current_depth += 1
            self.indent_stack.append(current_depth)
            yield Token('INDENT', ' ' * self.INDENT_SIZE, line_num, current_depth * self.INDENT_SIZE)

        # Level Sync: DEDENT
        while depth < current_depth:
            self.indent_stack.pop()
            current_depth -= 1
            yield Token('DEDENT', '', line_num, leading_spaces)

    def tokenize(self, code: str) -> Generator[Token, None, None]:
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                continue

            # 1. Structural Sync
            yield from self._sync_depth(line, i)

            # 2. Token Matching
            for match in self.master_pattern.finditer(line.lstrip(' ')):
                kind = match.lastgroup
                val = match.group()
                col = match.start() + (len(line) - len(line.lstrip(' ')))

                if kind in ('SKIP', 'COMMENT'): continue
                if kind == 'DEPRECATED': raise SolasLexicalError(f"Line {i}: Braces deprecated.")
                if kind == 'ILLEGAL_LOG': raise SolasLexicalError(f"Line {i}: Dark Logic '{val}' detected.")
                if kind == 'MISMATCH': raise SolasLexicalError(f"Line {i}: Illegal character '{val}'.")

                yield Token(kind, val, i, col)
            yield Token('NEWLINE', '\n', i, len(line))

        # Final EOF dedents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            yield Token('DEDENT', '', len(lines), 0)
        yield Token('EOF', '', len(lines), 0)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    try:
        with open(sys.argv[1], 'r') as f:
            lexer = SolasLexer()
            for t in lexer.tokenize(f.read()):
                print(f"{t.line}:{t.column}\t{t.type:<15} | {repr(t.value)}")
    except SolasLexicalError as e:
        print(f"LOCKDOWN ERROR: {e}", file=sys.stderr)
        sys.exit(1)
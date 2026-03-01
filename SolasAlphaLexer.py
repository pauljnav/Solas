import re
from typing import NamedTuple, Generator

class SolasLexer:
    """
    Solas Alpha Lexer v0.2
    Enforces: Intent-driven tokens, @resource mapping, and complexity limits.
    and
    """
    def __init__(self):
        # Token definitions using regex
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
            ('FLOW_OP',         r'->'), # [cite: 85]
            ('COMPARATOR',      r'==|!=|>=|<=|>|<|\bis\b(\s+not)?'), # [cite: 65, 78-79]
            ('NUMBER',          r'\b\d+(\.\d+)?\b'), # [cite: 84]
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
        tokens = []
        line_num = 1

        for match in self.regex.finditer(code):
            kind = match.lastgroup
            value = match.group()

            if kind == 'SKIP' or kind == 'COMMENT':
                continue
            elif kind == 'NEWLINE':
                line_num += 1
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Dark Logic Detected: '{value}' at line {line_num}")

            # ENFORCE: Complexity Guard (The Rule of Three)
            if kind == 'KEYWORD' and value in ('and', 'or'):
                # Simple check for multiple operators on a single 'line' block
                if code.count(' and ') + code.count(' or ') > 2:
                    raise SyntaxError(f"Complexity Overflow at line {line_num}: Limit 2 operators.")

            tokens.append((kind, value))

        return tokens

# --- TEST DRIVE ---
solas_script = """
// Fetching secure token
stream @net.ingress
refract if latency > 50ms and @env.MODE == "fast"
drift -> @core.static_buffer
emit @env("API-KEY"), @data.archive
"""

lexer = SolasLexer()
try:
    for token in lexer.tokenize(solas_script):
        print(f"Token: {token[0]:<10} | Value: {token[1]}")
except Exception as e:
    print(f"!! {e} !!")
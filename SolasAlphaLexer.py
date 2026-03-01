import re

class SolasLexer:
    """
    Solas Alpha Lexer v0.1
    Enforces: Intent-driven tokens, @resource mapping, and complexity limits.
    """
    def __init__(self):
        # Token definitions using regex
        self.rules = [
            ('COMMENT',   r'//.*'),                         # // Single line comments
            ('KEYWORD',   r'\b(stream|refract|drift|shape|emit|if|and|or|not)\b'),
            ('ENV_CALL',  r'@env\("([^"]+)"\)'),            # @env("KEY-NAME") - Escape Hatch
            ('RESOURCE',  r'@[a-z_]+(\.[a-z_0-9]+)*'),      # @net.ingress, @env.TOKEN
            ('CONDITION', r'[a-z_]+\s*(>|<|==|!=)\s*\d+[a-z%]*'), # latency > 50ms
            ('ARROW',     r'->'),                           # drift -> @core
            ('BLOCK',     r'\{|\}'),                        # shape { ... }
            ('IDENTIFIER',r'[a-z_][a-z_0-9]*'),
            ('NEWLINE',   r'\n'),
            ('SKIP',      r'[ \t]+'),
            ('MISMATCH',  r'.'),                            # Catch-all for invalid syntax
        ]
        self.regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.rules))

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
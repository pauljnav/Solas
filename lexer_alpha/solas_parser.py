import sys
from typing import List, Optional
from solas_lexer import SolasLexer, Token

# Solas Parser v0.1 (Base Architecture)

class ASTNode: pass

class ShapeNode(ASTNode):
    def __init__(self, name: str, fields: List):
        self.name = name
        self.fields = fields

class SolasParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: str) -> Token:
        token = self.peek()
        if token.type == expected_type:
            self.pos += 1
            return token
        raise SyntaxError(f"Line {token.line}: Expected {expected_type}, got {token.type}")

    def parse_stream(self) -> StreamNode:
        self.consume('KEYWORD') # 'stream'
        res = self.consume('RESOURCE').value
        self.consume('DOT')
        path = self.consume('ID').value
        full_resource = f"{res}.{path}"
        self.consume('NEWLINE')
        self.consume('INDENT')
        self.consume('DEDENT')
        return StreamNode(full_resource)

    def parse_shape(self) -> ShapeNode:
        """Parses: shape ID NEWLINE INDENT (ID COLON TYPE NEWLINE)+ DEDENT"""
        self.consume('KEYWORD') # 'shape'
        name = self.consume('ID').value
        self.consume('NEWLINE')
        self.consume('INDENT')

        fields = []
        while self.peek().type == 'ID':
            f_name = self.consume('ID').value
            self.consume('COLON')
            f_type = self.consume('TYPE').value
            self.consume('NEWLINE')
            fields.append((f_name, f_type))

        self.consume('DEDENT')
        return ShapeNode(name, fields)

    def parse(self):
        nodes = []
        while self.peek().type != 'EOF':
            if self.peek().value == 'shape':
                nodes.append(self.parse_shape())
            else:
                self.pos += 1 # Skip for now
        return nodes
from typing import List, Any

# --- AST Nodes ---
class ASTNode:
    def __repr__(self): return f"{self.__class__.__name__}"

class FieldNode(ASTNode):
    def __init__(self, name, dtype):
        self.name, self.dtype = name, dtype
    def __repr__(self): return f"{self.name}: {self.dtype}"

class ShapeNode(ASTNode):
    def __init__(self, name, fields):
        self.name, self.fields = name, fields
    def __repr__(self):
        return f"Shape({self.name}){' ' + str(self.fields) if self.fields else ''}"

class StreamNode(ASTNode):
    def __init__(self, path, alias, body):
        self.path, self.alias, self.body = path, alias, body
    def __repr__(self):
        return f"Stream({self.path}{f' as {self.alias}' if self.alias else ''}) {self.body}"

class LogicNode(ASTNode):
    def __init__(self, keyword, content):
        self.keyword, self.content = keyword, content
    def __repr__(self): return f"{self.keyword.upper()}({self.content})"

# --- The Parser ---
class SolasParser:
    def __init__(self, tokens: List[Any]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, distance=0) -> Any:
        return self.tokens[self.pos + distance]

    def consume(self, expected_type: str, expected_val: Any = None) -> Any:
        token = self.peek()
        if token.type != expected_type:
            raise SyntaxError(f"Line {token.line}: Expected {expected_type}, got {token.type}")
        if expected_val and token.value != expected_val:
            raise SyntaxError(f"Line {token.line}: Expected '{expected_val}', got '{token.value}'")
        self.pos += 1
        return token

    def parse_field(self) -> FieldNode:
        name = self.consume('ID').value
        self.consume('COLON')
        t = self.peek()
        # Support ID as a type (for custom shapes like GeoLocation)
        if t.type in ['TYPE', 'ID']:
            data_type = self.consume(t.type).value
        elif t.type == 'RESOURCE':
            res = self.consume('RESOURCE').value
            data_type = f"{res}.{self.consume('ID').value}" if self.peek().type == 'DOT' and self.consume('DOT') else res
        else:
            raise SyntaxError(f"Line {t.line}: Invalid type '{t.value}'")
        self.consume('NEWLINE')
        return FieldNode(name, data_type)

    def parse_shape(self) -> ShapeNode:
        self.consume('KEYWORD', 'shape')
        name = self.consume('ID').value

        # Check if this is a definition block or just a reference
        if self.peek().type == 'NEWLINE' and self.peek(1).type == 'INDENT':
            self.consume('NEWLINE')
            self.consume('INDENT')
            fields = []
            while self.peek().type != 'DEDENT':
                if self.peek().type == 'ID':
                    fields.append(self.parse_field())
                elif self.peek().value == 'on':
                    fields.append(self.parse_statement())
                else: self.pos += 1
            self.consume('DEDENT')
            return ShapeNode(name, fields)

        # It's a reference (like line 14 in stresstest)
        if self.peek().type == 'NEWLINE': self.consume('NEWLINE')
        return ShapeNode(name, [])

    def parse_statement(self) -> LogicNode:
        """Parses on, emit, refract, drift as flat or indented units"""
        key_token = self.consume('KEYWORD')
        keyword = key_token.value
        content = []

        # Collect tokens until newline or block
        while self.peek().type not in ['NEWLINE', 'DEDENT', 'EOF']:
            content.append(str(self.peek().value))
            self.pos += 1

        if self.peek().type == 'NEWLINE': self.consume('NEWLINE')

        # If followed by INDENT, it's a multi-line logic block (like line 15-16)
        if self.peek().type == 'INDENT':
            self.consume('INDENT')
            sub_body = []
            while self.peek().type != 'DEDENT':
                sub_body.append(self.parse_statement())
            self.consume('DEDENT')
            return LogicNode(keyword, f"{' '.join(content)} -> {sub_body}")

        return LogicNode(keyword, " ".join(content))

    def parse_stream(self) -> StreamNode:
        self.consume('KEYWORD', 'stream')
        res_path = f"{self.consume('RESOURCE').value}.{self.consume('DOT') and self.consume('ID').value}"

        alias = None
        if self.peek().value == 'as':
            self.consume('KEYWORD', 'as')
            alias = self.consume('ID').value

        self.consume('NEWLINE')
        self.consume('INDENT')

        body = []
        while self.peek().type != 'DEDENT':
            val = self.peek().value
            if val == 'shape': body.append(self.parse_shape())
            elif val in ['on', 'refract', 'emit', 'drift']: body.append(self.parse_statement())
            else: self.pos += 1

        self.consume('DEDENT')
        return StreamNode(res_path, alias, body)

    def parse(self) -> List[ASTNode]:
        ast = []
        while self.peek().type != 'EOF':
            t = self.peek()
            if t.value == 'shape': ast.append(self.parse_shape())
            elif t.value == 'stream': ast.append(self.parse_stream())
            elif t.value in ['on', 'emit', 'refract', 'drift']: ast.append(self.parse_statement())
            elif t.type == 'NEWLINE': self.pos += 1
            else: self.pos += 1
        return ast
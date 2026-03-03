from typing import List, Any

# v1.1.3 Solas Parser: Philosophical Guardian
# Aligned with Lexer v1.1.3 (Identity Machine)
# Implementation of Linear Flow, Rule of Three, and Dark Logic Firewall.

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
    def __init__(self, resource_path, alias, body):
        self.resource_path = resource_path
        self.alias = alias
        self.body = body

    @property
    def res_path(self):
        """Alias for backward compatibility with current toxic test suite."""
        return self.resource_path

    def __repr__(self):
        return f"Stream({self.resource_path}{f' as {self.alias}' if self.alias else ''}) {self.body}"

class LogicNode(ASTNode):
    def __init__(self, keyword, content):
        self.keyword, self.content = keyword, content
    def __repr__(self): return f"{self.keyword.upper()}({self.content})"

class SolasParser:
    def __init__(self, tokens: List[Any]):
        self.tokens = tokens
        self.pos = 0
        self.is_inside_stream = False
        self.FORBIDDEN_LOGIC = {'if', 'else', 'or', 'while', 'for', 'not'}

    def peek(self, distance=0) -> Any:
        if self.pos + distance >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + distance]

    def consume(self, expected_type: str, expected_val: Any = None) -> Any:
        token = self.peek()
        if token.type != expected_type:
            # Context-specific error for missing @ pointers
            if expected_type == 'RESOURCE' and token.type == 'ID':
                raise SyntaxError(f"Line {token.line}: Global Resource Pointer (@) required")
            raise SyntaxError(f"Line {token.line}: Expected {expected_type}, got {token.type}")

        if expected_val and token.value != expected_val:
            raise SyntaxError(f"Line {token.line}: Expected '{expected_val}', got '{token.value}'")

        self.pos += 1
        return token

    def parse_statement(self) -> LogicNode:
        """Enforces Rule of Three and Forbidden Logic Filter."""
        key_token = self.consume('KEYWORD')
        keyword = key_token.value

        # Guard: Root-level keywords used as logic
        if keyword in self.FORBIDDEN_LOGIC:
            raise SyntaxError(f"Line {key_token.line}: Dark Logic '{keyword}' detected.")

        content = []
        and_count = 0

        while self.peek().type not in ['NEWLINE', 'DEDENT', 'EOF']:
            token = self.peek()

            # Philosophical Filter
            if token.value in self.FORBIDDEN_LOGIC:
                raise SyntaxError(f"Line {token.line}: Dark Logic '{token.value}' detected.")

            # Rule of Three Counter
            if token.value == 'and':
                and_count += 1
                if and_count > 3:
                    raise SyntaxError(f"Line {token.line}: Complexity Overflow. Use @core for deep logic.")

            content.append(str(token.value))
            self.pos += 1

        if self.peek().type == 'NEWLINE': self.consume('NEWLINE')

        if self.peek().type == 'INDENT':
            self.consume('INDENT')
            sub_body = []
            while self.peek().type != 'DEDENT' and self.peek().type != 'EOF':
                sub_body.append(self.parse_statement())
            self.consume('DEDENT')
            return LogicNode(keyword, f"{' '.join(content)} -> {sub_body}")

        return LogicNode(keyword, " ".join(content))

    def parse_stream(self) -> StreamNode:
        """Enforces Linear Flow (No Nested Streams)."""
        if self.is_inside_stream:
            raise SyntaxError(f"Line {self.peek().line}: Nested Streams violate Linear Flow.")

        self.is_inside_stream = True
        self.consume('KEYWORD', 'stream')

        # Build resource path: @res.id
        base_res = self.consume('RESOURCE').value
        resource_path = base_res
        if self.peek().type == 'DOT':
            self.consume('DOT')
            resource_path = f"{base_res}.{self.consume('ID').value}"

        alias = None
        if self.peek().value == 'as':
            self.consume('KEYWORD', 'as')
            alias = self.consume('ID').value

        self.consume('NEWLINE')
        self.consume('INDENT')

        body = []
        while self.peek().type != 'DEDENT' and self.peek().type != 'EOF':
            val = self.peek().value
            if val == 'stream':
                # Explicit call to trigger recursion guard
                body.append(self.parse_stream())
            elif val == 'shape':
                body.append(self.parse_shape())
            elif val in ['on', 'refract', 'emit', 'drift', 'grow', 'evolve']:
                body.append(self.parse_statement())
            else:
                self.pos += 1

        self.consume('DEDENT')
        self.is_inside_stream = False # Release scope
        return StreamNode(resource_path, alias, body)

    def parse_shape(self) -> ShapeNode:
        self.consume('KEYWORD', 'shape')
        name = self.consume('ID').value
        fields = []

        if self.peek().type == 'NEWLINE' and self.peek(1).type == 'INDENT':
            self.consume('NEWLINE')
            self.consume('INDENT')
            while self.peek().type != 'DEDENT' and self.peek().type != 'EOF':
                if self.peek().type == 'ID':
                    fields.append(self.parse_field())
                elif self.peek().value in ['on', 'emit', 'refract']:
                    fields.append(self.parse_statement())
                else:
                    self.pos += 1
            self.consume('DEDENT')
        elif self.peek().type == 'NEWLINE':
            self.consume('NEWLINE')

        return ShapeNode(name, fields)

    def parse_field(self) -> FieldNode:
        name = self.consume('ID').value
        self.consume('COLON')
        t = self.peek()

        if t.type in ['TYPE', 'ID']:
            data_type = self.consume(t.type).value
        elif t.type == 'RESOURCE':
            res = self.consume('RESOURCE').value
            data_type = res
            if self.peek().type == 'DOT':
                self.consume('DOT')
                data_type = f"{res}.{self.consume('ID').value}"
        else:
            raise SyntaxError(f"Line {t.line}: Invalid type '{t.value}'")

        self.consume('NEWLINE')
        return FieldNode(name, data_type)

    def parse(self) -> List[ASTNode]:
        ast = []
        while self.peek().type != 'EOF':
            t = self.peek()
            if t.value == 'shape': ast.append(self.parse_shape())
            elif t.value == 'stream': ast.append(self.parse_stream())
            elif t.value in ['on', 'emit', 'refract', 'drift', 'grow']:
                ast.append(self.parse_statement())
            elif t.type == 'NEWLINE': self.pos += 1
            else: self.pos += 1
        return ast
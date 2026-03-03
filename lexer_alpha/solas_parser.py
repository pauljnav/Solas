from typing import List, Any

# Solas Parser v1.1.3 | Security-First Recursive Descent
# ------------------------------------------------------
# Enforces Solas Alpha Language Constraints:
# 1. Linear Flow: Prevents nested 'stream' definitions.
# 2. Dark Logic: Blocks 'if', 'else', 'or', 'while', 'for', 'not'.
# 3. Rule of Three: Caps logical complexity at 3 terms (2 'and' gates).
# 4. Structural Audit: Validates nested blocks via unified body parsing.


class ASTNode:
    def __repr__(self): return f"{self.__class__.__name__}"

class StreamNode(ASTNode):
    def __init__(self, resource_path, alias, body):
        self.resource_path = resource_path
        self.alias = alias
        self.body = body

    @property
    def res_path(self):
        """Alignment with test_toxic.py attribute expectation"""
        return self.resource_path

    def __repr__(self): return f"Stream({self.resource_path}) {self.body}"

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
        self.current_and_count = 0

    def peek(self, distance=0) -> Any:
        if self.pos + distance >= len(self.tokens): return self.tokens[-1]
        return self.tokens[self.pos + distance]

    def consume(self, expected_type: str, expected_val: Any = None) -> Any:
        token = self.peek()

        # Explicit Error for test_missing_resource_pointer alignment
        if expected_type == 'RESOURCE' and token.type == 'ID':
            raise SyntaxError(f"Line {token.line}: Global Resource Pointer (@) required")

        if token.type != expected_type:
            raise SyntaxError(f"Line {token.line}: Expected {expected_type}, got {token.type}")

        if expected_val and token.value != expected_val:
            raise SyntaxError(f"Line {token.line}: Expected '{expected_val}', got '{token.value}'")

        self.pos += 1
        return token

    def parse_body(self) -> List[Any]:
        body = []
        while self.peek().type != 'DEDENT' and self.peek().type != 'EOF':
            t = self.peek()
            val = str(t.value).lower()
            if val == 'stream':
                body.append(self.parse_stream())
            elif t.type in ['KEYWORD', 'ID']:
                body.append(self.parse_statement())
            elif t.type == 'NEWLINE':
                self.pos += 1
                self.current_and_count = 0
            else:
                self.pos += 1
        return body

    def parse_statement(self) -> LogicNode:
        # 1. Entry Audit
        key_token = self.peek()
        keyword_val = str(key_token.value).lower()

        if keyword_val in self.FORBIDDEN_LOGIC:
            raise SyntaxError(f"Line {key_token.line}: Dark Logic '{key_token.value}' detected.")

        # Consume the lead keyword (on, emit, etc)
        keyword = key_token.value
        self.pos += 1

        content = []

        # 2. Total Line Audit Loop
        while self.peek().type not in ['NEWLINE', 'DEDENT', 'EOF']:
            t = self.peek()
            val = str(t.value).lower()

            # Guard: Forbidden Keywords mid-line
            if val in self.FORBIDDEN_LOGIC:
                raise SyntaxError(f"Line {t.line}: Dark Logic '{t.value}' detected.")

            # Guard: Complexity Rule of Three
            if val == 'and':
                self.current_and_count += 1
                if self.current_and_count >= 3: # Changed from >3 to >=3
                    raise SyntaxError(f"Line {t.line}: Complexity Overflow. Use @core for deep logic.")

            content.append(str(t.value))
            self.pos += 1

        if self.peek().type == 'NEWLINE':
            self.consume('NEWLINE')
            self.current_and_count = 0

        # 3. Handle Nested Blocks
        if self.peek().type == 'INDENT':
            self.consume('INDENT')
            sub_body = self.parse_body()
            self.consume('DEDENT')
            return LogicNode(keyword, f"{' '.join(content)} -> {sub_body}")

        return LogicNode(keyword, " ".join(content))

    def parse_stream(self) -> StreamNode:
        if self.is_inside_stream:
            raise SyntaxError(f"Line {self.peek().line}: Nested Streams violate Linear Flow.")

        self.is_inside_stream = True
        self.consume('KEYWORD', 'stream')

        # Path Parsing
        base_res = self.consume('RESOURCE').value
        path = base_res
        if self.peek().type == 'DOT':
            self.consume('DOT')
            path += f".{self.consume('ID').value}"

        # Optional Alias
        alias = None
        if self.peek().value == 'as':
            self.consume('KEYWORD', 'as'); alias = self.consume('ID').value

        if self.peek().type == 'NEWLINE': self.consume('NEWLINE')
        self.consume('INDENT')

        body = self.parse_body()

        self.consume('DEDENT')
        self.is_inside_stream = False
        return StreamNode(path, alias, body)

    def parse(self) -> List[Any]:
        ast = []
        while self.peek().type != 'EOF':
            t = self.peek()
            val = str(t.value).lower()
            if val == 'stream':
                ast.append(self.parse_stream())
            elif t.type in ['KEYWORD', 'ID']:
                ast.append(self.parse_statement())
            elif t.type == 'NEWLINE':
                self.pos += 1
            else:
                self.pos += 1
        return ast
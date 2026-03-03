import unittest
from solas_lexer import SolasLexer, SolasLexicalError
from solas_parser import SolasParser, StreamNode

class TestSolasToxicSuite(unittest.TestCase):
    def setUp(self):
        self.lexer = SolasLexer()

    def test_golden_path_parsing(self):
        """Verify that valid blocks generate a correct AST with EBNF-aligned attributes."""
        code = """
stream @net.ingress as gateway
    on request: emit @sys.log
"""
        tokens = list(self.lexer.tokenize(code))
        parser = SolasParser(tokens)
        ast = parser.parse()

        self.assertTrue(len(ast) > 0)
        self.assertIsInstance(ast[0], StreamNode)
        # Testing the @property alias for backward compatibility
        self.assertEqual(ast[0].res_path, "@net.ingress")
        # Testing the primary EBNF-aligned attribute
        self.assertEqual(ast[0].resource_path, "@net.ingress")

    def test_dark_logic_blocking(self):
        """Forbidden keywords should pass the Lexer but fail the Parser."""
        codes = [
            "on status == 'fail': if x > 1: emit @core.err",
            "on timeout or refused: evolve logic",
            "on error: drift to @cache.a else drift to @cache.b"
        ]
        for code in codes:
            tokens = list(self.lexer.tokenize(code))
            parser = SolasParser(tokens)
            with self.assertRaises(SyntaxError) as cm:
                parser.parse()
            self.assertIn("Dark Logic", str(cm.exception))

    def test_illegal_characters(self):
        """Braces are not in the language; Lexer should reject them as MISMATCH."""
        code = "on init { emit @start }"
        with self.assertRaises(SolasLexicalError):
            list(self.lexer.tokenize(code))

    def test_missing_resource_pointer(self):
        """Verify that 'nut.ingress' is rejected because it lacks the @ prefix."""
        code = "stream nut.ingress\n    on data: emit @out"
        tokens = list(self.lexer.tokenize(code))
        parser = SolasParser(tokens)
        with self.assertRaises(SyntaxError) as cm:
            parser.parse()
        self.assertIn("Global Resource Pointer (@) required", str(cm.exception))

    def test_nested_stream_violation(self):
        """Ensure nested streams trigger a structural flow error in the Parser."""
        code = """
stream @outer.flow
    on data:
        stream @inner.flow
            on data: emit @out
"""
        tokens = list(self.lexer.tokenize(code))
        parser = SolasParser(tokens)
        with self.assertRaises(SyntaxError) as cm:
            parser.parse()
        self.assertIn("Nested Streams violate Linear Flow", str(cm.exception))

    def test_complexity_overflow_rule_of_three(self):
        """Verify that more than three 'and' gates trigger Complexity Overflow."""
        code = "on a and b and c and d: emit @result"
        tokens = list(self.lexer.tokenize(code))
        parser = SolasParser(tokens)
        with self.assertRaises(SyntaxError) as cm:
            parser.parse()
        self.assertIn("Complexity Overflow", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
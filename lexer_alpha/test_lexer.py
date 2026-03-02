import unittest
from solas_lexer import SolasLexer, SolasLexicalError

class TestSolasLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = SolasLexer()

    def test_scientific_notation(self):
        """Ensure v1.1 handles complex numbers."""
        code = "on latency > 2.5e-3"
        tokens = list(self.lexer.tokenize(code))
        # Expecting: KEYWORD(on), ID(latency), COMPARATOR(>), NUMBER(2.5e-3)
        numbers = [t.value for t in tokens if t.type == 'NUMBER']
        self.assertEqual(numbers, ['2.5e-3'])

    def test_indentation_depth(self):
        """Verify divmod depth-sync yields correct INDENT/DEDENT counts."""
        code = "stream @net\n    shape User\n        id: UUID"
        tokens = list(self.lexer.tokenize(code))
        indents = [t.type for t in tokens if t.type == 'INDENT']
        self.assertEqual(len(indents), 2, "Should have two levels of indentation")

    def test_lockdown_braces(self):
        """Bad Case: Braces must trigger LexicalError."""
        code = "shape User { id: UUID }"
        with self.assertRaisesRegex(SolasLexicalError, "Braces deprecated"):
            list(self.lexer.tokenize(code))

    def test_dark_logic_if(self):
        """Bad Case: 'if' keyword must be blocked."""
        code = "refract if latency > 50"
        with self.assertRaisesRegex(SolasLexicalError, "Dark Logic 'if' detected"):
            list(self.lexer.tokenize(code))

    def test_illegal_chars(self):
        """Bad Case: Hyphens in IDs must fail."""
        code = "emit @env.DEPLOY-STAGE"
        with self.assertRaises(SolasLexicalError):
            list(self.lexer.tokenize(code))

if __name__ == '__main__':
    unittest.main()
import unittest
from solas_lexer import SolasLexer, SolasLexicalError

class TestSolasLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = SolasLexer()

    def run_lexer(self, code):
        return list(self.lexer.tokenize(code))

    ## --- GOOD CASES (Should Pass) ---

    def test_scientific_notation_integrity(self):
        """Verify v1.1 atomic number capture."""
        code = "on latency > 2.5e-3 evolve logic -> \"stable\""
        tokens = self.run_lexer(code)
        val = next(t.value for t in tokens if t.type == 'NUMBER')
        self.assertEqual(val, '2.5e-3')

    def test_depth_sync_multi_dedent(self):
        """Verify the divmod stack cleanup."""
        code = "stream @net\n    shape User\n        id: UUID\nemit user"
        tokens = self.run_lexer(code)
        dedents = [t for t in tokens if t.type == 'DEDENT']
        self.assertEqual(len(dedents), 2)

    ## --- BAD CASES (Should Fail) ---

    def test_dark_logic_branching(self):
        """Block forbidden 'if' and 'or' keywords."""
        with self.assertRaisesRegex(SolasLexicalError, "Dark Logic 'if'"):
            self.run_lexer("refract if load > 50")
        with self.assertRaisesRegex(SolasLexicalError, "Dark Logic 'or'"):
            self.run_lexer("on latency > 50 or jitter < 5")

    def test_legacy_braces(self):
        """Block deprecated curly braces."""
        with self.assertRaisesRegex(SolasLexicalError, "Braces deprecated"):
            self.run_lexer("shape Geo { lat: Number }")

    def test_greedy_units_violation(self):
        """Block illegal character suffixes in numbers."""
        # 50ms will tokenize as NUMBER(50) then ID(ms).
        # But a hyphen in an ID will trigger the Lexical Error.
        with self.assertRaises(SolasLexicalError):
            self.run_lexer("on latency > 50-ms")

    def test_tab_contamination(self):
        """Enforce strict 4-space rule against tabs."""
        with self.assertRaisesRegex(SolasLexicalError, "Tabs are forbidden"):
            self.run_lexer("stream @net\n\tshape User")

if __name__ == '__main__':
    print("--- STARTING SOLAS LEXER GAUNTLET v1.1 ---")
    unittest.main()
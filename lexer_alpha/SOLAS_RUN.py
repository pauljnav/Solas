import sys
import os

from solas_lexer import SolasLexer
from solas_parser import SolasParser

def run_compiler(filepath):
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Phase 1: Lexical Analysis
        lexer = SolasLexer()
        tokens = list(lexer.tokenize(code))
        print(f"[*] Lexer: Generated {len(tokens)} tokens.")

        # Phase 2: Syntax Analysis (Parsing)
        parser = SolasParser(tokens)
        ast = parser.parse()
        print(f"[*] Parser: Successfully built AST with {len(ast)} nodes.")

        # Phase 3: Inspect the AST
        for node in ast:
            print(f"    -> {node}")

    except Exception as e:
        print(f"[!] ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py solas_run.py <file.solas>")
    else:
        run_compiler(sys.argv[1])
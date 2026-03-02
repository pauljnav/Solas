import sys
import os
from solas_lexer import SolasLexer
from solas_parser import SolasParser

def run_compiler(filepath):
    if not os.path.exists(filepath):
        print(f"[!] File not found: {filepath}")
        return

    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Phase 1: Lexing
        lexer = SolasLexer()
        tokens = list(lexer.tokenize(code))

        # Phase 2: Parsing
        parser = SolasParser(tokens)
        ast = parser.parse()

        # Phase 3: Reporting
        print(f"\n--- SOLAS BUILD REPORT: {os.path.basename(filepath)} ---")
        if not ast:
            print("Status: Empty AST.")
        else:
            for node in ast:
                print(f"AST Root: {node}")
        print("--- END REPORT ---\n")

    except Exception as e:
        print(f"[!] COMPILER ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py SOLAS_RUN.py <your_file.solas>")
    else:
        run_compiler(sys.argv[1])
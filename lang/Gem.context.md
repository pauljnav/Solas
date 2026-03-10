#gem.context

Project: Solas Alpha (Language Specification & Parser)
Current Status: In Progress (Milestone: v1.1.4 Logic Hardening Complete)
Critical Context:
 * Key Tech: Python 3.x, Recursive Descent Parsing, Custom Lexer, AST-driven Architecture.
 * Main Goal: Build a "Toxic-Proof" domain-specific language (DSL) for high-reliability data streams that physically prevents complex "Dark Logic" (if/else/loops) at the structural level.
Recent Decisions:
 * Decision A: The Rule of Three. Logic is strictly capped at 3 terms (max 2 and gates). The 3rd and gate triggers a Complexity Overflow to force developers toward modular @core logic rather than nested script complexity.
 * Decision B: Type-Agnostic Auditing. The Parser now audits the string value of tokens during parse_statement, ensuring forbidden keywords (e.g., if, or, while) are blocked even if the Lexer misidentifies their type.
 * Decision C: Linear Flow Guard. Nested stream definitions are explicitly blocked via recursion guards in parse_body to maintain a single-direction data pipeline.
 * Decision D: Test-Driven Alignment. Added a .res_path property to StreamNode and specific error strings for missing @ pointers to satisfy the test_toxic.py suite requirements.
Next Steps:
 * Step 1: Shape Definitions. Implement the technical specification for shape and refract structures within the AST.
 * Step 2: The Transpiler. Develop the engine to convert the validated AST into executable Python or intermediate bytecode.
 * Step 3: Runtime Validation. Ensure the @core resource pointers correctly map to system-level calls during execution.

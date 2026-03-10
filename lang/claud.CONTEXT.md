# Project: Solas — The Intent-Driven Programming Language
## Current Status: In Progress

## Critical Context:
* Key Tech: Custom language design — EBNF grammar, lexer (not yet built), tree-walk interpreter (not yet built)
* Key Files: `EBNF_solas.txt`, `README.md`, `RESOLVED_DECISIONS.md`, `CONTEXT.md`
* Main Goal: Design and implement a complete, intent-driven programming language called Solas. The language is AI-native, token-efficient, and built around the philosophy that code should read as a transparent map of purpose. The grammar specification is now largely complete. The next phase is outputting the updated EBNF and beginning lexer implementation.

---

## Recent Decisions:

### Block Structure
* Indentation-based, no curly braces. 4 spaces mandatory. Tabs not permitted.
* Blocks close on dedentation back to the opening keyword level.
* Blank lines inside blocks are ignored by the parser.
* Applies to all block constructs — `stream`, `shape`, `grow`, `refract`, `enum`, `hashmap`.

### Stream
* Syntax: `stream resource_expr [ as IDENTIFIER ]`
* `stream user from @net.api(...)` syntax is retired.
* Nesting is invalid — Hand-off Pattern used instead via `@core` pipes.
* Stream error handlers: `on error`, `on shape_warning`, `on shape_error`.

### Emit
* Supports comma-separated targets as a single logical data packet.
* e.g. `emit user.name, user.id`
* `emit_target` includes `resource_expr` to support `emit @core.posts_pipe`.

### Shape System — Complete
* **Named only:** All shapes must be named. Anonymous inline shapes not permitted. Referential Pattern enforced.
* **Versioning:** `shape UserProfile v1` — version suffix on every shape. First match wins in stream routing. Most specific version declared first.
* **Optional fields:** `?` replaces `:` for optional fields. e.g. `bio? String`
* **Required fields:** `:` declares required fields. e.g. `name: String`
* **Default values:** `=` assigns default to optional fields only. e.g. `timeout? Int = 30`
* **Array types:** `[String]` required collection. `[String:nullable]` items may be null. `?` on field name means collection itself may be absent. e.g. `posts? [String:nullable]`
* **Constraints:** Parentheses qualify type with inclusive range bounds. Positional min/max. One-sided constraints use empty position. e.g. `age: Int (0,100)`, `value? Int (1,)`
* **Numeric types:** `Number` retired. Explicit types: `Int`, `Int8`, `Int16`, `Int32`, `Int64`, `UInt`, `UInt8`, `UInt16`, `UInt32`, `UInt64`, `Float`, `Float32`, `Float64`, `Decimal`.
* **Semantic types:** `String`, `Email`, `URL`, `Date`, `Time`, `DateTime`, `E164`, `UUID`, `PostalCode`, `Blob`.
* **Enum types:** `enum IDENTIFIER:Type` with indented members. e.g. `enum OrderStatus:String` with members `pending`, `active`, `closed`.
* **Hashmap types:** `hashmap IDENTIFIER[KeyType,ValueType]` — comma separates key and value types. Members use `:` for assignment. e.g. `hashmap Priority[String,Int32]`

### Shape Validation Model
* Missing required field — hard failure, triggers `on shape_error`
* Missing optional field — soft, uses default if defined, otherwise continues
* Numeric range violation — data is master, triggers `on shape_warning`, stream continues
* Wrong type or string constraint violation — triggers `on shape_error`
* Unknown fields — lenient by default, captured automatically in `__additional` as raw JSON Blob
* Version matching — first match wins, developer controls order, most specific first
* No match — triggers `on shape_error`

### __additional
* Reserved automatic field present on every shaped result.
* Contains all fields that arrived but were not defined in the shape.
* Typed as raw JSON Blob — never silently discarded.
* Access: `user.__additional`
* Store: `emit user.__additional -> @data.store("schema_drift_log").as(JSON)`

### Format Keywords
* Format identifiers are unquoted keywords — not string literals.
* Valid formats: `JSON`, `CSV`, `Blob`, `XML`
* `STRING` remains as fallback for unnamed formats.
* e.g. `.as(JSON)` not `.as("JSON")`

### Conditions — Rule of Three
* Maximum three `and` operators (four conditions) per condition block.
* Exceeding this is Dark Logic — Semantic Guard throws `Complexity Overflow` error.
* Both inline and line-wrapped forms valid.
* `or` not permitted — split intent into separate `refract` rules.
* Line-wrapped: line ending in `and` signals continuation. Colon on final line signals closure.

### Resource System
* Resource roots: `@net`, `@data`, `@math`, `@core`, `@env`, `@cache`
* `@` prefix always fused with resource name as single atomic token.
* `@env.TOKEN` standard. `@env("MY-SECRET-KEY")` fallback for non-standard names.
* `resource_call` references named rules directly: `net_connector`, `net_modifier`, `data_action`, `data_modifier` plus generic fallback.

### grow
* `grow fib to 10` means exactly 10 iterations. Result length = len(init) + 10.

### Lexical
* `NEWLINE` defined as lexical token — `\n` or `\r\n`
* `block` rule uses `INDENT`/`DEDENT` — 4 spaces, no curly braces
* `RESOURCE` token is atomic: `@net | @data | @math | @core | @env | @cache`

---

## Open Items:
* Null vs absent distinction at field level for non-collection types — deferred, to be resolved.
* `refract` execution model — currently underspecified. `evolve logic -> "string"` needs formal definition.
* Semantic Guard — referenced throughout but not yet formally defined as a grammar rule.

---

## Next Steps:
* Step 1: Output fully updated `EBNF_solas.txt` reflecting all locked-in decisions.
* Step 2: Update `README.md` to reflect all new syntax — shape system, hashmap, enum, block structure, validation model.
* Step 3: Resolve open items — null vs absent, refract execution model, Semantic Guard.
* Step 4: Begin lexer implementation in Python.

# Solas: The Intent-Driven Language

**Solas** (n.) /soˈlas/ – *The point where intent meets clarity.*

In legacy programming, logic is often obscured by the "darkness" of boilerplate and rigid syntax. **Solas** is the light that strips these shadows away. It represents a paradigm shift from instructing a machine *how* to work to showing it *what* to achieve.

> *"We do not build to fight the dark of error; we code to invite the light of logic."*

---

## Core Philosophy

* **Clarity (Light):** Code is a transparent map of purpose, not a puzzle of brackets.
* **Resilience:** Native support for `drift` (recovery) and `refract` (optimization).
* **Efficiency:** Token-optimized syntax designed for the speed of AI inference.

---

## AI-Native Efficiency

Standard languages are "chatty"—cluttered with boilerplate that inflates LLM token consumption. Solas uses high-density, intent-driven syntax to reduce token overhead by up to 50%, making AI-driven development faster, cheaper, and more precise.

---

## The Solas Grammar

Solas eliminates syntactic friction. There are no imports, no semicolons, and no manual memory management.

### Key Primitives

| Keyword   | Function |
| --------- | -------- |
| `stream`  | Initiates continuous or asynchronous data flow. |
| `emit`    | Directs output to the active interface (Console, API, UI), or hands off to the next stream. |
| `refract` | Triggers real-time logic mutation based on performance. |
| `drift`   | Deterministic error recovery; self-heals to a backup path. |
| `grow`    | Handles organic recursion and iterative expansion. |
| `shape`   | Semantic data validation and type-mapping. |
| `as`      | Binds a stream result to a readable alias name. |

---

## Global Resource Map (`@`)

Solas interacts with the system through **Global Pointers**. These abstract complex system calls into simple intents.

* **`@net`**: Self-negotiating network layer.
* **`@data`**: Context-aware schema and validation engine.
* **`@math`**: High-performance tensor and vector primitives.
* **`@core`**: Runtime management and inter-stream pipes.
* **`@cache`**: Fast-access fallback storage for drift scenarios.
* **`@env`**: Variable environment and secrets. Standard access via dot notation (`@env.TOKEN`). Use call notation as a fallback for non-standard names (`@env("MY-SECRET-KEY")`).

---

## Quick Examples

### Self-Healing Data Stream

```solas
// Intent: Secure User Profile
shape UserProfile { id: UUID, name: String }

stream @net.api("user/1") as user {
    shape UserProfile
    on error -> drift to @cache.last_user
}
emit user.name
```

### Fibonacci Sequence (Organic Growth)

```solas
// Intent: Sequence Expansion
// grow runs exactly 10 iterations; result = 2 initial + 10 grown = 12 elements
grow fib to 10 {
    init [0, 1]
    step: tail(2).sum
}
emit fib
```

### Chained Streams (Hand-off Pattern)

```solas
// Intent: Lookup user from incoming request
shape UserID { id: UUID }
shape UserProfile { id: UUID, name: String }
shape PostList { posts: String }

stream @net.ingress as request {
    shape UserID
    on error -> drift to @cache.last_user
    emit @core.lookup_pipe
}

// Intent: Resolve full profile and respond
stream @core.lookup_pipe as user {
    shape UserProfile
    on error -> drift to @cache.last_user
    emit @core.posts_pipe
}

// Intent: Fetch user posts and return response
stream @core.posts_pipe as posts {
    shape PostList
    on error -> drift to @cache.last_posts
}

emit user.name, posts
```

---

## Linear Flow Philosophy

Solas follows a **Linear Flow** model. Stream blocks are never nested. Instead, dependent streams are connected via the **Hand-off Pattern** — one stream emits into a `@core` pipe, and the next stream picks it up. This keeps every intent visible as a distinct, sequential step.

```solas
// Invalid — nested intent
stream @net.ingress {
    stream @data.user_lookup { ... }
}

// Valid — chained intent
stream @net.ingress as request {
    emit @core.lookup_pipe
}
stream @core.lookup_pipe as user {
    emit @net.response
}
```

---

## The Rule of Three — Conditions and Dark Logic

Solas allows up to three `and` operators (four conditions) per condition block. Exceeding this is **Dark Logic** — intent obscured by procedural complexity. The Semantic Guard throws a `Complexity Overflow` error at parse time.

`or` is not permitted. A condition that branches on either/or represents two separate intents and must be written as two separate `refract` rules:

```solas
// Invalid — 'or' splits intent
refract recovery {
    on status is "timeout" or status is "refused": evolve logic -> "retry"
}

// Valid — each intent is its own rule
refract recovery {
    on status is "timeout": evolve logic -> "retry"
    on status is "refused": evolve logic -> "retry"
}
```

Both inline and line-wrapped forms are valid:

```solas
// Inline
refract performance {
    on latency > 200 and errors > 5 and memory > 80: evolve logic -> "switch to @cache"
}

// Line-wrapped — each line ending in 'and' is a continuation
refract performance {
    on latency > 200 and
       errors > 5 and
       memory > 80: evolve logic -> "switch to @cache"
}

// Dark Logic — Complexity Overflow error
refract performance {
    on a > 1 and b < 2 and c == 3 and d != 4 and e > 0: evolve logic -> "switch to @cache"
}

// Correct abstraction of Dark Logic
refract system_check {
    on @core.system_valid: evolve logic -> "switch to @cache"
}
```

---

## Shape Rules

Shapes are always **named** and **flat**. Anonymous inline shapes are not permitted. Sub-structures are defined as separate named shapes and referenced by name.

```solas
// Invalid — anonymous inline shape
stream @net.api("user/1") as user {
    shape { id: UUID, name: String }
}

// Valid — named shape, referential pattern
shape UserProfile { id: UUID, name: String }

stream @net.api("user/1") as user {
    shape UserProfile
}
```

---

## AI Implementation (Copilot/Gemini)

To enable Solas in your AI editor, add the following to your system instructions:

> "Translate intent into Solas. Prioritize succinctness. Use `@` for resources. Every line must represent a distinct logical intent. Streams are never nested — use the Hand-off Pattern. All shapes must be named."

---

## License

Copyright (c) 2026 Paul Naughton. Distributed under the MIT License.

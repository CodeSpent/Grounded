# Answer key: Mode C (Ad hoc Grounded Check)

Planted so a correct run catches one clear violation and one partial edge case,
not just a check that validation exists at all.

| Criterion | Expected status | Why |
|---|---|---|
| `body` required, must be a string | Met | `isinstance(body, str)` check, line 10 |
| `body` max 200 chars, 400 on violation | Not met | Code enforces `len(body) > 500`, not 200. The spec's limit isn't what's implemented |
| `body` not empty/whitespace-only, 400 on violation | Partial | Only checks `body == ""`. A whitespace-only string (e.g. `"   "`) passes both checks and reaches `save_comment` uncaught |
| Success returns 201 with created comment JSON | Met | `return jsonify(comment), 201` |

A correct run must not accept "there's a length check" as proof the spec's limit
is enforced. The actual number, 500 vs. 200, is the point.

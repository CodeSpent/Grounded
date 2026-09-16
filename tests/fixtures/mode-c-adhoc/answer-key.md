# Answer key — Mode C (Ad hoc Grounded Check)

Planted so a correct run must catch **one clear violation** and **one partial edge
case**, not just check that validation exists at all.

| Criterion | Expected status | Why |
|---|---|---|
| `body` required, must be a string | ✅ Met | `isinstance(body, str)` check, line 10 |
| `body` max 200 chars → 400 | ❌ Not met | Code enforces `len(body) > 500`, not 200 — spec's limit is not what's implemented |
| `body` not empty/whitespace-only → 400 | ⚠️ Partial | Only checks `body == ""`; a whitespace-only string (e.g. `"   "`) passes both checks and reaches `save_comment` uncaught |
| Success → 201 with created comment JSON | ✅ Met | `return jsonify(comment), 201` |

A correct run must not accept "there's a length check" as proof the *spec's* limit
is enforced — the actual number (500 vs. 200) is the point.

# Skill Improvement Proposal

**Context:** Issues found in the 2026-04-10 Space Snakes review that the current skill instructions did not prompt for.

---

## Issues that slipped through and why

| Issue found | Root cause in skill |
|---|---|
| Bare `except Exception: pass` silently swallowing all errors | `review` has no explicit check for silent exception handling |
| Double `json.dumps` with no comment explaining intent | `review` mentions "complex code without appropriate comments" but not the specific pattern of *intentional* non-obvious code that looks wrong |
| `pygame.Surface` allocated per-segment per-frame in render loop | Neither skill checks for object allocation inside hot loops |
| `snake-ai.md` documents `snake_ai.py` which doesn't exist | `review` doesn't cross-check `.md` doc references against actual files |
| `multiplayer.md` "Open Questions" is leftover pre-implementation planning | `create-feature` has no step to clean up planning docs after the feature ships |

---

## Proposed changes

### `review` SKILL.md — add 4 explicit check categories

Add these after step 6 ("Also check for outdated dependencies"):

```
7. Check for silent exception handling: bare `except: pass`, `except Exception: pass`,
   or any except block that sets a flag but logs nothing. Flag every one — they make
   bugs invisible. A note saying "log or re-raise" is sufficient.

8. Check for non-obvious code that lacks a "why" comment: code that looks like a bug
   but is intentional (e.g. double json.dumps, intentional mutation order, subtle
   async ordering). If future-reader will ask "is this a bug?", a one-line comment is required.

9. Check for object allocation inside hot loops (game loops, render loops, per-frame
   callbacks): Surface(), [], {}, dataclass instances, etc. Flag allocations that could
   be pre-computed once and reused.

10. Cross-check .md documentation against actual files: for every filename, class, or
    function mentioned in a .md file, verify it exists in the codebase. Flag any
    references to nonexistent code as dead documentation.
```

---

### `create-feature` SKILL.md — add 2 cleanup steps

After step 5 ("Check all .md files..."), add:

```
5b. After a feature ships, find any pre-implementation planning sections in .md files
    (sections titled "Open Questions", "New Files Required", "Deployment Steps", "Option
    Comparison", or similar) and either delete them or replace with a one-line "Implemented
    — see <file>" note. Planning cruft becomes misinformation once the feature exists.

5c. Never use bare `except: pass` or `except Exception: pass`. At minimum, log the
    exception. Silent swallowing turns bugs invisible in production.
```

---

## No changes needed to

- The "verify fixes before carrying forward" loop in `review` — that part worked perfectly (all 9 prior issues were correctly verified as fixed).
- The import/dead-code cleanup steps in `create-feature` — those are effective.

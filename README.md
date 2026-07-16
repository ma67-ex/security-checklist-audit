# security-checklist-audit

A Claude Code skill that runs a first-pass security audit of a local codebase
against a fixed 16-item checklist (Frontend Security, Backend Security,
Practical Security Habits) and returns the checklist filled in with
pass/fail/partial/N-A plus one-line evidence per item.

It's a static/heuristic scan of code already on disk: no network calls, no
live CVE lookups. Not a substitute for CodeQL, Semgrep, or a professional
pentest.

## How it works

`scripts/scan.py` walks a repo directory and applies regex-based checks per
checklist item, printing JSON with:

- `positive_evidence`: mitigation present (file:line + snippet)
- `negative_evidence`: risky pattern present (file:line + snippet)
- `note`: free-text context the script can reason about structurally (e.g.
  "no API route files found," "no lockfile in this tree")
- `supply_chain_flags`: a separate, repo-wide check for prompt-injection
  attempts in agent-instruction files (`CLAUDE.md`, `.cursorrules`, ...) and
  suspicious `npm install` lifecycle scripts

It's pattern-matching, not real static analysis (no AST, no data-flow). It
will miss things and flag things that turn out to be fine on closer read.
Its job is to point a human (or the calling skill) at the right files fast,
not to be the final word.

### Usage

```
python3 scripts/scan.py <repo_path> [--json-only]
```

## The checklist

**Frontend Security**
1. Use HTTPS everywhere
2. Input validation and sanitization
3. Don't store sensitive data in the browser
4. CSRF protection
5. Never expose API keys in frontend

**Backend Security**
6. Authentication fundamentals
7. Authorization checks
8. API endpoint protection
9. SQL injection prevention
10. Basic security headers
11. DDoS protection

**Practical Security Habits**
12. Keep dependencies updated
13. Proper error handling
14. Secure cookies
15. File upload security
16. Rate limiting

## Using it as a skill

Copy this directory into `~/.claude/skills/security-checklist-audit/` (or a
project's `.claude/skills/`). Claude Code picks it up automatically and
triggers it on prompts like "run a security audit," "review this before I
push it to GitHub," or "is this app secure." See [`SKILL.md`](SKILL.md) for
the full workflow Claude follows: run the scanner, read the actual matched
files by hand before trusting any snippet, classify each item as CONFIRMED
PASS / CONFIRMED FAIL / PARTIAL / NEEDS REVIEW / N/A, and render the filled
checklist.

## Layout

```
SKILL.md              skill instructions Claude Code follows
scripts/scan.py        the scanner
evals/evals.json       eval cases
references/             supporting reference material
```

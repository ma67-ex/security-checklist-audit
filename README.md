# security-checklist-audit

![Python](https://img.shields.io/badge/python-3-3776AB?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-standard%20library-2ea44f)
![License](https://img.shields.io/badge/license-MIT-green)

A Claude Code skill that audits a local codebase against a fixed 16-item
security checklist covering frontend security, backend security, and
practical security habits. It also checks for a privacy policy, terms of
service, and accessibility statement, and flags supply-chain risks specific
to AI-assisted codebases: prompt-injection attempts in agent-instruction
files and malicious `npm install` hooks.

The result is a report, not a wall of chat text: a dark, cybersecurity-themed
`report.html` with a risk summary, a severity bar, and a plain-English
explanation for every finding, served on localhost and opened automatically.

## What it checks

**Frontend security**
1. HTTPS everywhere
2. Input validation and sanitization
3. No sensitive data stored in the browser
4. CSRF protection
5. No API keys exposed in frontend code

**Backend security**
6. Authentication fundamentals
7. Authorization checks
8. API endpoint protection
9. SQL injection prevention
10. Basic security headers
11. DDoS protection

**Practical security habits**
12. Dependency freshness
13. Proper error handling
14. Secure cookies
15. File upload security
16. Rate limiting

**Beyond the checklist**
- Legal and compliance pages: privacy policy, terms of service, accessibility
  statement, weighed against whether the codebase actually collects user
  data.
- Supply-chain flags: prompt-injection patterns in `CLAUDE.md` /
  `AGENTS.md` / `.cursorrules`, and fetch-and-execute patterns in
  `package.json` install scripts.

## How it works

`scripts/scan.py` walks the repository and runs a set of pattern-based checks
per checklist item, printing structured JSON: positive evidence (a mitigation
is present), negative evidence (a risky pattern is present), and contextual
notes for cases the script can reason about on its own, such as a repo with
no API routes. Claude reads the flagged files directly, confirms or discards
each match, and writes the verdicts and reasoning into the report.

This is static pattern matching, not full program analysis: no AST, no
data-flow tracing, no live CVE lookup. It complements tools like CodeQL and
Semgrep rather than replacing them, and it is built to catch the gaps that
show up most often before a first push, fast.

```
python3 scripts/scan.py <repo_path>
```

## The report

`scripts/report_template.html` defines the design: a near-black background
with an olive-green accent, a risk-posture summary with a stacked severity
bar, one section per checklist category, and a status pill and severity
stripe on every finding. Each item explains what it checks and why it
matters in plain language, with the specific evidence for that repository
tucked behind a collapsible toggle. `scripts/glossary.md` holds the
explanatory copy, kept consistent across every run. The page opens on
localhost through `scripts/serve_report.py` in a plain terminal, or through
Claude Code's browser preview when one is available.

## Using it as a skill

Copy this directory into `~/.claude/skills/security-checklist-audit/`, or
into a project's `.claude/skills/`. Claude Code picks it up automatically and
triggers it on prompts like "run a security audit," "review this before I
push it to GitHub," or "is this app secure." [`SKILL.md`](SKILL.md) has the
full workflow: run the scanner, verify every match against the actual file,
classify each item, and render the report.

## Layout

```
SKILL.md                      instructions Claude Code follows
scripts/scan.py                the scanner
scripts/report_template.html   the report's design system
scripts/glossary.md            explanatory copy per checklist item
scripts/serve_report.py        localhost server for the rendered report
scripts/test_legal_pages.py    self-check for the legal-pages logic
evals/evals.json               eval cases
references/                    supporting reference material
```

## License

MIT. See [LICENSE](LICENSE).

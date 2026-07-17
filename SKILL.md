---
name: security-checklist-audit
description: Run a first-pass security audit of a local codebase against a fixed 16-item checklist (Frontend Security, Backend Security, Practical Security Habits) and return the checklist filled in with pass/fail/partial/N-A plus one-line evidence per item. Also checks for commonly-required site pages (privacy policy, terms of service, accessibility statement) when the codebase looks like it collects user data. Use this whenever the user asks to "check security," "run a security audit," "review this before I push it to GitHub," "is this app secure," asks about specific risks like XSS, CSRF, SQL injection, exposed API keys, secure cookies, rate limiting, or security headers, or asks whether they're missing a privacy policy / terms of service / accessibility page in one of their own projects. Also trigger when the user pastes or references the security checklist image/table itself and wants it filled out for a given repo. This is a static/heuristic scan of code already on disk (no network calls, no live CVE lookups) — it is not a substitute for CodeQL, Semgrep, or a professional pentest, and the skill says so in its own output. The legal-page check is presence-detection, not legal advice.
---

# Security checklist audit

Fill in the user's fixed 16-item security checklist for a given local codebase.
The checklist and its exact wording (do not rephrase items — the output table
must match the original) is reproduced in full under "The checklist" below.

## Why a script does the searching

Every item on this checklist reduces to "does pattern X show up in the code,
and does mitigation Y show up near it." That's mechanical, repetitive across
every audit, and easy to get subtly wrong with ad-hoc grep (case sensitivity,
false positives on English words that happen to look like SQL keywords,
lockfiles polluting unrelated checks — all real bugs hit while building this).
`scripts/scan.py` encodes that logic once. Run it, then reason over its output
rather than re-deriving grep patterns from scratch each time.

## Workflow

1. **Get the repo path** from the user if it isn't obvious from context.

2. **Run the scanner**:
   ```
   python3 <skill_dir>/scripts/scan.py <repo_path>
   ```
   It walks the repo (skipping `node_modules`, `.git`, build output, etc.) and
   prints JSON: for each of the 16 items, a list of `positive_evidence`
   (mitigation present), `negative_evidence` (risky pattern present), and a
   free-text `note` for cases the script can reason about structurally (e.g.
   "no API route files found at all," "no lockfile in this tree"). It also
   prints a top-level `supply_chain_flags` array — see "Supply-chain check"
   below, this is separate from the 16 items — and a top-level `legal_pages`
   object — see "Legal & compliance pages check" below, also separate.

3. **Read the actual matched files**, don't just trust the snippet field, before
   calling anything CONFIRMED. The script does regex matching, not real static
   analysis — it has no AST and no data-flow, so it can't tell a real SQL
   injection from a string that merely contains the word "DELETE," or tell a
   public-by-design Firebase client key from a private API secret. Open the
   file at the reported line and use judgment. This step is what makes the
   audit trustworthy — skipping it turns the skill into a keyword-count
   exercise.

4. **Classify each item** as one of:
   - `CONFIRMED PASS` — clear mitigation evidence, no contradicting risk found
   - `CONFIRMED FAIL` — clear risky pattern, no mitigation found nearby
   - `PARTIAL` — mitigation exists but incomplete (e.g. some API routes check
     auth, others don't; some cookies set `httpOnly` but not `secure`)
   - `NEEDS REVIEW` — script found something ambiguous, or found nothing and
     absence-of-evidence isn't strong enough to call it a clean pass (e.g. zero
     hits on cookie-setting code in a repo that clearly has a login flow —
     that's more likely the scanner's patterns not matching this framework's
     idiom than actual absence of cookies)
   - `N/A` — item doesn't apply to this codebase's architecture (e.g. DDoS
     protection is a hosting/CDN concern, not something that lives in
     application code; rate limiting doesn't apply if there are no API routes
     at all). Always give the one-line reason it's N/A rather than silently
     skipping it — the user should see *why*, not just an empty box.

   Don't default to PASS when the scanner found zero evidence either way.
   Zero hits usually means "this pattern doesn't exist in a form the regex
   recognizes," not "this is definitely handled." That distinction is the
   whole point of separating CONFIRMED from NEEDS REVIEW.

5. **Render the report as a page, not a chat table.** Copy
   `scripts/report_template.html` to a working file (temp dir or the repo
   itself, user's call) and fill in the content per "Output format" below.
   This is the primary deliverable, not a markdown table in chat.

6. **Humanize every word of copy you write into the report.** This is a hard
   requirement on all user-facing text this skill produces: the verdict
   paragraph, the WHAT/WHY lines, every evidence block, the chat summary.
   Apply the `humanizer` skill's rules before you commit any of it. The
   non-negotiable ones: no em or en dashes (`—`, `–`) and no double-hyphen
   `--` used as one; plain `is`/`are`/`has` over "serves as"/"stands as";
   sentence case, not Title Case; no rule-of-three padding; no promotional
   or significance-inflating language; active voice. The copy in
   `scripts/glossary.md` and the example content already in the template are
   written to these rules, so if you copy them faithfully you are most of the
   way there. Grep the finished file for `—`, `–`, and ` -- ` before serving
   it; any hit means it is not done.

7. **Serve it on localhost and open it.** See "Serving the report" below.

8. **In chat, send only a short summary**: the verdict line, the stat counts,
   and the localhost URL, and run that summary through the same humanizer
   rules. The full detail lives on the page. Don't also dump a markdown table
   into the conversation, that is the exact format this was built to replace.

## The checklist

**Frontend Security**
1. Use HTTPS everywhere — Prevents basic eavesdropping and man-in-the-middle attacks
2. Input validation and sanitization — Prevents XSS attacks by validating all user inputs
3. Don't store sensitive data in the browser — No secrets in localStorage or client-side code
4. CSRF protection — Implement anti-CSRF tokens for forms and state-changing requests
5. Never expose API keys in frontend — API credentials should always remain server-side

**Backend Security**
6. Authentication fundamentals — Use established libraries, proper password storage (hashing+salting)
7. Authorization checks — Always verify permissions before performing actions
8. API endpoint protection — Implement proper authentication for every API endpoint
9. SQL injection prevention — Use parameterized queries or ORMs, never raw SQL with user input
10. Basic security headers — Implement X-Frame-Options, X-Content-Type-Options, and HSTS
11. DDoS protection — Use a CDN or cloud service with built-in DDoS mitigation capabilities

**Practical Security Habits**
12. Keep dependencies updated — Most vulnerabilities come from outdated libraries
13. Proper error handling — Don't expose sensitive details in error messages
14. Secure cookies — Set HttpOnly, Secure and SameSite attributes
15. File upload security — Validate file types, sizes, and scan for malicious content
16. Rate limiting — Implement on all API endpoints, especially authentication-related ones

A few checks fold sibling risks into the item they share a root cause with,
rather than getting their own row (the 16 items are fixed — see above):
item 2 also flags `eval()`/`new Function()`/`child_process` sinks, since
"unvalidated input reaching a dangerous sink" is the same failure as XSS, just
with code execution as the payoff instead of script injection — relevant for
apps that generate and run code at request time. Item 13 also flags secrets
(password/token/api key) passed as arguments to `console.log`/`logger.*`
calls — a parallel leak channel to error-messages-in-responses (what item 13's
description names directly): the response can be clean while the exact same
secret still lands in a log line, which is often less access-controlled than
the app itself. Both are name-based heuristics (matches on the argument
looking secret-shaped, not on an actual secret value), so read the hit before
calling it confirmed, same as everywhere else in this skill.

## Output format

The deliverable is a page, not a chat markdown table. `scripts/report_template.html`
is the design system: a clean cybersecurity-report look. Near-black ground with
an olive-green accent, Arial (monospace only for the code in evidence blocks), content
in a centered readable column (`.content`, max-width 940px). Status is shown by
a colored left severity stripe plus a status pill, never a bracket tag. There is
no terminal chrome (no window dots, no `$` prompt, no `//` or `[ ]` markers).
It is single-theme and already tested for evidence collapse, small viewports,
and horizontal overflow. **Copy it, then only replace content. Never restyle it
per repo, and do not bring back a terminal look, extra fonts, or heavy glows.**
It ships with real example content for a past scan (stocks-app); treat every
visible piece of copy as a fill-in-the-blank, not a fixed value:

- `<title>` and the `.masthead` `<h1>` / `.sub`: repo name, files scanned count,
  scan type (leave "static heuristic scan"). Leave the shield SVG as-is.
- The `.posture` band: set its class to `low`, `moderate`, or `high`, and the
  `.risk-badge` text to "Low risk" / "Moderate risk" / "High risk". Compute from
  the worst status present: any FAIL gives `high`; else any WARN gives
  `moderate`; else `low`. The `<p>` under it is one plain-English paragraph
  saying why. This is the single most important paragraph on the page. It is the
  one thing a non-technical user will definitely read, so keep it concrete.
- The `.sevbar`: five `<span>`s (fail / warn / review / secure / na). Set each
  `width` to its share of the 16 items as a percent (count / 16 * 100). The
  `.keys` legend below repeats the raw counts; set each `<b>`.
- The `.legal-panel` up top: one `.legal-row` per legal page the scan checked
  (privacy policy, terms of service, accessibility), each with a `.pill` set to
  `secure` "Present" or `warning` "Missing" from `legal_pages.found` /
  `legal_pages.missing`. This is the at-a-glance legal readout; the full legal
  `.section` lower down carries the detail.
- Each checklist category is one `<section class="section">`: a `.section-head`
  (leave the SVG icon, set the `<h2>` name and the `.count` like "5 items"),
  then a `.list` wrapping that category's `<article class="finding"
  data-status="...">` rows, in the same order as "The checklist" below.
  `data-status` must be one of `fail`, `warning`, `review`, `secure`, `na`. That
  drives the left stripe color through CSS, so don't hardcode it. Inside each
  finding, set the `.pill` class to the same status and its text to the label:
  "Fail", "Warning", "Needs review", "Secure", "Not applicable" (and "Missing"
  for legal pages).
- Inside each finding: the WHAT/WHY lines come from `scripts/glossary.md`,
  close to verbatim, because that copy is already beginner-safe and already
  humanized. Don't re-derive it each run. The `<details class="evidence">`
  block (keep the chevron SVG in the summary) holds the specific finding for
  this repo (file:line, snippet, reasoning). That is where the per-repo judgment
  from steps 3 and 4 shows up. An item with zero evidence either way still gets
  a row; say so plainly in the evidence block ("no matches found for this
  pattern in the repo") rather than dropping the row.
- A final `<section>` for legal pages (`legal_pages.missing` from the scan)
  using `data-status="warning"` and `.pill warning` "Missing". Always render it:
  it is the detail behind the top `.legal-panel`, and the user specifically
  wants legal results shown in full, not only counted. Put supply-chain flags
  here too if `supply_chain_flags` is non-empty, as extra finding rows in their
  own `.section`. The layout does not care how many sections exist.
- The page ends with a `<footer class="report-footer">`, not a bare paragraph.
  It holds two things, always both, in this order:
  1. The `.caveat` disclaimer: keep the wording as-is, it is the same
     disclaimer every run needs.
  2. A `.footer-meta` row: `&copy; <current year> Muhammad Abdullah. All
     rights reserved.` in `.rights` on the left, and `.footer-links` with a
     GitHub link and a LinkedIn link on the right (`justify-content:
     space-between` does the left/right split, don't override it). No emoji
     on the GitHub link, plain text `GitHub`. The name and both URLs are
     `Muhammad Abdullah` / `https://github.com/ma67-ex` /
     `https://linkedin.com/in/ma67` (from the user's memory profile). Don't
     invent placeholder values or ask the user again unless that memory is gone
     or the user gives different links.
- The footer sits at the true bottom of the page: `body` is a flex column
  with `min-height: 100%` and `.content` is `flex: 1` in that column, so
  `.report-footer`'s `margin-top: auto` pushes it to the bottom of the
  viewport on a short report and to the natural end of content on a long one.
  It is not `position: fixed` — a footer fixed to the viewport while
  scrolling would sit on top of the findings list. Keep this flex structure;
  don't collapse `.content` back to a plain block container.

Don't add new CSS classes or inline styles for one-off content. Every finding
uses the same row shape: severity stripe, title, status pill, two paragraphs,
collapsible evidence. If something doesn't seem to fit, it still goes in that
shape.

## Serving the report

Write the filled file as `report.html` in a working directory (a temp/scratch
dir is fine — this doesn't need to live in the user's repo), then serve it on
localhost so it opens as a real page, not a markdown dump in chat:

- **In an environment with a Browser-pane preview tool** (this is the common
  case in Claude Code sessions): add an entry to the project's
  `.claude/launch.json` pointing at `python3 -m http.server <port> --directory
  <dir_containing_report.html>`, then start it with the preview tool and
  navigate to `report.html`. This is the same mechanism as any other dev
  server in this environment — nothing report-specific about it.
- **In a plain CLI environment** (no Browser pane): run
  `python3 <skill_dir>/scripts/serve_report.py <path_to_report.html>`. It
  picks a free port, serves the containing directory, opens the system
  browser, and prints the URL — stdlib only, no dependencies. Tell the user
  the printed `http://localhost:<port>/report.html` URL in case the browser
  didn't auto-open.

Either way, the URL that goes in the chat summary (workflow step 7) is the
real `http://localhost:<port>/...` address, not a file:// path.

### Supply-chain check

The 16 items are about vulnerabilities in the app's own code. There's a fifth
real-world category that's different in kind: the AI tooling that *wrote* the
code getting steered somewhere it shouldn't — a compromised IDE extension, a
malicious dependency, or a repo file that tries to manipulate a coding agent
directly. That doesn't fit as a 17th checklist row (the checklist is fixed,
don't add to it), so `scan.py`'s `supply_chain_flags` output covers two
narrow, checkable shapes of it instead:

- **Agent-instruction files** (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`,
  `.windsurfrules`, etc.) containing directives shaped like a prompt-injection
  attempt against whichever agent reads them — "ignore previous instructions,"
  "fetch this URL before writing any code," that kind of thing. High
  false-positive rate by design: plenty of legitimate setup docs say "read
  the docs before coding" in ways that can pattern-match. Read the actual file
  before flagging anything here as real — this bit personally mattered while
  testing this skill, since a real `AGENTS.md` telling an agent to read
  `node_modules/next/dist/docs/` first turned out to be completely legitimate
  project guidance, not an attack.
- **`package.json` install-lifecycle scripts** (`preinstall`/`install`/
  `postinstall`/`prepare` — these run automatically on `npm install`, no
  explicit opt-in) that fetch-and-execute or use an obfuscated-exec pattern.
  This is a known real supply-chain attack vector independent of whether the
  code was AI-written.

Neither check can tell you whether a dependency itself is backdoored — that
needs the package registry and the actual binary, not this repo's source.
They only catch the two shapes above. Treat every hit as "go read this file,"
never as an automatic verdict.

## Legal & compliance pages check

Separate from the 16-item checklist and from the supply-chain check — this
is site/legal hygiene, not application security, but it's the kind of thing
that's easy to ship a whole app without noticing is missing. `scan.py`'s
`legal_pages` output covers three pages:

- **Privacy Policy** — expected almost anywhere the app collects personal
  data (GDPR/CCPA/similar). `scan.py` treats the site as "collecting data"
  if it finds an email input field, an analytics/tracking script (GA,
  Segment, Mixpanel, Meta Pixel, Hotjar, PostHog...), a payment processor
  (Stripe, PayPal), an email-marketing tool (Mailchimp, ConvertKit,
  Klaviyo, SendGrid), or its own auth/cookie signals (next-auth, Supabase
  auth, Firebase auth, bcrypt/argon2, a `Set-Cookie`/`res.cookie(` call).
  Flagged as missing only carries real weight when `site_collects_data` is
  `true` — a static site with no forms and no analytics genuinely may not
  need one.
- **Terms of Service / Terms of Use** — not tied to data collection the same
  way; flagged for any site since it's the normal baseline for anything with
  accounts, user content, or paid features, but weigh it against how public
  and how commercial the project actually is (a personal portfolio site is a
  much weaker case than a SaaS app taking signups).
- **Accessibility Statement** — the "disability page": under the ADA (and
  similar rules elsewhere), U.S. public-facing sites are expected to be
  usable by people with disabilities, and a growing number publish a short
  accessibility statement alongside actual WCAG-conformant markup. Having
  the statement page without the underlying accessibility work behind it is
  close to worthless — treat a missing statement as a prompt to ask whether
  accessibility was considered at all, not just as a missing page to add.

**How detection works, and its limits**: the script looks for a page whose
file path matches the expected slug (e.g. `pages/privacy.tsx`,
`app/terms/page.tsx`, `privacy-policy.html`); if no page file is found, it
falls back to a text match for a link or mention (`/privacy`, "Privacy
Policy", etc.) anywhere in scanned source, on the theory that a link is
weaker evidence than a real page but still worth surfacing as "found." A
page that exists but is copy-pasted boilerplate, outdated, or doesn't match
what the app actually does won't be caught here — presence, not adequacy,
is all this checks. It also has no way to know which jurisdiction's rules
actually bind this specific project (GDPR vs. CCPA vs. nothing at all
depends on where the users are, not where the code is written).

**Always caveat this section as informational, not legal advice** — say so
explicitly in the Notes section if `legal_pages.missing` is non-empty, and
suggest the user confirm requirements with an actual lawyer for anything
beyond a personal/hobby project.

## Defense-in-depth checks folded into existing items

A production-grade setup has more layers than the 16 items name individually
(network-level DDoS/WAF, bot gating, secrets vaults, DB transport encryption,
error monitoring). Rather than invent new rows for these — the checklist is
fixed — `scan.py` folds each into whichever existing item it's closest to in
spirit, as extra evidence or a note:

- **Bot/abuse gating** (item 8): distinct from item 16's rate limiting — rate
  limiting throttles by request count, this identifies non-human/scripted
  callers up front (a same-origin `Sec-Fetch-Site`/`Origin` check, or a
  challenge widget like Turnstile/reCAPTCHA/hCaptcha). Detected as positive
  evidence, folded into item 8's note.
- **DB connection encryption** (item 1): "encrypt in transit" applies to the
  app's DB connection, not just the browser↔server hop. An explicit
  `sslmode=disable` or `ssl: false` on a connection string/ORM config is a
  plain, checkable anti-pattern — flagged as negative evidence right alongside
  the existing HTTP checks.
- **Secrets vault vs. bare `.env`** (item 5): not a pass/fail — plenty of
  small projects reasonably keep secrets in platform env vars rather than a
  dedicated vault (AWS Secrets Manager, GCP Secret Manager, Vault, Infisical,
  Doppler...), and that's fine at that scale. Recorded as an informational
  note so the audit at least surfaces the question for anything handling
  other people's data.
- **Error monitoring** (item 13): a different concern from item 13's own
  description ("don't leak error details to the client") — this is about
  whether errors get captured server-side at all (Sentry, Datadog, LogRocket,
  Rollbar, Bugsnag, New Relic). No monitoring tool isn't a vulnerability by
  itself, so it's a note, not a fail.
- **DDoS/CDN** (item 11): already checked for Vercel; also recognizes
  Cloudflare (`wrangler.toml` or a `cloudflare` dependency).

None of these five are hard pass/fail signals the way, say, a hardcoded
Stripe secret key is — they're maturity notes. Use judgment on how much they
matter for the project's actual scale (a personal project not having a
secrets vault is normal; a healthcare app not having one is a real finding).

## Common judgment calls

These come up on almost every real repo — worth knowing going in rather than
re-deriving each time:

- **"A code-shaped value in a username/password field should error, not
  run"**: a web app never literally compiles or executes a text field's
  contents just because it was typed into a form — the browser and server
  both treat it as inert text unless something explicitly hands it to an
  interpreter. So this concern splits into two real, separately-checked
  pieces rather than one: (1) does *anything* in the app actually execute
  user input — covered by item 2's `eval`/`new Function`/`child_process`
  sink check; and (2) does the identity field itself have any format check at
  all before use — `scan.py` flags a login/signup handler that destructures
  `username`/`email`/`password` straight off the request body with no
  `.test(`/zod/yup/joi/`validator.js` pattern nearby, under item 2. A repo can
  have a validation library installed and still never call it on the one form
  that matters, which is why this is a separate check from "is there a
  validation library anywhere in the repo" (item 2's positive-evidence
  check). Neither is dangerous by itself — the risk only materializes once
  that unchecked value reaches a sink (XSS, SQL, eval, mass assignment) that
  the other item 2/9 checks already cover.
- **"Someone else's URL shouldn't just work if pasted in"**: this is IDOR,
  and it's what item 7's raw-id-no-owner-check detection is for — a route
  that reads an id straight from the request/URL and queries or mutates by
  it with no ownership check anywhere in the file means any signed-in user
  (or in some setups, anyone) who gets or guesses that URL can act on it.
  `scan.py` flags this under item 7, with a distinct "DESTRUCTIVE" label when
  the matched call is a delete/remove/drop rather than a read, since handing
  someone the ability to delete another user's data is worse than letting
  them merely view it.

- **Firebase/Supabase/other BaaS client keys**: these are *meant* to be
  public — they're identifiers, not secrets, and access is controlled by the
  provider's security rules, not by hiding the key. Finding one hardcoded in
  client code is not automatically a FAIL for item 5; check whether the
  project's security rules (Firestore rules, RLS policies, etc.) actually
  exist and are restrictive. If you can't verify the rules from the repo, mark
  NEEDS REVIEW with that explanation rather than FAIL.
- **Supabase anon key vs service_role key — do not conflate these.** The anon
  key is the public, safe-by-design one (same category as a Firebase client
  key above). The `service_role` key is a full DB admin credential that
  bypasses Row Level Security entirely — finding *that* one in client-reachable
  code is a real CONFIRMED FAIL, not a judgment call. `scan.py`'s generic
  "env var name contains KEY" pattern can't tell these apart (both match) and
  will flag `NEXT_PUBLIC_SUPABASE_ANON_KEY` alongside a real `service_role`
  leak — always read the actual variable name before verdict-ing item 5 on a
  Supabase project. When Supabase is detected, `scan.py` also leaves a note on
  item 7 pointing at Row Level Security as the real enforcement layer, same
  idea as Firestore rules above.
- **Broken access control / IDOR** (a route that takes an id from the request
  and reads/writes/deletes by it with no ownership check anywhere in the
  file) was the second most common finding in a field study of 2,096
  vibe-coded apps — 25.6% of apps had it, including cases with sequential,
  guessable integer IDs on top. `scan.py` flags routes matching this shape
  under item 7 as a soft lead ("possible IDOR, read by hand") — it can't see
  whether the ownership check happens in middleware or a shared helper
  imported from elsewhere, so always trace the actual call path before
  calling it CONFIRMED. If confirmed, this is a FAIL, not a NEEDS REVIEW —
  an enumerable id with no auth check is a real, exploitable bug, not a
  theoretical one. `scan.py` calls out delete/destroy-shaped matches
  (`.delete(`, `deleteDoc(`, `DELETE FROM`, ...) as "DESTRUCTIVE" specifically
  — an unauthenticated read is bad, an unauthenticated delete is worse, and
  the snippet says so rather than burying it next to a plain GET.
- **SSRF** (item 8): a route that makes an outbound request to a URL it read
  from the client hands the client control over what the server fetches —
  not just the public internet, but internal-only services and metadata
  endpoints the server can reach but the client normally couldn't. `scan.py`'s
  heuristic is intentionally loose (outbound call with a variable destination,
  *and* the file separately reads request input into something URL/host-shaped
  — doesn't trace whether they're actually the same value), so expect false
  positives on routes that read user input for an unrelated reason. Confirm by
  actually tracing the destination argument before calling this a FAIL.
- **Mass assignment** (item 2): `db.update({ ...req.body })` or
  `create(req.body)` writes whatever fields the client included, not just the
  ones the form intended — the textbook version is a signup handler where the
  client adds `"isAdmin": true` to their request JSON and becomes an admin,
  because nothing on the backend decided which fields were writable. Look for
  an explicit allowlist (destructuring specific fields, a zod schema with
  `.strict()` or `.pick()`) near the flagged call before ruling this out.
- **Next.js App Router RSC payload leaks** — a subtler, easy-to-miss pattern:
  a Server Component fetches something from a DB/config (which may include
  secrets, e.g. a settings row that also has an API key column) and passes
  the *whole object* as a prop to a Client Component, or spreads it into JSX.
  That entire object — including any secret fields — gets serialized into the
  RSC payload embedded in the page's HTML. The app runs and renders
  perfectly, which is exactly why this doesn't surface on a normal read; it
  only shows up if you look at what the Client Component actually receives
  and ships. `scan.py` has a rough proximity heuristic for this under item 5
  (server-side fetch + object-spread-into-props in the same file) with a high
  false-positive rate by design — when it fires, actually trace what fields
  are in the fetched object and whether any of them are secrets before
  calling it a real finding. This one has no cheap N/A-out: if the project
  uses the App Router and fetches anything from a database in a Server
  Component, it's worth a manual look regardless of what the regex says.
- **No API routes at all**: a lot of small projects are client-only apps
  talking directly to a BaaS. Items 7, 8, and 16 (authorization, API
  endpoint protection, rate limiting) become N/A for the *application code*
  layer in that case — but say so explicitly, and note that the BaaS's own
  security rules are where that enforcement actually needs to live.
  `scan.py` already flags this via its `note` field when it finds zero API
  route files.
- **Rate limiting is checked per-route, not repo-wide** — a first version of
  `scan.py` marked item 16 a blanket PASS the moment *any* file mentioned a
  rate-limit library, which meant one protected endpoint could hide five
  unprotected ones. Now each route file gets its own verdict: PASS if it
  references a rate-limit call directly, PASS (with a note to verify config)
  if `middleware.ts` applies it repo-wide, NEEDS REVIEW if a rate-limit
  library exists somewhere else in the repo but isn't provably wired to this
  route, and FAIL if there's no rate-limit signal anywhere. Also matches
  hand-rolled limiters, not just named packages (`express-rate-limit`, etc.)
  — a plain word-boundary regex misses something like `checkRateLimit(`
  because there's no actual word-break inside a camelCase identifier for
  `\b` to land on.
- **Zero cookie-related matches**: don't read this as "cookies are secure,"
  read it as "this app may not be setting cookies you can find with a
  regex" — could be token-in-header auth instead (which sidesteps CSRF
  differently), or the pattern just didn't match this framework's syntax.
  Check how the app actually handles sessions before deciding.
- **DDoS protection**: essentially never verifiable from application code.
  If there's a `vercel.json`, Cloudflare config, or similar, note the
  platform provides it by default and mark N/A. Otherwise mark N/A with "infra-level
  concern, verify at the hosting layer" rather than FAIL — application code
  not doing DDoS mitigation is normal, not a defect.
- **"Can someone open dev tools and read PII?" (item 3)**: this is the
  question of what a curious user finds in the browser, and it splits into a
  static part and a runtime part. The static part — which `scan.py` covers —
  is anything baked into the client bundle or written to browser storage:
  PII-shaped `localStorage`/`sessionStorage` keys (broadened well past
  token/password to email/phone/address/dob/name/etc.), hardcoded email
  addresses / SSN-shaped / card-shaped literals in frontend source (emails
  get noise-filtered against `example.com`/`noreply`/vendor hosts, but a
  surviving hit still needs a human read — a `support@` address is usually
  fine, a real person's personal email is not), and data hung off `window.*`
  or `__STATE__`/`__USER__`-style globals that are directly inspectable from
  the console. The runtime part — what actually sits in React/Redux DevTools
  state, or how much PII an API response over-returns and shows in the Network
  tab — a static scan genuinely cannot see. When item 3 comes back clean from
  the scanner but the app clearly handles real user data, say so: mark it
  NEEDS REVIEW with a note that the static side looks fine but the Network-tab
  / component-state side needs an actual look in the running app, rather than
  reporting a confident PASS the scan can't back up.

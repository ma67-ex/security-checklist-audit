# Plain-English glossary for the security + legal report

For each checklist item and legal page, a beginner-safe "what" and "why", with
no jargon assumed. Use this copy close to verbatim when filling the WHAT/WHY
text in `report.html`. It is already written to the humanizer rules (no em or
en dashes, plain language, sentence case), so copying it faithfully keeps every
run clean. Swap in the actual finding for the specific project in the evidence
block; this glossary is the constant explainer text, not the per-repo evidence.

## Frontend security

**1. Use HTTPS everywhere**
- What it checks: whether your site encrypts data between visitors' browsers and your server.
- Why it matters: without it, anyone on the same network as your visitor can read or change everything they send, including passwords and form data.

**2. Input validation and sanitization**
- What it checks: whether text visitors type in, like comments or search boxes, gets checked before your site trusts it.
- Why it matters: unchecked input is how attackers slip in malicious scripts (called XSS) that run in other people's browsers and steal their sessions. In worse cases it tricks your server into running attacker code.

**3. Don't store sensitive data in the browser**
- What it checks: whether passwords, tokens, or personal info end up sitting in the browser, where anyone with dev tools open can read them.
- Why it matters: browser storage is not private. A shared computer or a simple "view source" can expose it.

**4. CSRF protection**
- What it checks: whether actions on your site, like changing an email, can be triggered by a link or form on some other website your visitor has open.
- Why it matters: without protection, a malicious page can quietly submit actions as your logged-in visitor, using their own session against them.

**5. Never expose API keys in frontend**
- What it checks: whether secret credentials for other services end up baked into the code that visitors' browsers download.
- Why it matters: anything sent to the browser can be pulled back out by anyone. A leaked key can mean someone else runs up your bill or reaches your backend services directly.

## Backend security

**6. Authentication fundamentals**
- What it checks: how your app confirms who a person is, and how it stores their password.
- Why it matters: writing your own login, or storing passwords as plain text, is one of the most common ways real apps get taken over.

**7. Authorization checks**
- What it checks: whether the app confirms a specific user is allowed to see or change a specific thing, not just that they are logged in at all.
- Why it matters: without it, any logged-in user, and sometimes anyone, can view or delete someone else's data by changing an id in the URL. This bug is called IDOR and it is one of the most common in real apps.

**8. API endpoint protection**
- What it checks: whether each backend endpoint confirms who is calling it before doing anything.
- Why it matters: an unprotected endpoint is an open door. Anyone who finds the URL can use it, whether or not they were meant to.

**9. SQL injection prevention**
- What it checks: whether database queries are built safely, or by gluing user input straight into a query string.
- Why it matters: a crafted input can let an attacker read, change, or delete your whole database. This is an old attack that still works today.

**10. Basic security headers**
- What it checks: a few small server settings that tell browsers extra rules to follow, like refusing to let another site frame yours.
- Why it matters: they are cheap to add and they shut down several kinds of attack, like clickjacking, almost for free.

**11. DDoS protection**
- What it checks: whether something in front of your app can absorb a flood of junk traffic meant to take it down.
- Why it matters: without it, a big enough flood of requests can knock your site offline. This is usually a hosting or CDN job, not application code.

## Practical security habits

**12. Keep dependencies updated**
- What it checks: whether the outside libraries your code relies on are reasonably current.
- Why it matters: most real vulnerabilities come from a known, already-fixed bug in an outdated library, not from a new attack.

**13. Proper error handling**
- What it checks: whether error messages shown to users, or written to logs, leak internal details like file paths or secrets.
- Why it matters: a detailed error is a gift to an attacker. It shows exactly how your app is built and makes it easier to find a way in.

**14. Secure cookies**
- What it checks: whether the small pieces of data (cookies) your site stores in the browser have the right protective flags set.
- Why it matters: missing flags let cookies, which are often login tokens, get stolen through injected scripts or sent over an unencrypted connection.

**15. File upload security**
- What it checks: whether files visitors upload get checked for type and size before your server accepts them.
- Why it matters: an unchecked upload can let someone plant a harmful file on your server, and in the worst case one that runs.

**16. Rate limiting**
- What it checks: whether there is a cap on how many times someone can hit an endpoint in a given stretch of time.
- Why it matters: without a cap, attackers can guess passwords over and over, spam your API, or run up your bill as fast as they want.

## Legal and compliance pages

**Privacy policy**
- What it is: a page that tells visitors what personal data you collect and what you do with it.
- Why it matters: it is legally required in most places, including the EU (GDPR) and California (CCPA), the moment you collect any personal data through forms, analytics, accounts, or cookies.

**Terms of service**
- What it is: the rules visitors and users agree to by using your site.
- Why it matters: it protects you legally and sets expectations, which matters most once you have accounts, payments, or user-posted content.

**Accessibility statement**
- What it is: a page describing how your site supports people with disabilities, such as screen reader and keyboard support. Some people call this the disability page.
- Why it matters: it is expected for many public US sites under the ADA, and it matters regardless of the law because a real share of visitors rely on it. The statement only means something alongside a site that is actually usable, so treat it as a prompt to check real accessibility, not a box to tick.

## Sub-checks that fold into an item above

Mention the specific name in the explanation, but use the parent item's status.

- IDOR (folds into item 7): a URL that lets you act on someone else's data just by changing an id in it.
- SSRF (folds into item 8): a route that lets a visitor make your server fetch a URL of their choosing, including internal addresses it should not be able to reach.
- Mass assignment (folds into item 2): a form handler that writes every field the client sent, letting someone add fields you never meant them to set, like `isAdmin: true`.
- RSC payload leak (folds into item 5, Next.js App Router only): a server component that loads something with secret fields and passes the whole object to the client, leaking those fields into the page's HTML.

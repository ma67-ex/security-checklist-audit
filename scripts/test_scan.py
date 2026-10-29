"""Self-check for scan(). Run: python3 scripts/test_scan.py"""
import os
import shutil
import tempfile

from scan import scan, find_matches


def _write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def _items(root):
    return {i["id"]: i for i in scan(root)}


def test_repo_location_does_not_change_what_counts_as_frontend_or_api():
    # A project that happens to live under a folder named api/ or routes/ must be judged by its own layout.
    base = tempfile.mkdtemp()
    try:
        for parent in ("api", "routes", "server"):
            root = os.path.join(base, parent, "myapp")
            _write(root, "src/Home.js", 'const stripeKey = "sk_live_abcdefghijklmnopqrstuv";\n')
            items = _items(root)
            assert any("Home.js" in m["file"] for m in items[5]["negative_evidence"]), (parent, items[5])
            assert not items[8]["negative_evidence"], (parent, "Home.js is not an API route", items[8]["negative_evidence"])
            assert not items[16]["negative_evidence"], (parent, items[16]["negative_evidence"])
    finally:
        shutil.rmtree(base)


def test_real_api_routes_are_still_found_in_a_plain_location():
    root = tempfile.mkdtemp()
    try:
        _write(root, "pages/api/items.js", "export default function handler(req, res) { res.json([]) }\n")
        items = _items(root)
        assert [m["file"] for m in items[8]["negative_evidence"]] == ["pages/api/items.js"], items[8]
        assert [m["file"] for m in items[16]["negative_evidence"]] == ["pages/api/items.js"], items[16]
    finally:
        shutil.rmtree(root)


def test_each_cookie_is_judged_by_its_own_options():
    root = tempfile.mkdtemp()
    try:
        _write(root, "pages/api/login.js", (
            'export default function a(req, res) {\n'
            '  res.cookie("s", token, {\n'
            '    httpOnly: true, secure: true });\n'
            '}\n'
            'export function b(req, res) {\n'
            '  res.cookie("s", token, {\n'
            '    path: "/" });\n'
            '}\n'))
        item = _items(root)[14]
        assert [m["line"] for m in item["positive_evidence"]] == [2], item
        assert [m["line"] for m in item["negative_evidence"]] == [6], item
    finally:
        shutil.rmtree(root)


def test_find_matches_reports_the_right_lines_and_skips_comments():
    text = "// innerHTML = x\nconst a = 1\nel.innerHTML = y\n# innerHTML = z\n"
    hits = find_matches(text, r"innerHTML\s*=", "f.js")
    assert [(h["line"], h["snippet"]) for h in hits] == [(3, "el.innerHTML = y")], hits


if __name__ == "__main__":
    import sys
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("ok   ", name)
        except AssertionError as e:
            failed += 1
            print("FAIL ", name, "-", str(e)[:200])
    print(f"{len(tests) - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)

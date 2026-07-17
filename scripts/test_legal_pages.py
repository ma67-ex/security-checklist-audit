"""Self-check for scan_legal_pages(). Run: python3 scripts/test_legal_pages.py"""
import os
import shutil
import tempfile

from scan import scan_legal_pages, iter_files


def test_detects_page_and_flags_missing_ones():
    root = tempfile.mkdtemp()
    try:
        pages = os.path.join(root, "pages")
        os.makedirs(pages)
        with open(os.path.join(pages, "privacy.jsx"), "w") as f:
            f.write("export default function Privacy() { return <div>Privacy Policy</div>; }")
        with open(os.path.join(pages, "signup.jsx"), "w") as f:
            f.write('<input type="email" name="email" /><script>gtag("config")</script>')

        result = scan_legal_pages(root, list(iter_files(root)))

        assert result["found"]["privacy_policy"] == ["pages/privacy.jsx"], result["found"]
        missing_pages = {m["page"] for m in result["missing"]}
        assert missing_pages == {"Terms of Service / Terms of Use", "Accessibility Statement"}, missing_pages
        for m in result["missing"]:
            assert m["site_collects_data"] is True, m
    finally:
        shutil.rmtree(root)


def test_no_signals_no_false_flag_on_data_collection():
    root = tempfile.mkdtemp()
    try:
        with open(os.path.join(root, "index.jsx"), "w") as f:
            f.write("export default function Home() { return <div>Hello</div>; }")

        result = scan_legal_pages(root, list(iter_files(root)))

        assert {m["page"] for m in result["missing"]} == {
            "Privacy Policy", "Terms of Service / Terms of Use", "Accessibility Statement",
        }
        assert all(m["site_collects_data"] is False for m in result["missing"])
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    test_detects_page_and_flags_missing_ones()
    test_no_signals_no_false_flag_on_data_collection()
    print("OK")

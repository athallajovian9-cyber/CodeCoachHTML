"""Tests for CodeCoach HTML analyzer."""
import unittest
import html_silent as HS


class TestHTMLAnalyzer(unittest.TestCase):
    def test_clean_html_has_no_findings(self):
        code = """<!DOCTYPE html>
<html>
<head><title>My Game</title></head>
<body>
    <h1>Welcome</h1>
    <p>Hello world!</p>
    <img src="avatar.png" alt="Player avatar">
    <a href="https://example.com">Click</a>
</body>
</html>"""
        findings = HS.check_html(code)
        self.assertEqual(len(findings), 0)

    def test_unclosed_tag_detected(self):
        code = "<div><p>Unclosed paragraph</div>"
        findings = HS.check_html(code)
        self.assertTrue(any(f.kind == "unclosed_tag" for f in findings))

    def test_missing_img_src_detected(self):
        code = "<img alt='Broken pic'>"
        findings = HS.check_html(code)
        self.assertTrue(any(f.kind == "img_missing_src" for f in findings))

    def test_empty_link_detected(self):
        code = "<a href=''>Nowhere</a>"
        findings = HS.check_html(code)
        self.assertTrue(any(f.kind == "empty_href" for f in findings))

    def test_extra_closing_tag_detected(self):
        code = "<p>Text</p></div>"
        findings = HS.check_html(code)
        self.assertTrue(any(f.kind == "extra_close_tag" for f in findings))


if __name__ == "__main__":
    unittest.main()

"""HTML and CSS linter / analyzer for kid web coders.
Detects common beginner mistakes in HTML & CSS without requiring external libraries.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class Finding:
    kind: str
    line: int
    name: str
    title: str
    plain: str
    parent_says: str
    fix_hint: str
    search: str


VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}


class CodeCoachHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_stack: list[tuple[str, int]] = []
        self.findings: list[Finding] = []
        self.has_doctype = False
        self.has_title = False
        self.has_body = False
        self.img_without_alt: list[int] = []

    def handle_decl(self, decl: str):
        if "doctype html" in decl.lower():
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        tag = tag.lower()
        line = self.getpos()[0]

        if tag == "title":
            self.has_title = True
        elif tag == "body":
            self.has_body = True
        elif tag == "img":
            attr_dict = {k.lower(): v for k, v in attrs}
            if "src" not in attr_dict or not attr_dict["src"]:
                self.findings.append(
                    Finding(
                        kind="img_missing_src",
                        line=line,
                        name="<img>",
                        title="Image tag <img> is missing its src file path",
                        plain="An <img> needs src='...' so the browser knows which picture file to show.",
                        parent_says="Does your <img> tag have a src pointing to your picture file?",
                        fix_hint="Add src='picture.png' inside your <img> tag.",
                        search="html img src attribute",
                    )
                )
            if "alt" not in attr_dict:
                self.img_without_alt.append(line)

        if tag not in VOID_TAGS:
            self.tag_stack.append((tag, line))

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        line = self.getpos()[0]
        if tag in VOID_TAGS:
            return

        if not self.tag_stack:
            self.findings.append(
                Finding(
                    kind="extra_close_tag",
                    line=line,
                    name=f"</{tag}>",
                    title=f"Closing </{tag}> found without an opening tag",
                    plain=f"The tag </{tag}> was closed, but there was no matching <{tag}> opened earlier.",
                    parent_says=f"Look at line {line}: is there an extra </{tag}>?",
                    fix_hint=f"Remove the extra </{tag}> or add <{tag}> above it.",
                    search=f"html closing tag without opening tag {tag}",
                )
            )
            return

        # Check stack top
        top_tag, top_line = self.tag_stack[-1]
        if top_tag == tag:
            self.tag_stack.pop()
        else:
            # Check if tag is further down stack
            matching_idx = None
            for idx in range(len(self.tag_stack) - 1, -1, -1):
                if self.tag_stack[idx][0] == tag:
                    matching_idx = idx
                    break

            if matching_idx is not None:
                # Unclosed tags in between
                unclosed = self.tag_stack[matching_idx + 1:]
                for u_tag, u_line in unclosed:
                    self.findings.append(
                        Finding(
                            kind="unclosed_tag",
                            line=u_line,
                            name=f"<{u_tag}>",
                            title=f"Tag <{u_tag}> was opened on line {u_line} but never closed before </{tag}>",
                            plain=f"Tags should be closed in reverse order. <{u_tag}> was opened inside, but </{tag}> closed before it.",
                            parent_says=f"Did you forget to close </{u_tag}> before closing </{tag}>?",
                            fix_hint=f"Add </{u_tag}> before line {line}.",
                            search=f"html unclosed tag {u_tag}",
                        )
                    )
                self.tag_stack = self.tag_stack[:matching_idx]
            else:
                self.findings.append(
                    Finding(
                        kind="mismatched_close_tag",
                        line=line,
                        name=f"</{tag}>",
                        title=f"Mismatched closing tag </{tag}> (expected </{top_tag}> from line {top_line})",
                        plain=f"The browser expected to close </{top_tag}> next, but found </{tag}> instead.",
                        parent_says=f"Line {line} closes </{tag}>, but <{top_tag}> from line {top_line} is still open.",
                        fix_hint=f"Change </{tag}> to </{top_tag}> or close <{top_tag}> first.",
                        search=f"html mismatched closing tag",
                    )
                )


def check_html(source: str, path: str = "") -> list[Finding]:
    parser = CodeCoachHTMLParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception as e:
        return [
            Finding(
                kind="parse_error",
                line=1,
                name="html",
                title=f"HTML syntax error: {str(e)}",
                plain="The HTML structure has an unexpected character or broken tag.",
                parent_says="Check your opening and closing angle brackets < > for typos.",
                fix_hint="Check brackets < and >.",
                search="html syntax error",
            )
        ]

    findings = list(parser.findings)

    # Any remaining unclosed tags
    for tag, line in parser.tag_stack:
        findings.append(
            Finding(
                kind="unclosed_tag",
                line=line,
                name=f"<{tag}>",
                title=f"Tag <{tag}> on line {line} is never closed",
                plain=f"You opened <{tag}>, but never added </{tag}> to close it.",
                parent_says=f"Can you find where <{tag}> from line {line} should end and add </{tag}>?",
                fix_hint=f"Add </{tag}> where this element ends.",
                search=f"html unclosed tag {tag}",
            )
        )

    # Check for empty links
    lines = source.splitlines()
    for idx, l in enumerate(lines, 1):
        if re.search(r'<a\s+href=["\']\s*["\']', l, re.IGNORECASE):
            findings.append(
                Finding(
                    kind="empty_href",
                    line=idx,
                    name="<a>",
                    title="Link <a href=''> has an empty destination",
                    plain="The link tag <a> doesn't go anywhere because the href is blank.",
                    parent_says="Where should this link go? Put a website link or file name in href='...'",
                    fix_hint="Change href='' to href='https://...' or href='page.html'.",
                    search="html empty href link",
                )
            )

        # Broken style attributes
        if "style=" in l:
            # Unclosed style quote
            if l.count('style="') and l.count('"') % 2 != 0:
                findings.append(
                    Finding(
                        kind="unclosed_style_quote",
                        line=idx,
                        name="style",
                        title="Style attribute has an unclosed quotation mark",
                        plain="A style='...' attribute started a quotation mark but never closed it.",
                        parent_says="Check the quotation marks around your CSS style attribute.",
                        fix_hint="Make sure style='...' has quotes on both sides.",
                        search="html style attribute unclosed quote",
                    )
                )

    findings.sort(key=lambda f: f.line)
    return findings

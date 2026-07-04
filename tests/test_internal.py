"""Unit tests for internal helpers of the native extractor."""

from parsel import Selector

from parsel_text import (
    _collapse_whitespace,
    _iter_text_parts,
    _outermost,
    remove_trailing_chars,
)


def roots(html, xpath):
    """lxml elements matched by *xpath* (for exercising element-level helpers)."""
    return [s.root for s in Selector(text=html).xpath(xpath)]


# --------------------------------------------------------------------------- #
# _collapse_whitespace (and its backwards-compat alias remove_trailing_chars).
# --------------------------------------------------------------------------- #
class TestCollapseWhitespace:
    def test_collapses_internal_spaces(self):
        assert _collapse_whitespace("a   b") == "a b"

    def test_strips_both_ends(self):
        assert _collapse_whitespace("  a  ") == "a"

    def test_collapses_tabs_and_newlines(self):
        assert _collapse_whitespace("a\tb\nc") == "a b c"

    def test_collapses_nbsp(self):
        assert _collapse_whitespace("a  b") == "a b"

    def test_empty_and_whitespace_only(self):
        assert _collapse_whitespace("") == ""
        assert _collapse_whitespace("   \t\n  ") == ""

    def test_remove_trailing_chars_is_the_same_shim(self):
        assert remove_trailing_chars("  a   b\tc\nd  ") == "a b c d"


# --------------------------------------------------------------------------- #
# _iter_text_parts: descendant text of one element, cleaned, in order.
# --------------------------------------------------------------------------- #
class TestIterTextParts:
    def test_order_and_segmentation(self):
        (div,) = roots("<div>A<span>B</span>C</div>", "//div")
        assert _iter_text_parts(div) == ["A", "B", "C"]

    def test_excludes_script_keeps_tail(self):
        (body,) = roots("<body>x<script>SECRET</script>y</body>", "//body")
        assert _iter_text_parts(body) == ["x", "y"]

    def test_excludes_noscript(self):
        (art,) = roots("<article>hi<noscript>NS</noscript>bye</article>", "//article")
        assert _iter_text_parts(art) == ["hi", "bye"]

    def test_preserves_pre_whitespace(self):
        (pre,) = roots("<pre>a\n    b</pre>", "//pre")
        assert _iter_text_parts(pre) == ["a\n    b"]

    def test_whitespace_only_dropped(self):
        (div,) = roots("<div>  <span> </span>  </div>", "//div")
        assert _iter_text_parts(div) == []


# --------------------------------------------------------------------------- #
# _outermost: drop matches nested inside other matches (the de-dup rule).
# --------------------------------------------------------------------------- #
class TestOutermost:
    def test_keeps_only_outer_of_nested(self):
        divs = roots("<div id='o'><div id='i'>x</div></div>", "//div")
        kept = _outermost(divs)
        assert len(kept) == 1
        assert kept[0].get("id") == "o"

    def test_keeps_all_disjoint(self):
        divs = roots("<body><div>a</div><div>b</div></body>", "//div")
        assert len(_outermost(divs)) == 2

    def test_empty(self):
        assert _outermost([]) == []

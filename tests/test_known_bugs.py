"""Bug ledger: xfail(strict) tests asserting the DESIRED behaviour.

These fail today (documenting known bugs) and are collected as ``xfail``.
``xfail_strict = true`` (pyproject) means that once a refactor fixes the bug the
test XPASSes and *fails the suite* -- the signal to delete the xfail mark and
promote it to a normal passing test.
"""

import pytest

from conftest import (
    README_HTML,
    deep_nested_html,
    load_fixture,
    mojibake,
    sel,
    soup,
)

from parsel_text import get_bs4_soup_text, get_results_row_text, get_xpath_text


@pytest.mark.xfail(
    reason="rstrip on lines 76/99 is a no-op (return value discarded); "
    "output keeps a trailing newline.",
)
def test_get_xpath_text_has_no_trailing_newline():
    result = get_xpath_text(parsel_sel=sel(README_HTML), xpath="//p")
    assert not result.endswith("\n")


@pytest.mark.xfail(
    reason="get_xpath_row_results has the same no-op rstrip; rows keep a trailing newline.",
)
def test_get_results_row_text_rows_have_no_trailing_newline():
    rows = get_results_row_text(
        parsel_sel=sel("<ul><li>a</li><li>b</li></ul>"), xpath="//li"
    )
    assert all(not row.endswith("\n") for row in rows)


@pytest.mark.xfail(
    reason="get_bs4_soup_text hardcodes fix_mojibake=True; there is no way to "
    "disable mojibake correction (the parameter does not exist -> TypeError).",
)
def test_get_bs4_soup_text_honours_fix_mojibake_false():
    raw = mojibake("café")
    result = get_bs4_soup_text(bs4_soup=soup("<div>" + raw + "</div>"), fix_mojibake=False)
    assert raw in result


# --------------------------------------------------------------------------- #
# Findings from the production-HTML exploration (2026-07-04). The user asked to
# treat these as bugs to fix in the refactor.
# --------------------------------------------------------------------------- #
@pytest.mark.xfail(
    reason="An xpath matching nested same-type elements (e.g. //div) re-extracts "
    "each matched subtree, so descendant text is duplicated once per nesting level.",
)
def test_nested_selector_does_not_duplicate():
    out = get_xpath_text(parsel_sel=sel("<div><div>DUP</div></div>"), xpath="//div")
    assert out.count("DUP") == 1


@pytest.mark.xfail(
    reason="traverse_soup is recursive; a DOM nested >= ~1000 levels overflows the "
    "Python stack (RecursionError). A parsel .//text() rewrite (C-level) fixes it.",
)
def test_deep_dom_does_not_crash():
    out = get_xpath_text(parsel_sel=sel(deep_nested_html(1500)), xpath="//body")
    assert "DEEP_LEAF" in out


@pytest.mark.xfail(
    reason="remove_trailing_chars collapses all whitespace, destroying significant "
    "indentation/newlines inside <pre>/<code> (code/poetry data loss).",
)
def test_pre_code_preserves_indentation():
    out = get_xpath_text(parsel_sel=sel(load_fixture("whitespace.html")), xpath="//code")
    assert "\n    if n < 2" in out


@pytest.mark.xfail(
    reason="<noscript> fallback text (usually non-content) is included; it should be "
    "excluded like <script>/<style>.",
)
def test_noscript_excluded():
    out = get_xpath_text(parsel_sel=sel(load_fixture("news.html")), xpath="//article")
    assert "NOSCRIPT_MARKER" not in out

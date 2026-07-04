"""Regression tests for the bugs fixed by the parsel-native refactor.

Each of these was an xfail(strict) entry in the pre-refactor bug ledger. Now they
must stay green -- if one fails, one of the fixes regressed.
"""

from conftest import README_HTML, deep_nested_html, load_fixture, mojibake, sel, soup

from parsel_text import get_bs4_soup_text, get_results_row_text, get_xpath_text


def test_get_xpath_text_has_no_trailing_newline():
    result = get_xpath_text(parsel_sel=sel(README_HTML), xpath="//p")
    assert not result.endswith("\n")


def test_get_results_row_text_rows_have_no_trailing_newline():
    rows = get_results_row_text(
        parsel_sel=sel("<ul><li>a</li><li>b</li></ul>"), xpath="//li"
    )
    assert all(not row.endswith("\n") for row in rows)


def test_get_bs4_soup_text_honours_fix_mojibake_false():
    raw = mojibake("café")
    result = get_bs4_soup_text(bs4_soup=soup("<div>" + raw + "</div>"), fix_mojibake=False)
    assert raw in result


def test_nested_selector_does_not_duplicate():
    out = get_xpath_text(parsel_sel=sel("<div><div>DUP</div></div>"), xpath="//div")
    assert out.count("DUP") == 1


def test_deep_dom_does_not_crash():
    out = get_xpath_text(parsel_sel=sel(deep_nested_html(1500)), xpath="//body")
    assert "DEEP_LEAF" in out


def test_pre_code_preserves_indentation():
    out = get_xpath_text(parsel_sel=sel(load_fixture("whitespace.html")), xpath="//code")
    assert "\n    if n < 2" in out


def test_noscript_excluded():
    out = get_xpath_text(parsel_sel=sel(load_fixture("news.html")), xpath="//article")
    assert "NOSCRIPT_MARKER" not in out

"""Bug ledger: xfail(strict) tests asserting the DESIRED behaviour.

These fail today (documenting known bugs) and are collected as ``xfail``.
``xfail_strict = true`` (pyproject) means that once a refactor fixes the bug the
test XPASSes and *fails the suite* -- the signal to delete the xfail mark and
promote it to a normal passing test.
"""

import pytest

from conftest import README_HTML, mojibake, sel, soup

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

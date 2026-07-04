"""Unit tests for internal helpers and the ParselGetSelectorInText class."""

from conftest import mojibake, sel, soup

from parsel_text import ParselGetSelectorInText, remove_trailing_chars


# --------------------------------------------------------------------------- #
# remove_trailing_chars
#
# NB: despite its name/docstring ("trailing whitespace"), this helper collapses
# *all* runs of whitespace (spaces, tabs, newlines, NBSP) into single spaces and
# strips both ends. These tests pin that real behaviour.
# --------------------------------------------------------------------------- #
class TestRemoveTrailingChars:
    def test_collapses_internal_spaces(self):
        assert remove_trailing_chars("a   b") == "a b"

    def test_strips_both_ends(self):
        assert remove_trailing_chars("  a  ") == "a"

    def test_collapses_tabs_and_newlines(self):
        assert remove_trailing_chars("a\tb\nc") == "a b c"

    def test_collapses_nbsp(self):
        assert remove_trailing_chars("a  b") == "a b"

    def test_empty_string(self):
        assert remove_trailing_chars("") == ""

    def test_whitespace_only(self):
        assert remove_trailing_chars("   \t\n  ") == ""

    def test_single_word_unchanged(self):
        assert remove_trailing_chars("word") == "word"

    def test_mixed_whitespace(self):
        assert remove_trailing_chars("  a   b\tc\nd  ") == "a b c d"


# --------------------------------------------------------------------------- #
# ParselGetSelectorInText -- the stateful worker behind the public functions.
# --------------------------------------------------------------------------- #
class TestParselGetSelectorInText:
    @staticmethod
    def _fresh(fix_mojibake: bool = False) -> ParselGetSelectorInText:
        obj = ParselGetSelectorInText(fix_mojibake=fix_mojibake)
        obj.total_text = ""
        return obj

    def test_traverse_soup_order_and_newlines(self):
        obj = self._fresh()
        obj.traverse_soup(root=soup("<div>A<span>B</span>C</div>"))
        assert obj.total_text == "A\nB\nC\n"

    def test_traverse_soup_fix_mojibake_true(self):
        obj = self._fresh(fix_mojibake=True)
        obj.traverse_soup(root=soup("<div>" + mojibake("café") + "</div>"))
        assert obj.total_text == "café\n"

    def test_traverse_soup_fix_mojibake_false(self):
        obj = self._fresh(fix_mojibake=False)
        obj.traverse_soup(root=soup("<div>" + mojibake("café") + "</div>"))
        assert obj.total_text == mojibake("café") + "\n"

    def test_get_sel_results_accumulates(self):
        obj = self._fresh()
        results = sel("<div><p>One</p><p>Two</p></div>").xpath("//p")
        obj.get_sel_results(sel_results=results)
        assert obj.total_text == "One\nTwo\n"

    def test_get_xpath_results_resets_between_calls(self):
        obj = ParselGetSelectorInText(fix_mojibake=False)
        first = obj.get_xpath_results(parsel_sel=sel("<p>One</p>"), xpath="//p")
        second = obj.get_xpath_results(parsel_sel=sel("<p>Two</p>"), xpath="//p")
        assert first == "One\n"
        # Not "One\nTwo\n": get_xpath_results resets total_text on entry.
        assert second == "Two\n"

    def test_get_xpath_row_results(self):
        obj = ParselGetSelectorInText(fix_mojibake=False)
        rows = obj.get_xpath_row_results(
            parsel_sel=sel("<ul><li>Uno   dos</li><li>Tres</li><li>  </li></ul>"),
            xpath="//li",
        )
        assert rows == ["Uno dos\n", "Tres\n", ""]

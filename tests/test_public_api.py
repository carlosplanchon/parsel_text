"""Characterisation tests for the public API.

Every assertion here pins the *current* observed behaviour -- including the
trailing "\\n" produced by the no-op rstrip. Together they form the safety net
for the upcoming refactor (dropping bs4, using parsel directly). Desired-but-not-
yet-true behaviour lives in test_known_bugs.py.
"""

from conftest import NBSP, README_HTML, mojibake, sel, soup

from parsel_text import (
    get_bs4_soup_text,
    get_results_row_text,
    get_xpath_text,
)


class TestGetXpathText:
    def test_readme_example(self):
        result = get_xpath_text(
            parsel_sel=sel(README_HTML),
            xpath="//div[@id='content']/p//text()",
        )
        assert result == "Hello, world!\nWelcome to the parsel_text library.\n"

    def test_trailing_newline_present(self):
        # Pinned CURRENT behaviour: output ends with a stray newline.
        # See test_known_bugs.py for the desired (stripped) state.
        result = get_xpath_text(parsel_sel=sel(README_HTML), xpath="//p")
        assert result.endswith("\n")

    def test_empty_match_returns_empty_string(self):
        assert get_xpath_text(parsel_sel=sel(README_HTML), xpath="//nonexistent") == ""

    def test_document_order_preserved(self):
        result = get_xpath_text(
            parsel_sel=sel("<div>A<span>B</span>C<p>D</p></div>"), xpath="//div"
        )
        assert result == "A\nB\nC\nD\n"

    def test_deeply_nested_order(self):
        result = get_xpath_text(
            parsel_sel=sel("<body>A<div>B<span>C</span>D</div>E</body>"),
            xpath="//body",
        )
        assert result == "A\nB\nC\nD\nE\n"

    def test_multiple_matches_concatenated(self):
        result = get_xpath_text(
            parsel_sel=sel("<div><p>One</p><p>Two</p></div>"), xpath="//p"
        )
        assert result == "One\nTwo\n"

    def test_element_xpath_equals_text_xpath(self):
        s = sel("<div><p>One</p><p>Two</p></div>")
        assert get_xpath_text(parsel_sel=s, xpath="//p") == get_xpath_text(
            parsel_sel=s, xpath="//p//text()"
        )

    # -- mojibake ----------------------------------------------------------- #
    def test_mojibake_fixed_by_default(self):
        s = sel("<p>" + mojibake("café") + "</p>")
        assert get_xpath_text(parsel_sel=s, xpath="//p") == "café\n"

    def test_mojibake_fix_true(self):
        s = sel("<p>" + mojibake("café") + "</p>")
        assert get_xpath_text(parsel_sel=s, xpath="//p", fix_mojibake=True) == "café\n"

    def test_mojibake_fix_false_preserves_raw(self):
        s = sel("<p>" + mojibake("café") + "</p>")
        assert (
            get_xpath_text(parsel_sel=s, xpath="//p", fix_mojibake=False)
            == mojibake("café") + "\n"
        )

    # -- entities & whitespace --------------------------------------------- #
    def test_entity_amp(self):
        assert (
            get_xpath_text(parsel_sel=sel("<body>Tom &amp; Jerry</body>"), xpath="//body")
            == "Tom & Jerry\n"
        )

    def test_entity_lt_gt(self):
        assert (
            get_xpath_text(parsel_sel=sel("<body>1 &lt; 2 &gt; 0</body>"), xpath="//body")
            == "1 < 2 > 0\n"
        )

    def test_nbsp_entity_collapsed(self):
        assert (
            get_xpath_text(parsel_sel=sel("<body>a&nbsp;&nbsp;b</body>"), xpath="//body")
            == "a b\n"
        )

    def test_nbsp_raw_collapsed(self):
        assert (
            get_xpath_text(
                parsel_sel=sel("<body>a" + NBSP + NBSP + "b</body>"), xpath="//body"
            )
            == "a b\n"
        )

    def test_internal_whitespace_collapsed(self):
        assert (
            get_xpath_text(
                parsel_sel=sel("<p>the   parsel_text   library</p>"), xpath="//p"
            )
            == "the parsel_text library\n"
        )

    # -- exclusions (key behaviours a naive refactor would silently break) -- #
    def test_html_comment_excluded(self):
        assert (
            get_xpath_text(
                parsel_sel=sel("<body>Before<!-- SECRET COMMENT -->After</body>"),
                xpath="//body",
            )
            == "Before\nAfter\n"
        )

    def test_script_content_excluded(self):
        assert (
            get_xpath_text(
                parsel_sel=sel("<body>Text<script>var x = 42;</script>More</body>"),
                xpath="//body",
            )
            == "Text\nMore\n"
        )

    def test_style_content_excluded(self):
        assert (
            get_xpath_text(
                parsel_sel=sel("<body>Text<style>.a{color:red}</style>More</body>"),
                xpath="//body",
            )
            == "Text\nMore\n"
        )

    # -- misc --------------------------------------------------------------- #
    def test_attribute_selection(self):
        html = '<a href="http://x.com">link</a>'
        assert get_xpath_text(parsel_sel=sel(html), xpath="//a/@href") == "http://x.com\n"

    def test_emoji_preserved(self):
        assert (
            get_xpath_text(parsel_sel=sel("<body>hi \U0001f600 end</body>"), xpath="//body")
            == "hi \U0001f600 end\n"
        )

    def test_malformed_html_tolerated(self):
        # lxml is lenient: the unclosed <p> is auto-closed, no crash.
        result = get_xpath_text(parsel_sel=sel("<div><p>Hi</div>"), xpath="//div")
        assert result == "Hi\n"


class TestGetResultsRowText:
    def test_multiple_rows(self):
        rows = get_results_row_text(
            parsel_sel=sel("<ul><li>Uno   dos</li><li>Tres</li></ul>"), xpath="//li"
        )
        assert rows == ["Uno dos\n", "Tres\n"]

    def test_whitespace_only_row_is_empty_string(self):
        rows = get_results_row_text(
            parsel_sel=sel("<ul><li>  </li><li>x</li></ul>"), xpath="//li"
        )
        assert rows == ["", "x\n"]

    def test_empty_match_returns_empty_list(self):
        assert get_results_row_text(parsel_sel=sel("<p>no lists</p>"), xpath="//li") == []

    def test_order_preserved(self):
        rows = get_results_row_text(
            parsel_sel=sel("<ul><li>1</li><li>2</li><li>3</li></ul>"), xpath="//li"
        )
        assert rows == ["1\n", "2\n", "3\n"]

    def test_row_with_nested_elements(self):
        rows = get_results_row_text(
            parsel_sel=sel("<ul><li>A<span>B</span></li></ul>"), xpath="//li"
        )
        assert rows == ["A\nB\n"]

    def test_mojibake_fixed_by_default(self):
        rows = get_results_row_text(
            parsel_sel=sel("<ul><li>" + mojibake("café") + "</li></ul>"), xpath="//li"
        )
        assert rows == ["café\n"]

    def test_mojibake_fix_false(self):
        rows = get_results_row_text(
            parsel_sel=sel("<ul><li>" + mojibake("café") + "</li></ul>"),
            xpath="//li",
            fix_mojibake=False,
        )
        assert rows == [mojibake("café") + "\n"]


class TestGetBs4SoupText:
    def test_extracts_text_with_order(self):
        assert (
            get_bs4_soup_text(bs4_soup=soup("<div>A<span>B</span>C</div>")) == "A\nB\nC\n"
        )

    def test_always_fixes_mojibake(self):
        # Pinned CURRENT behaviour: mojibake is fixed unconditionally (no flag).
        # Desired configurability tracked in test_known_bugs.py.
        result = get_bs4_soup_text(bs4_soup=soup("<div>" + mojibake("café") + "</div>"))
        assert result == "café\n"

    def test_comment_excluded(self):
        assert (
            get_bs4_soup_text(bs4_soup=soup("<div>Before<!-- c -->After</div>"))
            == "Before\nAfter\n"
        )

    def test_script_excluded(self):
        assert (
            get_bs4_soup_text(
                bs4_soup=soup("<div>Text<script>var x = 1;</script>More</div>")
            )
            == "Text\nMore\n"
        )

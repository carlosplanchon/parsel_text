#!/usr/bin/env python3

"""parsel_text: extract text from XPath queries on parsel Selectors.

The extractor walks lxml text nodes natively (no BeautifulSoup): it fixes
mojibake with ftfy, drops <script>/<style>/<noscript>/comment text, preserves
whitespace inside <pre>/<textarea>, and never duplicates text when an XPath
matches nested elements.
"""

from __future__ import annotations

import ftfy

from parsel import Selector, SelectorList


# Tags whose text content is not real page content and is dropped. <template> and
# <noscript> hold inert markup; <script>/<style> hold code.
_EXCLUDE_TAGS = frozenset({"script", "style", "noscript", "template"})

# Tags where whitespace is significant and must be preserved verbatim.
_PREFORMATTED_TAGS = frozenset({"pre", "textarea"})


def _collapse_whitespace(text: str) -> str:
    """Collapse every run of whitespace into a single space and strip the ends."""
    return " ".join(text.split())


def _ancestor_tags(text_node) -> set:
    """Return the tag names of an lxml text node's ancestors.

    lxml exposes two kinds of text node: an element's ``.text`` (``is_tail`` is
    False -- it lives *inside* the element) and its ``.tail`` (``is_tail`` is True
    -- the text that *follows* the element, which really belongs to the element's
    parent). For a tail node we therefore start one level up; otherwise text that
    merely follows a <script>/<noscript> would be wrongly dropped.
    """
    parent = text_node.getparent()
    if parent is None:
        return set()
    start = parent.getparent() if getattr(text_node, "is_tail", False) else parent
    tags = set()
    node = start
    while node is not None:
        tag = node.tag
        if isinstance(tag, str):  # skips comments/PIs, whose .tag is a callable
            tags.add(tag)
        node = node.getparent()
    return tags


def _clean_text_node(text_node) -> str:
    """One lxml text node -> its cleaned contribution, or "" if it is dropped."""
    tags = _ancestor_tags(text_node)
    if tags & _EXCLUDE_TAGS:
        return ""
    raw = str(text_node)
    text = raw if (tags & _PREFORMATTED_TAGS) else _collapse_whitespace(raw)
    return text if text.strip() != "" else ""


def _iter_text_parts(element) -> list[str]:
    """All descendant text of an lxml element, in document order, cleaned."""
    parts = []
    for text_node in element.xpath(".//text()"):
        part = _clean_text_node(text_node)
        if part != "":
            parts.append(part)
    return parts


def _outermost(elements: list) -> list:
    """Keep only elements that are not nested inside another element in the list.

    XPath node-sets already de-duplicate individual nodes, but a query like
    ``//div`` returns an ancestor *and* its descendants; extracting each subtree
    would repeat the descendants' text once per level. Keeping only the outermost
    matches (whose subtrees already cover the inner ones) removes the duplication.
    """
    matched = {id(el) for el in elements}
    return [
        el
        for el in elements
        if not any(id(anc) in matched for anc in el.iterancestors())
    ]


def _string_part(root: str) -> str:
    """Clean a string XPath result (a text node or an attribute value)."""
    if getattr(root, "getparent", None) is not None:
        # A smart string (text node / attribute) that knows its parent: honour
        # the exclusion and preformatted rules just like an element's text.
        return _clean_text_node(root)
    return _collapse_whitespace(root)


def _extract(sel_results: SelectorList) -> list[str]:
    """Text parts for a whole SelectorList, in document order, de-duplicated."""
    elements = [s.root for s in sel_results if not isinstance(s.root, str)]
    keep = {id(el) for el in _outermost(elements)}

    parts: list[str] = []
    for s in sel_results:
        root = s.root
        if isinstance(root, str):
            part = _string_part(root)
            if part != "":
                parts.append(part)
        elif id(root) in keep:
            parts.extend(_iter_text_parts(root))
    return parts


def get_xpath_text(
    parsel_sel: Selector,
    xpath: str,
    fix_mojibake: bool = True,
) -> str:
    """Extract all text matched by *xpath* on *parsel_sel* as a single string.

    Text nodes are joined with newlines, in document order. When *fix_mojibake*
    is True (default) the result is run through ``ftfy.fix_text``.
    """
    text = "\n".join(_extract(parsel_sel.xpath(xpath)))
    return ftfy.fix_text(text) if fix_mojibake else text


def get_results_row_text(
    parsel_sel: Selector,
    xpath: str,
    fix_mojibake: bool = True,
) -> list[str]:
    """Like :func:`get_xpath_text` but one string per matched node.

    Each match keeps its own full subtree (no cross-match de-duplication): N
    matches produce N rows, in document order.
    """
    rows: list[str] = []
    for s in parsel_sel.xpath(xpath):
        root = s.root
        if isinstance(root, str):
            part = _string_part(root)
            parts = [part] if part != "" else []
        else:
            parts = _iter_text_parts(root)
        text = "\n".join(parts)
        rows.append(ftfy.fix_text(text) if fix_mojibake else text)
    return rows


def get_bs4_soup_text(bs4_soup, fix_mojibake: bool = True) -> str:
    """Extract text from a BeautifulSoup object.

    Kept for backwards compatibility. The library no longer depends on
    BeautifulSoup: the soup is re-serialised and run through the native
    extractor, so the caller just needs a value whose ``str()`` is HTML.
    """
    root = Selector(text=str(bs4_soup)).root
    text = "\n".join(_iter_text_parts(root))
    return ftfy.fix_text(text) if fix_mojibake else text


def remove_trailing_chars(text: str) -> str:
    """Collapse all runs of whitespace into single spaces and strip the ends.

    Kept for backwards compatibility. Despite the historical name, this collapses
    *all* internal whitespace, not only trailing whitespace.
    """
    return _collapse_whitespace(text)

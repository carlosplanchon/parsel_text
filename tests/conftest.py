"""Shared helpers and constants for the parsel_text test-suite."""

import bs4

from parsel import Selector


# Non-breaking space (U+00A0). Python's str.split() treats it as whitespace, so
# parsel_text collapses it away like any ordinary space.
NBSP = " "

# The exact document used in the README example.
README_HTML = (
    "<html><body><div id='content'>"
    "<p>Hello, world!</p>"
    "<p>Welcome to the parsel_text library.</p>"
    "</div></body></html>"
)


def sel(html: str) -> Selector:
    """Build a parsel Selector from an HTML string."""
    return Selector(text=html)


def soup(html: str) -> bs4.BeautifulSoup:
    """Build a BeautifulSoup (lxml) object from an HTML string."""
    return bs4.BeautifulSoup(html, features="lxml")


def mojibake(text: str) -> str:
    """Return a deterministic mojibake version of *text*.

    Simulates UTF-8 bytes wrongly decoded as latin-1, e.g.
    ``"café" -> "cafÃ©"`` -- exactly what ftfy.fix_text is meant to undo.
    """
    return text.encode("utf-8").decode("latin-1")

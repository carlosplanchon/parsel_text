# parsel_text

`parsel_text` is a Python library designed to simplify the extraction of text data from HTML or XML documents using XPath queries on `parsel` Selector objects. It provides a straightforward interface to obtain and optionally fix mojibake (garbled text due to encoding issues).

## Installation

To install `parsel_text`, use pip:

```bash
pip install parsel_text
```

## Usage

### Function: `parsel_sel_get_text`

This is the main function of the library, designed to extract all text results from an XPath query on a `parsel` Selector object.

#### Parameters

- `parsel_sel` (`parsel.Selector`): The `parsel` Selector object from which to extract text.
- `xpath` (`str`): The XPath query string to specify the text extraction path.
- `fix_mojibake` (`bool`, optional): A flag to indicate whether to fix mojibake issues in the extracted text. Default is `True`.

#### Returns

- `str`: A string containing the concatenated text results from the specified XPath query.

### Example

Here's a simple example of how to use the `parsel_sel_get_text` function:

```python
from parsel import Selector
from parsel_text import parsel_sel_get_text

html_content = """
<html>
  <body>
    <div id="content">
      <p>Hello, world!</p>
      <p>Welcome to the parsel_text library.</p>
    </div>
  </body>
</html>
"""

# Create a parsel Selector object
selector = Selector(text=html_content)

# Define the XPath query
xpath_query = "//div[@id='content']/p//text()"

# Extract text using the parsel_sel_get_text function
extracted_text = parsel_sel_get_text(parsel_sel=selector, xpath=xpath_query)

print(extracted_text)
```

#### Output

```
Hello, world!
Welcome to the parsel_text library.
```

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

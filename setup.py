#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="parsel_get_selector_text",
    packages=find_packages(),
    version="0.5",
    license="MIT",
    description="Extracts all text results from an XPath "\
        "query on a parsel Selector object.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Carlos A. Planchón",
    author_email="carlosandresplanchonprestes@gmail.com",
    url="https://github.com/carlosplanchon/parsel_get_selector_text",
    keywords=["dom", "parsel", "scraping", "xpath"],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        "ftfy",
        "parsel",
        "beautifulsoup4"
    ]
)

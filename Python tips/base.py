#!/usr/bin/env python3

import argparse
import html
import logging


def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description="Arguments get parsed via --commands")
    parser.add_argument(
        "-v",
        metavar="verbosity",
        type=int,
        default=4,
        help="Verbosity of logging: 0 -critical, 1- error, 2 -warning, 3 -info, 4 -debug",
    )

    args = parser.parse_args()
    verbose = {0: logging.CRITICAL, 1: logging.ERROR, 2: logging.WARNING, 3: logging.INFO, 4: logging.DEBUG}
    logging.basicConfig(format="%(message)s", level=verbose[args.v], filename="output/errors.log")
    return args


def unescape_html(text: str) -> str:
    """Converts any HTML entities found in text to their textual representation.

    Args:
        text (str): utterance that may contain HTML entities.

    Examples:

        Example of HTML entities found during annotations::

        >>> unescape_html("&nbsp;")
        ""
        >>> unescape_html("&amp;")
        "&"
        >>> unescape_html("&gt;")
        ">"
        >>> unescape_html("&lt;")
        "<"
        >>> unescape_html("&le;")
        "≤"
        >>> unescape_html("&ge;")
        "≥"


    Returns:
        str: utterance without HTML entities.

    """
    return html.unescape(text)

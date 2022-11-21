#!/usr/bin/env python3

import argparse
import html
import logging
from typing import List

import pandas as pd


def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description='Arguments get parsed via --commands')
    parser.add_argument(
        '-v',
        metavar='verbosity',
        type=int,
        default=4,
        help='Verbosity of logging: 0 -critical, 1- error, 2 -warning, 3 -info, 4 -debug',
    )

    args = parser.parse_args()
    verbose = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    logging.basicConfig(format='%(message)s', level=verbose[args.v], filename='output/errors.log')
    return args


def print_df(df: pd.DataFrame, rows: int, exit_script: bool = False) -> None:
    """Prints a DataFrame.

    Args:
        df (pandas.core.frame.DataFrame): tabular view to print.
        rows (int): the number of rows to print.
        exit_script (bool): whether to exit the script.
    """
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df.head(rows))
        if exit_script:
            exit()


def unescape_html(text: str) -> str:
    """Converts any HTML entities found in text to their textual representation.

    Args:
        text (str): utterance that may contain HTML entities.

    Examples:
        >>>
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


def equal_array_items(x: List) -> bool:
    """Compares whether all array items are of the same type and content.

    Args:
        x (typing.List): an array to compare list items in.

    Examples:
        >>>
        >>> equal_array_items(["1", "1"])
        True
        >>> equal_array_items(["1", "2"])
        False

    Returns:
        bool: True if all items in this list are equal, False otherwise.

    """
    if len(x) == 2:
        return x[0] == x[1]
    else:
        return x[0] == x[1] and equal_array_items(x[1:])

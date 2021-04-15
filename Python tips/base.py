#!/usr/bin/env python3

import os
import sys
import argparse
import logging
from logging import debug, info, warning, error, critical
import json


def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description='Arguments get parsed via --commands')
    parser.add_argument('-v', metavar='verbosity', type=int, default=4,
        help='Verbosity of logging: 0 -critical, 1- error, 2 -warning, 3 -info, 4 -debug')

    args = parser.parse_args()
    verbose = {0: logging.CRITICAL, 1: logging.ERROR, 2: logging.WARNING, 3: logging.INFO, 4: logging.DEBUG}
    logging.basicConfig(format='%(message)s', level=verbose[args.v], filename='output/errors.log')
    return args


def print_df(df, rows, exit_script=False):
    """Prints Pandas DataFrame."""
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df.head(rows))
        if exit_script:
            exit()


def unescape_html(
        text: str) -> str:
    """Converts any HTML entities found in text to their textual representation.
    :param text: utterance that may contain HTML entities
    :type text: str
    Example of HTML entities found during annotations
        html_entities = [("&nbsp;", " ")
            , ("&amp;", "&")
            , ("&gt;", ">")
            , ("&lt;", "<")
            , ("&le;", "≤")
            , ("&ge;", "≥")]
    :return: utterance wihtout HTML entities
    :rtype: str
    """
    return html.unescape(text)


def equal_array_items(
        x: List) -> bool:
    """Compares whether all array items are of the same type and content.
    Example:
        lst = [{'end': 20, 'labels': ['NORP'], 'start': 13, 'text': 'english'}
        , {'end': 20, 'labels': ['NORP'], 'start': 13, 'text': 'english'}]
        equal_array_items(lst)
        >>> True
        lst = [{'end': 20, 'labels': ['NORP'], 'start': 13, 'text': 'english'}
        , {'end': 20, 'labels': ['LOCATION'], 'start': 13, 'text': 'english'}]
        equal_array_items(lst)
        >>> False
    :param x: array to compare list items in
    :type x: list
    :return: whether all items in this list are equal
    :rtype: bool
    """
    if len(x) == 2:
        return x[0] == x[1]
    else:
        return x[0] == x[1] and equal_array_items(x[1:])

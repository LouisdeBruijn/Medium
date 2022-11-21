#!/usr/bin/env python3
# File name: format.py
# Description: Basic format for Python scripts
# Author: Louis de Bruijn
# Date: 19-05-2020

import argparse
import logging
import sys
from logging import error, info


def parse_arguments():
    """Read arguments from a command line."""
    parser = argparse.ArgumentParser(description="Arguments get parsed via --commands")
    parser.add_argument(
        "-v",
        metavar="verbosity",
        type=int,
        default=2,
        help="Verbosity of logging: 0 -critical, 1- error, 2 -warning, 3 -info, 4 -debug",
    )

    args = parser.parse_args()
    verbose = {0: logging.CRITICAL, 1: logging.ERROR, 2: logging.WARNING, 3: logging.INFO, 4: logging.DEBUG}
    logging.basicConfig(format="%(message)s", level=verbose[args.v], stream=sys.stdout)

    return args


def modular_sphinx_function():
    """< Summary. >.

    :param <variable_name>: <variable_description>, defaults to <default_value>
    :type <variable_name>: <variable_type>(, optional)
    <other parameters and types>
    :raises <error_type>: <error_description>
    <other exceptions>
    :rtype: <return_type>
    :return: <return_description>
    """
    return "This modular function with examplary Sphinx docstring conventions."


def modular_google_function(arg1: int) -> int:
    """< Summary. >.

    Args:
        arg1 (int): <description>

    Examples:
        >>>
        >>> modular_google_function(1)
        2

    Returns:
        The sum of the first argument

    """
    return arg1 + arg1


def main():
    """Execute when running this script."""
    info("Running the main program.")

    print(modular_sphinx_function)

    print(modular_google_function(1))

    try:
        "string" + 10
    except Exception as e:
        error(str(e))


if __name__ == "__main__":
    args = parse_arguments()
    main()

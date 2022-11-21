#!/usr/bin/env python3
# File name: auto_waterfall.py
# Description: Automatic waterfall logging of Pandas and Pyspark DataFrames
# Author: Louis de Bruijn
# Date: 21-11-2022


import logging
import os
import sys
from typing import List

from filtering import filter_bedrooms, filter_house_age_range, filter_household_members, join_new_house_data
from sklearn import datasets
from waterfall import LogWaterfall


class LogVariables(object):
    """Decorator for automatic waterfall logging of variables in Markdown file."""

    def __init__(self, vars_to_log: List, log: LogWaterfall):
        """Initialisation.

        Args:
            vars_to_log (list): array of variables names to log waterfall
            log (LogWaterfall): waterfall logging object
        """
        self.vars_to_log = vars_to_log
        self.log = log

    def __call__(self, func):
        """Call of the decorator function."""

        def wrapped_func(*args, **kwargs):
            """Calls actual function that the decorator accompanies."""
            with LogDebugContext(func.__name__, self.vars_to_log, self.log):
                return_value = func(*args, **kwargs)
            return return_value

        return wrapped_func


class LogDebugContext:
    """Debug context to trace any function calls inside the context."""

    def __init__(self, name: str, vars_to_log: List, log: LogWaterfall):
        """Initialisation.

        Args:
            name (str): name of the function that is to de debugged
            vars_to_log (List): array of variables names to log waterfall
            log (LogWaterfall): waterfall logging object
        """
        self.name = name
        self.vars_to_log = vars_to_log
        self.log = log
        self.previous_df = None

    def __enter__(self):
        """Enter the trace."""
        sys.settrace(self.trace_calls)

    def __exit__(self, *args, **kwargs):
        """Exit the trace."""
        sys.settrace = None

    def trace_calls(self, frame, event):
        """Trace calls.

        Args:
            frame (): a tracing frame
            event (): a tracing event

        Returns:
            traced_lines (): traced lines
        """
        if event != "call":
            # we want to only trace our call to the decorated function
            return
        elif frame.f_code.co_name != self.name:
            # return the trace function to use when you go into that function call
            return

        self.log.init_md(md_title="Waterfall California housing dataset")  # initializes table markdown file

        traced_lines = self.trace_lines

        logging.info(f"Logged variables {self.vars_to_log}.")

        return traced_lines

    def trace_lines(self, frame, event):
        """Trace lines.

        Args:
            frame (): a tracing frame
            event (): a tracing event

        Returns:
            None
        """
        if event not in ["line", "return"]:
            return

        local_vars = frame.f_locals

        for var_name, var_value in local_vars.items():
            if var_name in self.vars_to_log:

                df = local_vars[var_name]
                if df is not self.previous_df:

                    self.log.line(df, reason="filtering step", conf_flag="n/a")
                    self.previous_df = df

        self.log.create_md()


auto_generate_log = LogWaterfall(
    dir_path=f"{os.getcwd()}/tmd/",
    tb_name="california_housing",
    identifier=None,
    tmd_section="1_data_source",
    file_name="auto_waterfall",
    append=False,
)


@LogVariables(vars_to_log=["california_housing_df"], log=auto_generate_log)
def main():
    """Main function."""
    california_housing = datasets.fetch_california_housing(as_frame=True)
    california_housing_df = california_housing.frame

    settings = {
        "min_bedrooms": 1.0,
        "max_occupants": 2.0,
        "house_age": [10, 80],
        "join_new_houses": True,
    }

    california_housing_df = filter_bedrooms(california_housing_df, settings)

    california_housing_df = filter_household_members(california_housing_df, settings)

    california_housing_df = filter_house_age_range(california_housing_df, settings)

    if settings["join_new_houses"]:
        california_housing_df = join_new_house_data(california_housing_df, california_housing.frame)


if __name__ == "__main__":
    main()

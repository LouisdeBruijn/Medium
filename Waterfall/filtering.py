#!/usr/bin/env python3
# File name: filtering.py
# Description: Filtering functions for showcasing of Waterfall logging scripts
# Author: Louis de Bruijn
# Date: 21-11-2022

import pandas as pd


def filter_bedrooms(df, settings):
    """Filters houses with at least one bedroom in the block."""
    return df.loc[lambda row: row["AveBedrms"] >= settings["min_bedrooms"]]


def filter_household_members(df, settings):
    """Filters houses for one or two household members."""
    return df.loc[lambda row: row["AveOccup"] <= settings["max_occupants"]]


def filter_house_age_range(df, settings):
    """Filters houses aged between two ages."""
    return df.loc[
        lambda row: (row["HouseAge"] >= settings["house_age"][0]) & (row["HouseAge"] <= settings["house_age"][1])
    ]


def join_new_house_data(df1, df2):
    """Appends houses with an average number of bedrooms in the block between 0.5 and 1.0."""
    return pd.concat(
        [df1, df2.loc[lambda row: (row["AveBedrms"] >= 0.5) & (row["AveBedrms"] <= 1.0)]],
        join="outer",
        ignore_index=True,
    )

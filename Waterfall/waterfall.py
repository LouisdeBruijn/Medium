#!/usr/bin/env python3
# File name: waterfall.py
# Description: Waterfall logging of Pandas and Pyspark DataFrames
# Author: Louis de Bruijn
# Date: 21-11-2022

import logging
import os
from typing import Any, Dict, Optional, Union

import pandas as pd
import plotly.graph_objects as go
from filtering import filter_bedrooms, filter_house_age_range, filter_household_members, join_new_house_data
from mdutils.mdutils import MdUtils
from pyspark.sql import DataFrame as sparkDataFrame
from sklearn import datasets

# pandas==1.2.4
# pyspark==3.3.1
# mdutils==1.3.1
# scikit-learn==1.0.2
# plotly==5.11.0
# kaleido==0.2.1

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        # logging.FileHandler("waterfall.log"),
        logging.StreamHandler()
    ],
)


class LogWaterfall:
    """Logs a table on each filtering steps in waterfall fashion in a Markdown file."""

    def __init__(
        self, dir_path: str, tb_name: str, identifier: Optional[str], tmd_section: str, file_name: str, append: bool
    ):
        """Initialisation.

        Args:
            dir_path (str): path to directory where Markdown files are saved
            tb_name (str): name of the table to log
            identifier (str): column name with unique entities
            tmd_section (str): TMD document section name
            file_name (str): name of the Markdown file
            append (bool): whether to append to an existing Markdown file
        """
        self.dir_path = dir_path
        self.tb_name = tb_name
        self.identifier = identifier if identifier else None
        self.previous_entries: Dict = dict()
        self.previous_unique_cust: Dict = dict()
        self.file_path = os.path.join(self.dir_path, f'{tmd_section}_{file_name}.md')
        self.mdFile = MdUtils(self.file_path)
        self.append = append

    def init_or_append_md(self, df: Union[pd.DataFrame, sparkDataFrame]):
        """Initializes a new Markdown file or appends to existing file.

        Args:
            df (spark.DataFrame, pd.DataFrame): DataFrame that the filtering is applied to

        Returns:
            None
        """
        logging.info('Waterfall logging enabled.')
        if self.append and os.path.exists(self.file_path):
            self.set_previous_values()
            logging.info('Appending to existing Waterfall Markdown file.')
        else:
            self.init_md(md_title='Waterfall California housing dataset')
            self.line(df=df, reason='Raw California housing data', conf_flag='n/a')
            logging.info('Creating new markdown file.')

    def init_md(self, md_title: str):
        """Creates the header of a new Markdown file.

        Args:
            md_title (str): title of the Markdown file

        Returns:
            None
        """
        self.mdFile.new_line(text=md_title, bold_italics_code='i')
        self.mdFile.new_line(text='')
        self.mdFile.new_line(
            text='| Table | # entries | # entries change | # unique entities | # unique entities change | Reason'
            ' | Configurations flag |',
            wrap_width=125,
        )
        self.mdFile.new_line(
            text='| :---- | :-------- | :--------------- | :---------------- | :----------------------- '
            '| :----- | :------------------ |',
            wrap_width=125,
        )

    def set_previous_values(self):
        """Read existing Markdown file and sets column values for self.previous_entries and self.previous_unique_cust.

        Returns:
            None
        """
        self.mdFile.read_md_file(file_name=self.file_path)

        with open(self.file_path, 'r') as md_file:
            for line in md_file.read().splitlines():
                if line.startswith('| `'):
                    columns = [
                        col.strip() for col in line.split('|') if col
                    ]  # split by delimiter and strip whitespaces
                    tb_name, previous_entries, previous_unique_cust = columns[0].strip('`'), columns[1], columns[3]
                    self.previous_entries[tb_name] = int(previous_entries)  # replace previous_entries value
                    self.previous_unique_cust[tb_name] = int(previous_unique_cust)  # replace previous_entries value

    def line(
        self,
        df: Union[pd.DataFrame, sparkDataFrame],
        reason: str = 'filtering step',
        conf_flag: Any = 'n/a',
        tb_name: str = None,
    ):
        """Adds a line with the table filtering action for the Markdown file.

        Args:
            df (spark.DataFrame, pd.DataFrame): DataFrame that the filtering is applied to
            reason (str): The reason for this specific DataFrame filtering
            conf_flag (str): which configuration flag is used from .yaml files
            tb_name (str): the table name that this action is to

        Returns:
            None
        """
        tb_name = self.tb_name if not tb_name else tb_name

        if not self.previous_entries.get(tb_name) or not self.previous_unique_cust.get(tb_name):
            self.previous_entries[tb_name], self.previous_unique_cust[tb_name] = 'n/a', 'n/a'

        if isinstance(df, pd.DataFrame):
            current_entries, current_unique_cust = df.shape[0], df.shape[0]
            if self.identifier:
                current_unique_cust = df[self.identifier].nunique()

        elif isinstance(df, sparkDataFrame):
            current_entries, current_unique_cust = df.count(), df.count()
            if self.identifier:
                current_unique_cust = df.select(self.identifier).distinct().count()
        else:
            raise ValueError('Either pd.DataFrame or spark.DataFrame should be provided as `df`.')

        if self.previous_entries[tb_name] == 'n/a' or self.previous_unique_cust[tb_name] == 'n/a':
            columns = (
                f'`{tb_name}`',
                current_entries,
                self.previous_entries[tb_name],
                current_unique_cust,
                self.previous_unique_cust[tb_name],
                reason,
                conf_flag,
            )
        else:
            columns = (
                f'`{tb_name}`',
                current_entries,
                current_entries - self.previous_entries[tb_name],
                current_unique_cust,
                current_unique_cust - self.previous_unique_cust[tb_name],
                reason,
                conf_flag,
            )

        self.previous_entries[tb_name] = current_entries
        self.previous_unique_cust[tb_name] = current_unique_cust

        md_line = f"| {' | '.join((str(col) for col in columns))} |"
        self.mdFile.new_line(text=md_line, wrap_width=len(md_line))

    def create_md(self):
        """Creates the Markdown file.

        Returns:
            None
        """
        self.mdFile.create_md_file()


def plot_waterfall_markdowns(path_table: str, path_image: str, file_name: str, tmd_section: str):
    """Reads all Markdown waterfall tables in TMD and generates plots for all.

    Args:
        path_table (str): location to save tables
        path_image (str): location to save images
        file_name (str): name of the markdown files
        tmd_section (str): tmd section name

    Returns:
        None
    """
    waterfall_md_files = [f for f in os.listdir(path_table) if f.startswith(f'{tmd_section}_{file_name}')]

    for fn in waterfall_md_files:

        filter_steps = []

        with open(f'{path_table}{fn}', 'r') as md_file:
            for line in md_file:
                line = line.rstrip('\n')
                if line.startswith('*'):
                    md_title = line.strip().strip('*')
                if line.startswith('| `'):
                    text = line[2:].split(' |')[:-1]
                    text = [el.strip() for el in text]
                    filter_steps.append(text)

        filtering_steps = [step[1:] for step in filter_steps]  # remove first column
        header = (
            '| Table | # entries | # entries removed | # unique entities |'
            + ' # unique entities removed | Reason | Configurations flag'
        )
        columns = header.split(' | ')[1:]  # remove first column
        int_cols = [i for i in columns if i.startswith('#')]

        waterfall_df = pd.DataFrame(filtering_steps, columns=columns)

        # remove rows where there are no changes in # entries removed or # unique entities removed
        waterfall_df[int_cols] = waterfall_df[int_cols].replace('n/a', '0')

        df_skip_first_row = waterfall_df.iloc[1:, :]
        indices = df_skip_first_row[
            (df_skip_first_row['# entries removed'] == '0') & (df_skip_first_row['# unique entities removed'] == '0')
        ].index

        waterfall_df_img = waterfall_df.drop(indices, inplace=False)

        start_count = waterfall_df_img['# entries'][0]
        end_count = waterfall_df_img['# entries'].to_list()[-1]

        measures = ['absolute'] + ['relative'] * (waterfall_df_img.shape[0] - 1) + ['total']
        texts = [start_count] + [x for x in waterfall_df_img['# entries removed'][1:]] + [end_count]
        texts = [int(x) for x in texts]
        y_axes = [start_count] + texts[1:]
        x_axes = waterfall_df_img['Reason'].to_list() + ['Total']

        fig = go.Figure(
            go.Waterfall(
                name='# of entries',
                orientation='v',
                measure=measures,  # 'relative' or 'total'
                x=x_axes,
                textfont=dict(
                    family='sans-serif',
                    size=11,
                ),
                text=texts,
                y=y_axes,
                connector={'line': {'color': 'rgba(0,0,0,0)'}},
                totals={'marker': {'color': '#ff6600', 'line': {'color': '#ff6600', 'width': 1}}},
            )
        )

        fig.update_layout(
            autosize=True,
            width=1000,
            height=1000,
            title=md_title,
            xaxis=dict(title='Filtering steps'),
            yaxis=dict(title='# of entries'),
            showlegend=False,
            legend=dict(
                x=0.78,
                y=0.91,
                traceorder='normal',
                font=dict(family='sans-serif', size=12, color='grey'),
            ),
            waterfallgroupgap=0.1,
        )

        fig.update_traces(
            textposition='outside',
        )

        fn_without_extension = fn.rstrip('.md')
        image_file_path = os.path.join(path_image, f'{fn_without_extension}.png')
        fig.write_image(image_file_path)


def main():
    """Main function."""
    california_housing = datasets.fetch_california_housing(as_frame=True)
    california_housing_df = california_housing.frame

    settings = {
        'min_bedrooms': 1.0,
        'max_occupants': 2.0,
        'house_age': [10, 80],
        'join_new_houses': True,
    }

    waterfall_log = LogWaterfall(
        dir_path=f'{os.getcwd()}/tmd/',
        tb_name='california_housing',
        identifier=None,
        tmd_section='1_data_source',
        file_name='waterfall',
        append=False,
    )

    waterfall_log.init_or_append_md(california_housing_df)

    california_housing_df = filter_bedrooms(california_housing_df, settings)
    waterfall_log.line(df=california_housing_df, reason='Select in-scope bedrooms', conf_flag=settings['min_bedrooms'])

    california_housing_df = filter_household_members(california_housing_df, settings)
    waterfall_log.line(df=california_housing_df, reason='Maximum two occupants', conf_flag=settings['max_occupants'])

    california_housing_df = filter_house_age_range(california_housing_df, settings)
    waterfall_log.line(df=california_housing_df, reason='House age range', conf_flag=settings['house_age'])

    if settings['join_new_houses']:
        california_housing_df = join_new_house_data(california_housing_df, california_housing.frame)
        waterfall_log.line(
            df=california_housing_df,
            reason='Join houses w/ at least a half bedroom',
            conf_flag=settings['join_new_houses'],
        )

    waterfall_log.create_md()

    plot_waterfall_markdowns(
        path_table=f'{os.getcwd()}/tmd/',
        path_image=f'{os.getcwd()}/images/',
        file_name='waterfall',
        tmd_section='1_data_source',
    )


if __name__ == '__main__':
    main()

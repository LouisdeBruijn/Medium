from collections import defaultdict
from pathlib import Path
from typing import Union


def automate_mkdocs_from_docstring(
    mkdocs_dir: Union[str, Path], mkgendocs_f: str, repo_dir: Union[str, Path], cut_file: bool, match_string: str
):
    """Automates the -pages for mkgendocs package by adding all functions in a directory.

    Args:
        mkdocs_dir (str): textual directory for the hierarchical directory & navigation in Mkdocs
        mkgendocs_f (str): The configurations file for the mkgendocs package
        repo_dir (str): textual directory to search for Python functions in
        cut_file (bool): whether to remove remaining lines in file after the match_string line
        match_string (str): the text to be matches, after which the functions will be added in mkgendocs format

    Example:

        >>>
        >>> automate_mkdocs_from_docstring('scripts', cut_file=True, repo_dir=Path.cwd(), match_string='pages:')

    Returns:
        str: feedback message

    """
    p = repo_dir.glob("**/*.py")
    scripts = [x for x in p if x.is_file()]

    functions = defaultdict(list)
    for script in scripts:
        with open(script, "r") as file:
            lines = file.readlines()

            for line in lines:
                if line.startswith("def ") and "main()" not in line:
                    import re

                    function = re.split("def |\\(", line)[1]
                    functions[script].append(function)

    with open(f"{repo_dir}/{mkgendocs_f}", "r+") as mkgen_config:
        insert_string = ""
        for path, function_names in functions.items():
            insert_string += (
                f'  - page: "{mkdocs_dir}/{path.parent.name}/{path.stem}.md"\n    '
                f'source: "{path.parent.name}/{path.stem}.py"\n    functions:\n'
            )

            f_string = ""
            for f in function_names:
                insert_f_string = f"      - {f}\n"
                f_string += insert_f_string

            insert_string += f_string

        contents = mkgen_config.readlines()
        if match_string in contents[-1]:
            contents.append(insert_string)
        else:
            for index, line in enumerate(contents):
                if match_string in line and insert_string not in contents[index + 1]:
                    contents.insert(index + 1, insert_string)

                    if cut_file:
                        contents = contents[: index + 1]

                    break

        mkgen_config.seek(0)
        mkgen_config.writelines(contents)

        return f"Added to {mkgendocs_f}: {tuple(functions.values())}."


def automate_fake_func(f="fake"):
    """ """
    print(f)


def main():

    python_tips_dir = (
        Path.cwd()
    )  # use `Path.cwd().parent` for all Python files in the repository and not just the 'Python Tips' folder

    automate_mkdocs_from_docstring(
        mkdocs_dir="scripts",
        mkgendocs_f="mkgendocs.yml",
        repo_dir=python_tips_dir,
        cut_file=True,
        match_string="pages:\n",
    )


if __name__ == "__main__":
    main()

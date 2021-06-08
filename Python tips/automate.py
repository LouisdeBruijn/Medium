import re
from collections import defaultdict
from pathlib import Path
from typing import Union, get_type_hints


def automate_mkdocs_from_docstring(
    mkdocs_dir: Union[str, Path], mkgendocs_f: str, repo_dir: Path, match_string: str
) -> str:
    """Automates the -pages for mkgendocs package by adding all Python functions in a directory to the mkgendocs config.

    Args:
        mkdocs_dir (str): textual directory for the hierarchical directory & navigation in Mkdocs
        mkgendocs_f (str): The configurations file for the mkgendocs package
        repo_dir (Path): textual directory to search for Python functions in
        match_string (str): the text to be matches, after which the functions will be added in mkgendocs format

    Example:

        >>>
        >>> automate_mkdocs_from_docstring('scripts', repo_dir=Path.cwd(), match_string='pages:')

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

                    contents = contents[: index + 1]
                    contents.append(insert_string)
                    break

    with open(f"{repo_dir}/{mkgendocs_f}", "w") as mkgen_config:
        mkgen_config.writelines(contents)

    return f"Added to {mkgendocs_f}: {tuple(functions.values())}."


def indent(string: str) -> int:
    """

    Args:
        string (str): str

    Returns:
        int: Number of whitespace indentations

    """
    return sum(4 if char == "\t" else 1 for char in string[: -len(string.lstrip())])


def main():

    repo_dir = Path("/Users/hd65ox/Repositories/Medium/Python tips")

    p = repo_dir.glob("**/*.py")
    scripts = [x for x in p if x.is_file()]

    functions = defaultdict(list)
    for script in scripts:

        new_arguments = {}
        with open(script, "r") as file:
            script_lines = file.readlines()

            import importlib

            module = importlib.import_module(script.stem)

            for idx, line in enumerate(script_lines):
                if line.startswith("def ") and "main()" not in line:

                    function = re.split("def |\\(", line)[1]
                    functions[script].append(function)

                    f_ = getattr(module, function)
                    type_hints = get_type_hints(f_)

                    return_hint = type_hints.pop("return", None)
                    if type_hints:

                        file = "".join(script_lines[idx:])
                        raw_docstring = re.search(r'((?:"){1,3})([^"]+)\1', file)

                        if raw_docstring:

                            docstring_content = raw_docstring.group()
                            # docstring_lines = docstring_content.split("\n")

                            args = re.search(
                                r'    Args:(.*?)(    Example[s]?:|    Return[s]?:|    """)',
                                docstring_content,
                                re.DOTALL,
                            )

                            if args:

                                arguments = args.group()
                                argument_lines = arguments.split("\n")

                                exclude = ["Args:", "Example:", "Examples:", "Returns:", '"""']

                                argument_lines = [arg for arg in argument_lines if arg]
                                argument_lines = [arg for arg in argument_lines if not any(x in arg for x in exclude)]

                                for argument in argument_lines:
                                    arg_name = argument.split()[0]
                                    if arg_name in argument:

                                        if argument.split(":"):
                                            if "(" and ")" in argument.split(":")[0]:
                                                new_argument_docstring = re.sub(
                                                    r"\(.*?\)", f"({str(type_hints[arg_name])})", argument
                                                )

                                                idx = script_lines.index(f"{argument}\n")
                                                new_arguments[idx] = f"{new_argument_docstring}\n"

                                            else:
                                                print(f"no variable type in the argument: {arg_name}")
                                        else:
                                            print(f"no 'arg : description'-format for this argument: {arg_name}")
                                    else:
                                        print(f"no docstring for this argument: {arg_name}")
                            else:
                                print(f"there are no arguments in this docstring: {function}")
                        else:
                            print(f"no docstring for function: {function}")

                        if return_hint:

                            raw_return = re.search(r'    Return[s]?:(.*?)(    """)', docstring_content, re.DOTALL)

                            if raw_return:

                                return_argument = raw_return.group()
                                return_lines = return_argument.split("\n")

                                exclude = ["Returns:", '"""']

                                return_lines = [return_arg for return_arg in return_lines if return_arg]
                                return_lines = [
                                    return_arg
                                    for return_arg in return_lines
                                    if not any(x in return_arg for x in exclude)
                                ]

                                if return_lines and len(return_lines) == 1:

                                    return_arg = return_lines[0]
                                    if return_arg.split(":"):

                                        new_return_docstring = re.sub(r"\w(.*:)", f"{str(return_hint)}:", return_arg)

                                        idx = script_lines.index(f"{return_arg}\n")
                                        new_arguments[idx] = f"{new_return_docstring}\n"

                                    else:
                                        print(f"no variable-type in return statement docstring: {function}")
                                else:
                                    print(f"no return statement docstring argument: {function}")

                            else:
                                print(f"no return argument in docstring for function: {function}")

                        else:
                            print(f"no return type-hint for function: {function}")

                    else:
                        print(f"no type-hints for function: {function}")

        sorted_arguments = sorted(new_arguments.items(), reverse=True)

        for (idx, new_arg) in sorted_arguments:
            script_lines[idx] = new_arg

        with open(f"{repo_dir}/test_it.py", "w") as overwrite_script:
            overwrite_script.writelines(script_lines)
        exit()

    exit()

    python_tips_dir = (
        Path.cwd()
    )  # use `Path.cwd().parent` for all Python files in the repository and not just the 'Python Tips' folder

    automate_mkdocs_from_docstring(
        mkdocs_dir="scripts",
        mkgendocs_f="mkgendocs.yml",
        repo_dir=python_tips_dir,
        match_string="pages:\n",
    )


if __name__ == "__main__":
    main()

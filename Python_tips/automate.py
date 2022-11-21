"""Automates Python scripts formatting, linting and Mkdocs documentation."""

import ast
import importlib
import re
from collections import defaultdict
from pathlib import Path
from typing import Union, get_type_hints


def automate_mkdocs_from_docstring(
    mkdocs_dir: Union[str, Path], mkgendocs_f: str, repo_dir: Path, match_string: str
) -> str:
    """Automates the -pages for mkgendocs package by adding all Python functions in a directory to the mkgendocs config.

    Args:
        mkdocs_dir (typing.Union[str, pathlib.Path]): textual directory for the hierarchical directory & navigation in Mkdocs
        mkgendocs_f (str): The configurations file for the mkgendocs package
        repo_dir (pathlib.Path): textual directory to search for Python functions in
        match_string (str): the text to be matches, after which the functions will be added in mkgendocs format

    Example:
        >>>
        >>> automate_mkdocs_from_docstring('scripts', repo_dir=Path.cwd(), match_string='pages:')

    Returns:
        str: feedback message

    """
    p = repo_dir.glob('**/*.py')
    scripts = [x for x in p if x.is_file()]

    if Path.cwd() != repo_dir:  # look for mkgendocs.yml in the parent file if a subdirectory is used
        repo_dir = repo_dir.parent

    functions = defaultdict(list)
    for script in scripts:

        with open(script, 'r') as source:
            tree = ast.parse(source.read())

        for child in ast.iter_child_nodes(tree):
            if isinstance(child, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if child.name not in ['main']:
                    module = importlib.import_module(script.stem)
                    f_ = getattr(module, child.name)
                    function = f_.__name__
                    functions[script].append(function)

    with open(f'{repo_dir}/{mkgendocs_f}', 'r+') as mkgen_config:
        insert_string = ''
        for path, function_names in functions.items():
            insert_string += (
                f'  - page: "{mkdocs_dir}/{path.parent.name}/{path.stem}.md"\n    '
                f'source: "{path.parent.name}/{path.stem}.py"\n    functions:\n'
            )

            f_string = ''
            for f in function_names:
                insert_f_string = f'      - {f}\n'
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

    with open(f'{repo_dir}/{mkgendocs_f}', 'w') as mkgen_config:
        mkgen_config.writelines(contents)

    return f'Added to {mkgendocs_f}: {tuple(functions.values())}.'


def indent(string: str) -> int:
    """Count the indentation in whitespace characters.

    Args:
        string (str): text with indents

    Returns:
        int: Number of whitespace indentations

    """
    return sum(4 if char == '\t' else 1 for char in string[: -len(string.lstrip())])


def docstring_from_type_hints(repo_dir: Path, overwrite_script: bool = False, test: bool = True) -> str:
    """Automate docstring argument variable-type from type-hints.

    Args:
        repo_dir (pathlib.Path): textual directory to search for Python functions in
        overwrite_script (bool): enables automatic overwriting of Python scripts in repo_dir
        test (bool): whether to write script content to a test_it.py file

    Returns:
        str: feedback message

    """
    p = repo_dir.glob('**/*.py')
    scripts = [x for x in p if x.is_file()]

    functions = defaultdict(list)
    for script in scripts:

        with open(script, 'r') as source:
            tree = ast.parse(source.read())

        function_docs = []
        for child in ast.iter_child_nodes(tree):
            if isinstance(child, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if child.name not in ['main']:

                    docstring_node = child.body[0]
                    module = importlib.import_module(script.stem)

                    f_ = getattr(module, child.name)
                    type_hints = get_type_hints(f_)  # the same as f_.__annotations__

                    print(type_hints)
                    return_hint = type_hints.pop('return', None)
                    print(return_hint)
                    function = f_.__name__
                    functions[script].append(function)

                    if type_hints:

                        docstring = f'"""{ast.get_docstring(child, clean=True)}\n"""'
                        docstring_lines = docstring.split('\n')

                        if docstring:

                            args = re.search(
                                r'Args:(.*?)(Example[s]?:|Return[s]?:|""")',
                                docstring,
                                re.DOTALL,
                            )

                            new_arguments = {}
                            if args:

                                arguments = args.group()
                                argument_lines = arguments.split('\n')

                                exclude = [
                                    'Args:',
                                    'Example:',
                                    'Examples:',
                                    'Returns:',
                                    '"""',
                                ]

                                argument_lines = [arg for arg in argument_lines if arg]
                                argument_lines = [arg for arg in argument_lines if not any(x in arg for x in exclude)]

                                for argument in argument_lines:
                                    arg_name = argument.split()[0]
                                    if arg_name in argument:

                                        if argument.split(':'):
                                            if '(' and ')' in argument.split(':')[0]:

                                                variable_type = str(type_hints[arg_name])
                                                class_type = re.search(r"(<class ')(.*)('>)", variable_type)
                                                if class_type:
                                                    variable_type = class_type.group(2)

                                                new_argument_docstring = re.sub(
                                                    r'\(.*?\)',
                                                    f'({variable_type})',
                                                    argument,
                                                )

                                                idx = docstring_lines.index(f'{argument}')
                                                new_arguments[idx] = f'{new_argument_docstring}'

                                            else:
                                                print(f'no variable type in the argument: {arg_name}')
                                        else:
                                            print(f"no 'arg : description'-format for this argument: {arg_name}")
                                    else:
                                        print(f'no docstring for this argument: {arg_name}')
                            else:
                                print(f'there are no arguments in this docstring: {function}')

                            if return_hint:

                                raw_return = re.search(
                                    # r'(?<=Returns:\n).*',
                                    r'Return[s]?:\n(.*)',
                                    docstring,
                                    re.DOTALL,
                                )

                                if raw_return:

                                    return_argument = raw_return.group(1)
                                    return_lines = return_argument.split('\n')

                                    exclude = ['Returns:', '"""']

                                    return_lines = [return_arg for return_arg in return_lines if return_arg]
                                    return_lines = [
                                        return_arg
                                        for return_arg in return_lines
                                        if not any(x in return_arg for x in exclude)
                                    ]

                                    if return_lines and len(return_lines) == 1:

                                        return_arg = return_lines[0]
                                        if return_arg.split(':'):

                                            variable_type = str(return_hint)
                                            class_type = re.search(r"(<class ')(.*)('>)", variable_type)
                                            if class_type:
                                                variable_type = class_type.group(2)

                                            new_return_docstring = re.sub(
                                                r'\S(.*:)',
                                                f'{variable_type}:',
                                                return_arg,
                                            )

                                            idx = docstring_lines.index(f'{return_arg}')
                                            new_arguments[idx] = f'{new_return_docstring}\n'

                                        else:
                                            print(f'no variable-type in return statement docstring: {function}')
                                    else:
                                        print(f'no return statement docstring argument: {function}')
                                else:
                                    print(f'no return argument in docstring for function: {function}')
                            else:
                                print(f'no return type-hint for function: {function}')

                            sorted_arguments = sorted(new_arguments.items(), reverse=True)
                            for (idx, new_arg) in sorted_arguments:
                                docstring_lines[idx] = new_arg

                            docstring_lines = [f"{' ' * docstring_node.col_offset}{line}" for line in docstring_lines]
                            new_docstring = '\n'.join(docstring_lines)

                            function_docs.append(
                                (
                                    docstring_node.lineno,
                                    {
                                        'function_name': function,
                                        'col_offset': docstring_node.col_offset,
                                        'begin_lineno': docstring_node.lineno,
                                        'end_lineno': docstring_node.end_lineno,
                                        'value': new_docstring,
                                    },
                                )
                            )

                            # print(ast.unparse(child))
                            # you would be able to use ast.unparse(child), however this does not include # comments.
                            # https://stackoverflow.com/questions/768634/parse-a-py-file-read-the-ast-modify-it-then-write-back-the-modified-source-c

                        else:
                            print(f'no docstring for function: {function}')
                    else:
                        print(f'no type-hints for function: {function}')

        with open(script, 'r') as file:
            script_lines = file.readlines()

        function_docs.sort(key=lambda x: x[0], reverse=True)
        for (idx, docstring_attr) in function_docs:
            script_lines = (
                script_lines[: docstring_attr['begin_lineno'] - 1]
                + [f'{docstring_attr["value"]}\n']
                + script_lines[docstring_attr['end_lineno'] :]
            )

        if overwrite_script:
            if test:
                script = f'{repo_dir}/test_it.py'
            with open(script, 'w') as script_file:
                script_file.writelines(script_lines)

            print(f'Automated docstring generation from type hints: {script}')

    return 'Docstring generation from type-hints complete!'


def main():
    """Execute when running this script."""
    python_tips_dir = Path.cwd().joinpath('Medium/Python_tips')
    # python_tips_dir = Path.cwd().joinpath("Python_tips")

    docstring_from_type_hints(python_tips_dir, overwrite_script=True, test=False)

    automate_mkdocs_from_docstring(
        mkdocs_dir='scripts',
        mkgendocs_f='mkgendocs.yml',
        repo_dir=python_tips_dir,
        match_string='pages:\n',
    )


if __name__ == '__main__':
    main()

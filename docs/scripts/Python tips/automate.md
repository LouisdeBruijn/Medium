#


### automate_mkdocs_from_docstring
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/automate.py/#L10)
```python
.automate_mkdocs_from_docstring(
   mkdocs_dir: Union[str, Path], mkgendocs_f: str, repo_dir: Path,
   match_string: str
)
```

---
Automates the -pages for mkgendocs package by adding all Python functions in a directory to the mkgendocs config.


**Args**

* **mkdocs_dir** (typing.Union[str, pathlib.Path]) : textual directory for the hierarchical directory & navigation in Mkdocs
* **mkgendocs_f** (str) : The configurations file for the mkgendocs package
* **repo_dir** (pathlib.Path) : textual directory to search for Python functions in
* **match_string** (str) : the text to be matches, after which the functions will be added in mkgendocs format


**Example**


```python

>>> automate_mkdocs_from_docstring('scripts', repo_dir=Path.cwd(), match_string='pages:')

```

**Returns**

* **str**  : feedback message


----


### indent
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/automate.py/#L79)
```python
.indent(
   string: str
)
```

---
Count the indentation in whitespace characters.


**Args**

* **string** (str) : str


**Returns**

* **int**  : Number of whitespace indentations


----


### docstring_from_type_hints
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/automate.py/#L92)
```python
.docstring_from_type_hints(
   repo_dir: Path, overwrite_script: bool = False
)
```

---
Automate docstring argument variable-type from type-hints.


**Args**


repo_dir (pathlib.Path):
overwrite_script (bool):


**Returns**

* **str**  : feedback message


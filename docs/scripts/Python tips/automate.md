#


### automate_mkdocs_from_docstring
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/automate.py/#L11)
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
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/automate.py/#L80)
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
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/automate.py/#L93)
```python
.docstring_from_type_hints(
   repo_dir: Path, overwrite_script: bool = False, test: bool = True
)
```

---
Automate docstring argument variable-type from type-hints.


**Args**

* **repo_dir** (pathlib.Path) : textual directory to search for Python functions in
* **overwrite_script** (bool) : enables automatic overwriting of Python scripts in repo_dir
* **test** (bool) : whether to write script content to a test_it.py file


**Returns**

* **str**  : feedback message


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
* **mkgendocs_f** (<class 'str'>) : The configurations file for the mkgendocs package
* **repo_dir** (<class 'pathlib.Path'>) : textual directory to search for Python functions in
* **match_string** (<class 'str'>) : the text to be matches, after which the functions will be added in mkgendocs format


**Example**


```python

>>> automate_mkdocs_from_docstring('scripts', repo_dir=Path.cwd(), match_string='pages:')

```

**Returns**

* feedback message


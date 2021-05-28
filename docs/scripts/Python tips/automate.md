#


### automate_mkdocs_from_docstring
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/automate.py/#L6)
```python
.automate_mkdocs_from_docstring(
   mkdocs_dir: Union[str, Path], mkgendocs_f: str, repo_dir: Union[str, Path],
   match_string: str
)
```

---
Automates the -pages for mkgendocs package by adding all functions in a directory.


**Args**

* **mkdocs_dir** (str) : textual directory for the hierarchical directory & navigation in Mkdocs
* **mkgendocs_f** (str) : The configurations file for the mkgendocs package
* **repo_dir** (str) : textual directory to search for Python functions in
* **match_string** (str) : the text to be matches, after which the functions will be added in mkgendocs format


**Example**



```python

>>> automate_mkdocs_from_docstring('scripts', repo_dir=Path.cwd(), match_string='pages:')

```

**Returns**

* **str**  : feedback message


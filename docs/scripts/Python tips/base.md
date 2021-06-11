#


### parse_arguments
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/base.py/#L11)
```python
.parse_arguments()
```

---
Read arguments from a command line.

----


### print_df
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/base.py/#L28)
```python
.print_df(
   df: pd.DataFrame, rows: int, exit_script: bool = False
)
```

---
Prints a DataFrame.


**Args**

* **df** (pandas.core.frame.DataFrame) : tabular view to print.
* **rows** (int) : the number of rows to print.
* **exit_script** (bool) : whether to exit the script.


----


### unescape_html
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/base.py/#L42)
```python
.unescape_html(
   text: str
)
```

---
Converts any HTML entities found in text to their textual representation.


**Args**

* **text** (str) : utterance that may contain HTML entities.


**Examples**


```python

>>> unescape_html("&nbsp;")
""
>>> unescape_html("&amp;")
"&"
>>> unescape_html("&gt;")
">"
>>> unescape_html("&lt;")
"<"
>>> unescape_html("&le;")
"≤"
>>> unescape_html("&ge;")
"≥"

```

**Returns**

* **str**  : utterance without HTML entities.


----


### equal_array_items
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Python tips/base.py/#L70)
```python
.equal_array_items(
   x: List
)
```

---
Compares whether all array items are of the same type and content.


**Args**

* **x** (typing.List) : an array to compare list items in.


**Examples**


```python

>>> equal_array_items(["1", "1"])
True
>>> equal_array_items(["1", "2"])
False

```

**Returns**

* **bool**  : True if all items in this list are equal, False otherwise.


#


### print_df
[source](https://github.com/LouisdeBruijn/Medium.git/blob/master/Python tips/base.py/#L28)
```python
.print_df(
   df: pd.DataFrame, rows: int, exit_script: bool = False
)
```

---
Prints a DataFrame.


**Args**

* **df** (pd.DataFrame) : tabular view to print.
* **rows** (int) : the number of rows to print.
* **exit_script** (bool) : whether to exit the script.


----


### unescape_html
[source](https://github.com/LouisdeBruijn/Medium.git/blob/master/Python tips/base.py/#L43)
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


Example of HTML entities found during annotations::


```python

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
[source](https://github.com/LouisdeBruijn/Medium.git/blob/master/Python tips/base.py/#L73)
```python
.equal_array_items(
   x: List
)
```

---
Compares whether all array items are of the same type and content.


**Args**

* **x** (List) : an array to compare list items in.


**Examples**

* 20, 'labels': ['NORP'], 'start': 13, 'text': 'english'}         , {'end': 20, 'labels': ['NORP'], 'start': 13, 'text': 'english'}])
* 20, 'labels': ['NORP'], 'start': 13, 'text': 'english'}         , {'end': 20, 'labels': ['LOCATION'], 'start': 13, 'text': 'english'}])

True
False


**Returns**

* **bool**  : True if all items in this list are equal, False otherwise.


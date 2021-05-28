#


### fonts
[source](https://github.com/LouisdeBruijn/Medium/blob/master/PDF retrieval/pdf_retrieval.py/#L6)
```python
.fonts(
   doc, granularity = False
)
```

---
Extracts fonts and their usage in PDF documents.

:param doc: PDF document to iterate through
:type doc: <class 'fitz.fitz.Document'>
:param granularity: also use 'font', 'flags' and 'color' to discriminate text
:type granularity: bool

:rtype: [(font_size, count), (font_size, count}], dict
:return: most used fonts sorted by count, font style information

----


### font_tags
[source](https://github.com/LouisdeBruijn/Medium/blob/master/PDF retrieval/pdf_retrieval.py/#L44)
```python
.font_tags(
   font_counts, styles
)
```

---
Returns dictionary with font sizes as keys and tags as value.

:param font_counts: (font_size, count) for all fonts occuring in document
:type font_counts: list
:param styles: all styles found in the document
:type styles: dict

:rtype: dict
:return: all element tags based on font-sizes

----


### headers_para
[source](https://github.com/LouisdeBruijn/Medium/blob/master/PDF retrieval/pdf_retrieval.py/#L80)
```python
.headers_para(
   doc, size_tag
)
```

---
Scrapes headers & paragraphs from PDF and return texts with element tags.

:param doc: PDF document to iterate through
:type doc: <class 'fitz.fitz.Document'>
:param size_tag: textual element tags for each size
:type size_tag: dict

:rtype: list
:return: texts with pre-prended element tags

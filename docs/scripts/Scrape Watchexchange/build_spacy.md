#


### get_proxies
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Scrape Watchexchange/build_spacy.py/#L19)
```python
.get_proxies()
```

---
Returns list of free proxies for webscraping rotation

----


### random_user_agent
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Scrape Watchexchange/build_spacy.py/#L38)
```python
.random_user_agent()
```

---
Returns a randomly chosen User Agent for webscraper

----


### parse_url
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Scrape Watchexchange/build_spacy.py/#L74)
```python
.parse_url(
   url, proxy_pool = None, proxy_nr = None
)
```

---
Reads url.

----


### get_pages
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Scrape Watchexchange/build_spacy.py/#L98)
```python
.get_pages(
   soup
)
```

---
Get number of pages

----


### chrono24_result_page
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Scrape Watchexchange/build_spacy.py/#L103)
```python
.chrono24_result_page(
   watch_brand, output_file
)
```

---
Scrapes the result page of Chrono24 for main details and href links

:param watch_brand: the watch brand to scrape pages of from Chrono24
:type watch_brand: str
:param output_file: the .csv file where all the information should be stored
:type output_file: str

:rtype: .csv file
returns: watch_id|watch_manufacturer|watch_title|watch_currency|watch_price|href

----


### scrape_chrono24
[source](https://github.com/LouisdeBruijn/Medium/blob/master/Scrape Watchexchange/build_spacy.py/#L164)
```python
.scrape_chrono24(
   csv_main_details
)
```

---
Scrape all watch information from detail-page of Chrono24
with links from csv file input


:param csv_main_details: the .csv file with the information and links from Chrono24 main-detail page
:type csv_main_details: str

:rtype: .json file with all details
:return: list of json dictionary with all details per watch listing

#!/usr/bin/env python3
# File name: build_spacy.py
# Description: build SpaCy model from Chrono24 data
# Author: Louis de Bruijn
# Date: 27-01-2020


from urllib.request import Request, urlopen
import requests
import random
from bs4 import BeautifulSoup
import re
import json
import time

from itertools import cycle


def get_proxies():
    """Returns list of free proxies for webscraping rotation"""
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    response = response.content

    soup = BeautifulSoup(response, "html.parser")
    table = soup.find('table', id='proxylisttable')
    table_body = table.find('tbody')

    proxies = set()
    for row in table_body.findAll('tr'):
        columns = row.findAll('td')
        proxy = "{0}:{1}".format(columns[0].text, columns[1].text)
        proxies.add(proxy)

    return proxies


def random_user_agent():
    """Returns a randomly chosen User Agent for webscraper"""
    user_agent_list = [
        #Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        #Firefox
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
    ]

    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}

    return headers


def parse_url(url, proxy_pool=None, proxy_nr=None):
    """Reads url."""
    # req = Request(url, headers=headers)
    # web_byte = urlopen(req).read()
    # response = web_byte.decode('utf-8')
    headers = random_user_agent()

    if not proxy_pool:
        response = requests.get(url, headers=headers)
    else:
        tries = 0
        while tries < proxy_nr:
            try:
                tries += 1
                proxy = next(proxy_pool)
                response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=5.0)
            except Exception as e:
                print("Skipping. Connnection error. Tries {0}".format(tries))

    response = response.content
    soup = BeautifulSoup(response, "html.parser")
    return soup


def get_pages(soup):
    """Get number of pages"""
    return soup.find('ul', {'class': 'pagination inline pull-xs-none pull-sm-right'}).findAll('li')[-2].find('a').text


def chrono24_result_page():
    """Scrapes the result page of Chrono24 for main details and href links

    returns: watch_id|watch_manufacturer|watch_title|watch_currency|watch_price|href
    """
    soup = parse_url('https://www.chrono24.com/{0}/index-{1}.htm'.format('rolex', 1))
    page_nr = int(get_pages(soup))

    proxies = get_proxies()
    proxies_nr = len(proxies)
    print('Scraping {0} pages with {1} proxies.'.format(page_nr, proxies_nr))
    proxy_pool = cycle(proxies)

    with open('spacy_pages.csv', 'a') as spacy_rolex:
        if len(open('spacy_pages.csv').readlines()) < 1:
            spacy_rolex.write('watch_id|watch_manufacturer|watch_title|watch_currency|watch_price|href\n')

        for i in range(0, page_nr+1):
            url = 'https://www.chrono24.com/{0}/index-{1}.htm'.format('rolex', i)
            print('Scraping page number {0} [{1}].'.format(i, url))
            # soup = parse_url(url, proxy_pool=proxy_pool, proxy_nr=proxies_nr)
            soup = parse_url(url, proxy_pool=None, proxy_nr=None)
            watches = soup.find('div', id='wt-watches')

            for watch in watches.findAll('div', {'class': 'article-item-container'}):

                article_item = watch.find('a', {'class': 'article-item'})
                try:
                    w_title = article_item.find('div', {'class': 'article-title'}).text.strip()
                    w_href = article_item.get('href')
                    w_id = article_item.get('data-article-id')
                    w_manufacturer = article_item.get('data-manufacturer')

                    if w_id is None:  # some promotion watch in between, skip it
                        continue

                    article_price = article_item.find('strong').text.strip()
                    match = re.search(r'([\D]+)([\d,]+)', article_price)
                    if match is None:  # article_price == 'Price on request'
                        w_currency = ''
                        w_price = ''
                    else:
                        w_currency = match.group(1)
                        w_price = match.group(2)

                    string = "|".join([w_id, w_manufacturer, w_title, w_currency, w_price, w_href])
                    spacy_rolex.write(string + '\n')
                except Exception as e:
                    print(e)

            print('Page {0} finished.'.format(i))

    return "Succesfully scraped {0} pages.".format(page_nr)


def main():



    with open("spacy_pages.csv") as result_page:
        next(result_page)

        page_nr = len(open('spacy_pages.csv').readlines())
        print('Scraping {0} pages.'.format(page_nr))

        start = time.time()
        for idx, line in enumerate(result_page):

            if idx % 1000 == 0 and idx is not 0:
                print("first {0} took {1}.".format(idx, round(time.time()-start), 2))

            line = line.rstrip('\n').split('|')
            url = "https://www.chrono24.com{0})".format(line[-1])
            soup = parse_url(url, proxy_pool=None, proxy_nr=None)

            print('Scraping page number {0} [{1}].'.format(idx+1, url))

            dic = {}
            dic["Watch ID"] = line[0]
            dic["Watch manufacturer"] = line[1]
            dic["Post title"] = line[2]
            dic["Post currency"] = line[3]
            dic["Post amount"] = line[4]
            dic["Post link"] = line[5]

            try:
                shipping_div = soup.find('span', id='shipping-costs')
                ship_divs = shipping_div.findAll('div')
                for div in ship_divs:
                    if 'hidden' not in div.get('class') and 'js-shipping-cost-free' in div.get('class'):
                        shipping_currency = '$'
                        shipping_amount = 0
                    if 'hidden' not in div.get('class') and 'js-shipping-cost' in div.get('class'):
                        span = div.find('span')
                        shipping_currency = span.text[2]
                        shipping_amount = span.text[3:]

                dic["Shipping currency"] = shipping_currency
                dic["Shipping costs"] = shipping_amount
            except AttributeError as e:
                print(e)  # no shipping information provided

            try:
                table_el = soup.find('div', {'class': 'row text-lg m-b-6'})
                table_div = table_el.findAll('div', {'class': 'col-md-12'})
            except AttributeError as e:
                print(e)  # link is wrong, it does not go to a detail-page

            specs = table_div[0]
            description = table_div[1]

            ## SPECIFICATIONS
            table_bodies = specs.findAll('tbody')
            for body in table_bodies:
                tr_els = body.findAll('tr')
                tr_els = tr_els[2:]  # skip "Basic Info" header and "Listing Number"

                for tr in tr_els:
                    td_els = tr.findAll('td')
                    descr = td_els[0].find('strong').text
                    value = td_els[1].text.strip().split('\n')[0]
                    dic[descr] = value

            json_dic = json.dumps(dic)
            with open("chrono24_watches.json", "a") as watch_json:
                if len(open('chrono24_watches.json').readlines()) < 1:
                    watch_json.write('[\n')
                watch_json.write('\t' + json_dic + ',\n')

            ## DESCRIPTION TEXT
            '''description is loaded dynamically, need selenium for that...'''

            # print('Page {0} finished.'.format(idx+1))


if __name__ == '__main__':
    main()

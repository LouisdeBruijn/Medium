#!/usr/bin/env python3
# File name: watch_to_buy.py
# Description: compare WatchExchange listing price and Chrono24 prices
# Author: Louis de Bruijn
# Date: 29-08-2019

import praw
import datetime as dt
import re
import pickle

# creating and saving a dic
import json
from collections import defaultdict

# scraping
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# Google Vision API
import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Spacy NER tagging
import spacy
import en_core_web_sm

# Selenium fill web form
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException # catch exception

# Explicit waits in Selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_currencies():
    '''collect all known currencies'''

    url = 'https://en.wikipedia.org/wiki/ISO_4217'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    with open('currencies.txt', 'w') as curr_file:
        for table in soup.findAll('table', {'class': 'wikitable sortable'}):
            for tr in table.findAll('tr')[1:]:
                code = tr.findAll('td')[0].text
                curr_file.write(code[:3] + '|')

def get_wiki_watch_brands():
    '''collect all watch brands on Wikipedia page in a pipe-delimited text-file'''

    url = 'https://en.wikipedia.org/wiki/List_of_watch_manufacturers'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    with open('watch_brands.txt', 'w') as watch_file:        
        for ul in soup.findAll('ul'):
            if ul.find_previous_sibling():
                if ul.find_previous_sibling().name == 'h2':
                    for a in ul.findAll('a'):
                        brand_name = re.sub(r" ?\([^)]+\)", "", a['title'])
                        watch_file.write(brand_name + '|')



def get_chrono24_watch_brands():
    '''collect all watch brands on Wikipedia page in a pipe-delimited text-file'''

    url = 'https://www.chrono24.com/search/browse.htm?char=A-Z'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    with open('watch_brands.txt', 'r') as brands_file: 
        names = brands_file.readline()
        brands = names.split('|')

    for ul in soup.findAll('ul', {'class': 'list-unstyled row'}):
        for li in ul.findAll('li', {'class': 'col-xs-12 col-sm-8 col-md-6'}):
            for a in li.findAll():
                brand_name = a['title'].rstrip()
                if brand_name not in brands:
                    with open('watch_brands.txt', 'a') as watch_file:
                        watch_file.write(brand_name + '|')


def get_ablogtowatch_watch_brands():
    '''collect all watch brands on Wikipedia page in a pipe-delimited text-file'''

    url = 'https://www.ablogtowatch.com/watch-brands/'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    web_byte = urlopen(req).read()
    response = web_byte.decode('utf-8')
    soup = BeautifulSoup(response, "html.parser")

    with open('watch_brands.txt', 'r') as brands_file: 
        names = brands_file.readline()
        brands = names.split('|')

    for p in soup.findAll('p', {'class': 'brndWtchName'}):
        brand_name = p.text

        if brand_name not in brands:
            with open('watch_brands.txt', 'a') as watch_file:
                watch_file.write(brand_name + '|')



def get_chrono24_models():
    '''gets the models from the Chrono24 site'''

    url = 'https://www.chrono24.com/watches/mens-watches--62.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    with open('watch_models.txt', 'w') as models_file:
        model = soup.findAll('div', {'class': 'scroll-area checkbox-list m-b-3'})[1]
        for inp in model.findAll('input'):
                models_file.write(inp['data-label'] + '|')


def google_vision(file_name):
    '''returns best matches based on Google Vision Cloud API'''
    matches = []

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name)

    # Loads the image into memory
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs logo detection on the image file
    logo_response = client.logo_detection(image=image)
    logos = logo_response.logo_annotations

    # Performs web (text) detection on image file
    web_response = client.web_detection(image=image)
    web_brands = web_response.web_detection.web_entities

    # returning list of matching brand names
    matches = [logo.description for logo in logos] 

    # Only return if image is labelled as a watch
    if web_brands[0].description == 'Watch':
        best_web_match = web_brands[1].description
        matches.append(best_web_match)

    return matches

def get_date(created):
    '''returns date from UNIX timestamp'''
    return dt.datetime.fromtimestamp(created)



def watchbase_dataset():
    '''creates a dictionary from watchbase dataset with links for selenium'''
    dic = defaultdict(list)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://watchbase.com/watches")

    brand_container = driver.find_element_by_id('brand-container')
    brand_boxes = brand_container.find_elements_by_class_name('brand-box')
    for brand_box in brand_boxes:
        h3 = brand_box.find_element_by_tag_name('h3')
        try:
            image = h3.find_element_by_tag_name('img')
            brand_name = image.get_attribute('title')
        except NoSuchElementException:
            a = h3.find_element_by_tag_name('a')
            brand_name = a.text

        models = brand_box.find_elements_by_class_name('link-color')
        for model in models:
            model_name = model.text
            model_link = model.get_attribute('href')
            if model_name:
                dic[brand_name].append((model_name, model_link))

    file = open('brand_dictionary.json', 'w')
    json.dump(dic, file)

    # brand_links = json.load(open('brand_dictionary.json', 'r'))

    return dic

def scrape_watch_models():
    '''scraping all the brands and models in a nested dictionary'''
    dic = defaultdict(dict)

    # open selininum driver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://watchbase.com/watches")
    main_window = driver.current_window_handle

    # click cookies notification away, otherwise we won't be able to click w/ selenium on the underlying links
    cookies = WebDriverWait(driver,5).until(
         EC.presence_of_element_located((By.ID, 'cookiescript_accept')))
    cookies.click()

    # find the elements
    brand_container = driver.find_element_by_id('brand-container')
    brand_boxes = brand_container.find_elements_by_class_name('brand-box')
    for brand_box in brand_boxes:
        # get the title
        h3 = brand_box.find_element_by_tag_name('h3')
        try:
            image = h3.find_element_by_tag_name('img')
            brand_name = image.get_attribute('title')
        except NoSuchElementException:
            a = h3.find_element_by_tag_name('a')
            brand_name = a.text

        # get models from new page
        models = brand_box.find_elements_by_class_name('link-color')
        for model in models:
            model_name = model.text
            if model_name:
                # add model_name to each brand_name
                dic[brand_name].update({ model_name: defaultdict(dict) })

                # click link, open new tab and switch to that tab
                ActionChains(driver).key_down(Keys.COMMAND).click(model).key_up(Keys.COMMAND).perform()
                new_window = driver.window_handles[-1]
                driver.switch_to.window(new_window)

                # check for recaptcha
                recaptcha = driver.find_element_by_tag_name('p')
                if recaptcha.text == 'Please verify that you are not a robot.':
                    print(model_name)
                    for key, value in dic.items():
                        for k, v in value.items():
                            print(key, k)
                    input('Waiting for recaptcha to continue: ')

                # watch model page
                model_brands = driver.find_elements_by_class_name('bottomtext')
                for model_brand in model_brands:
                    reference, description = model_brand.text.split('\n')
                    dic[brand_name][model_name].update({reference: description})

                # close driver if new tab opened and switch back to main window
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(main_window)

    with open('brands_models.pickle', 'wb') as handle:
        pickle.dump(dic, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # with open('brands_models.pickle', 'rb') as handle:
    #     b = pickle.load(handle)


def main():

    with open('brands_models.pickle', 'rb') as handle:
        dic = pickle.load(handle)

    print(len(dic))

    cnt = 0
    tot = 0
    total = 0
    for key, value in dic.items():
        cnt += 1
        for k, v in value.items():
            tot += 1
            print(key, k)
            total += len(v)


    print(cnt, tot, total)

    # initialize SpaCy English model
    nlp = spacy.load("en_core_web_sm")

    with open('currencies.txt', 'r') as curr_file:
        curr = curr_file.readline()

    with open('watch_brands.txt', 'r') as brands_file:
        brands = brands_file.readline()

    with open('watch_models.txt', 'r') as models_file:
        for line in models_file:
            models = line.split('|')


    with open('../../Reddit secrets/secrets.txt') as f:
        keys = f.read().split('|')

    reddit = praw.Reddit(client_id=keys[0],
                         client_secret=keys[1],
                         user_agent=keys[2],
                         username=keys[3],
                         password=keys[4])

    subreddit = reddit.subreddit('Watchexchange')

    print(models)

    cnt = 0
    for submission in subreddit.new(limit=100):
        if submission.title.startswith('[WTS]'):

            # use Google Vision API if submission contains an image
            '''if submission.url.endswith('.jpg'):
                file_name = 'images/{0}.jpg".format(submission)'
                urllib.request.urlretrieve(submission.url, file_name)
                google_matches = google_vision(file_name)
                print(google_matches)
            '''
            # print(submission.url)
            # print(get_date(submission.created))
            redditer = submission.author
            # print(redditer.name)

            all_comments = submission.comments.list()
            for comment in all_comments:
                if comment.author == submission.author:

                    # regex to find currency symbols before, after and if no symbols used
                    before = re.findall('((?:\*\*)?(?:~~)?(?:{0})?(?:\*\*)?(?:~~)?[$\€\£](?:~~)?(?:\*\*)?\d+(?:~~)?(?:\*\*)?(?:[\.\,]\d+)?(?:~~)?(?:\*\*)?(?:[ ?](?:{1}))?)(?:\*\*)?(?:~~)?'
                        # $ 2700 USD
                        .format(curr, curr), comment.body)
                    after = re.findall('(?:\*\*)?(?:~~)?(?:{0})?(?:\*\*)?(?:~~)?(?:\*\*)?\d+(?:~~)?(?:\*\*)?(?:[\.\,]\d+)?(?:~~)?(?:\*\*)? ?[$\€\£](?:(?: ?)(?:{1}))?(?:\*\*)?(?:~~)?'
                        .format(curr, curr), comment.body)
                        # 2700 $ USD
                    acronym = re.findall('(?:\~\~)?(?:\*\*)?\d+(?:\*\*)?(?:\~\~)?(?:[\.\,]\d+)?(?:\*\*)?(?:\~\~)?(?:(?: ?)(?:{0}))(?:\*\*)?(?:~~)?'
                        .format(curr), comment.body)
                    
                    # if nothing found, print line with 'price' in it
                    price_line = re.search('.*(Price|Price|price|PRICE).*\n', comment.body)
                    

                    lol = 'Selling this Junghans 027/3500.00. I bought this recently but only wore it a few times because my Sinn is taking most of my wrist time. I am selling for $625 USD F&F or +3% for G&S. Shipping from Ontario, Canada.'
                    pol = 'Omega Speedmaster Professional ref 145.022-69 (Omega 861 movement) **Notice cool engraving on caseback!**'

                    print(submission.title)


                    #TODO: heb nu de models ook in een text file... hopelijk is dit genoeg??

                    # if None not in (before, after, acronym, price_line):
                    #     doc = nlp(pol)
                    #     for ent in doc.ents:
                    #         print(ent.text, ent.label_)


                    #     for sent in doc.sents:
                    #         if 'Omega' in sent.text:
                    #             for token in sent:
                    #                 print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
                    #                         token.shape_, token.is_alpha, token.is_stop)
                    # exit()
                    # if before:
                    #     print('before', before)
                    # elif after:
                    #     print('after', after)
                    # elif acronym:
                    #     print('no currency symbol', acronym)
                    # elif price_line:
                    #     print(price_line)
                    #     price = re.search('(\~\~)?(\*\*)?\d+(\*\*)?(\~\~)?([\.\,]\d+)?(\*\*)?(\~\~)?',
                    #     price_line)
                    #     print(price)
                    # else:
                    #     print(comment.body)

                    # with open('brand_excerpts.txt', 'a+') as write_out:
                    #     watch = re.search('(?:{0}).*\n'.format(brands), comment.body)
                    #     if watch:
                    #         write_out.write(watch.group(0))



# dit is trouwens ook interessant om te scrapen omdat die data verloren gaat doordat mensen hun post aanpassen
# nu nog de titels
# nu nog kijken of we wel overal die ~~ en ** hebben staan


if __name__ == '__main__':
    main()

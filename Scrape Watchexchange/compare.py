#!/usr/bin/env python3
# File name: watch_to_buy.py
# Description: compare WatchExchange listing price and Chrono24 prices
# Author: Louis de Bruijn
# Date: 29-08-2019

import praw
import datetime as dt
import re
import pickle

# stopwords
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer


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
    """collect all known currencies"""

    url = 'https://en.wikipedia.org/wiki/ISO_4217'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    with open('currencies.txt', 'w') as curr_file:
        for table in soup.findAll('table', {'class': 'wikitable sortable'}):
            for tr in table.findAll('tr')[1:]:
                code = tr.findAll('td')[0].text
                curr_file.write(code[:3] + '|')


def get_wiki_watch_brands():
    """collect all watch brands on Wikipedia page in a pipe-delimited text-file"""

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
    """collect all watch brands on Wikipedia page in a pipe-delimited text-file"""

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
    """collect all watch brands on a blog to watch page in a pipe-delimited text-file"""

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
    """gets the models from the Chrono24 site"""

    url = 'https://www.chrono24.com/watches/mens-watches--62.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    with open('watch_models.txt', 'w') as models_file:
        model = soup.findAll('div', {'class': 'scroll-area checkbox-list m-b-3'})[1]
        for inp in model.findAll('input'):
                models_file.write(inp['data-label'] + '|')


def get_date(created):
    """returns date from UNIX timestamp"""
    return dt.datetime.fromtimestamp(created)


def watchbase_dataset():
    """creates a dictionary from watchbase dataset with links for selenium"""
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
    """scraping all the brands and models in a nested dictionary"""
    dic = defaultdict(dict)

    # open selininum driver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://watchbase.com/watches")
    main_window = driver.current_window_handle

    # click cookies notification away, otherwise we won't be able to click w/ selenium on the underlying links
    cookies = WebDriverWait(driver, 5).until(
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


class Watch():
    """A class concerning all properties of a watch"""

    def __init__(self, submission, google_vision=False):
        self.submission = submission
        self.google_vision = google_vision

        self.comment_count = 0
        self.errors = []

        self.post = ''
        self.li_post = []
        self.brand = ''
        self.model = ''
        self.subtype = ''
        self.description = []
        self.google_matches = []

        # initialize pipe-delimited strings and lists
        self.pi_terms = open('all_watches.txt', 'r').readline()
        self.li_terms = self.__split_pipe('all_watches.txt')

        self.pi_currencies = open('currencies.txt', 'r').readline()
        self.pi_brands = open('watch_brands.txt', 'r').readline()
        self.li_brands = self.__split_pipe('watch_brands.txt')
        self.li_models = self.__split_pipe('watch_models.txt')
        self.di_types = pickle.load(open('brands_models.pickle', 'rb'))

        if submission:
            self.__initialize()


    def __initialize(self):
        """Initalize all properties"""
        if not isinstance(self.submission, praw.models.reddit.submission.Submission):
            raise TypeError("Submission is not of type 'Reddit Submission'")
        if not self.submission.title.startswith('[WTS]'):
            raise ValueError("Submission Title does not start with '[WTS]'")

        if self.google_vision:
            self.google_matches = self.__google_vision(self)

        # append title and comments to one string
        self.post = self.submission.title + '\n'
        for comment in self.submission.comments.list():
            if comment.author == self.submission.author:
                self.comment_count += 1
                self.post += comment.body


        # find brand name
        tknzr = TweetTokenizer()
        self.li_post = tknzr.tokenize(self.post)

        terms = []
        for term in self.li_terms:
            if term in self.li_post:
                terms.append(term)

        print(self.li_post)
        print()
        print(terms)
        print()

        # li_brand = re.findall(r'\w+', brand.group())
        # print(brand)
        # print(li_brand)
        # brands = re.findall('(?:{0}).*\n'.format(self.pi_terms), self.post)
        # print(brands)
        # print()
        # if not brand:
        #     return "No brand was found"
        # li_brand = re.findall(r'\w+', brand.group())
        # self.__find_brand(li_brand)

        # # find model and type
        # tknzr = TweetTokenizer()
        # li_post = tknzr.tokenize(self.post)
        # li_post_clean = self.clean_list(li_post)
        # self.__find_model(li_post, li_post_clean)

        # find price

        # # regex to find currency symbols before, after and if no symbols used
        # before = re.findall('((?:\*\*)?(?:~~)?(?:{0})?(?:\*\*)?(?:~~)?[$\€\£](?:~~)?(?:\*\*)?\d+(?:~~)?(?:\*\*)?(?:[\.\,]\d+)?(?:~~)?(?:\*\*)?(?:[ ?](?:{1}))?)(?:\*\*)?(?:~~)?'
        #     .format(curr, curr), comment.body)
        #     # $ 2700 USD
        # after = re.findall('(?:\*\*)?(?:~~)?(?:{0})?(?:\*\*)?(?:~~)?(?:\*\*)?\d+(?:~~)?(?:\*\*)?(?:[\.\,]\d+)?(?:~~)?(?:\*\*)? ?[$\€\£](?:(?: ?)(?:{1}))?(?:\*\*)?(?:~~)?'
        #     .format(curr, curr), comment.body)
        #     # 2700 $ USD
        # acronym = re.findall('(?:\~\~)?(?:\*\*)?\d+(?:\*\*)?(?:\~\~)?(?:[\.\,]\d+)?(?:\*\*)?(?:\~\~)?(?:(?: ?)(?:{0}))(?:\*\*)?(?:~~)?'
        #     .format(curr), comment.body)

        # # if nothing found, print line with 'price' in it
        # price_line = re.search('.*(Price|Price|price|PRICE).*\n', comment.body)

        # print(before)
        # print(after)
        # print(acronym)
        # print(price_line)


    def __find_model(self, li_post, li_post_clean):
        """Finds the watch model and its subtype

        :param li li_post: tokenized post
        :param li li_post_clean: preprocessed li_post (stopwords & articles)
        """
        watch_models = self.di_types[self.brand]
        watch_types = []
        if watch_models:
            for model, subtype in watch_models.items():
                if model in li_post:
                    self.model = model
                    # print('Model found (1): ', self.model)
            if not self.model:
                for model, subtype in watch_models.items():
                    li_model = model.split()
                    for m in li_model:
                        if m in li_post_clean:
                            self.model = m
                            watch_types.append(model)
                            # print('Model found (2): ', self.model)
            if not self.model:
                for model, subtype in watch_models.items():
                    li_model = model.split()
                    for m in li_model:
                        if m in li_post:
                            self.model = m
                            watch_types.append(model)
                            # print('Model found (3): ', self.model)

            if self.model and watch_types:
                # print('model and possible types', self.model, watch_types)
                for watch_type in watch_types:
                    for subtype, descr in watch_models[watch_type].items():
                        if subtype in li_post_clean:
                            self.subtype = subtype
                            # print('Subtype found (1): ', self.subtype)

                if not self.subtype:
                    for watch_type in watch_types:
                        for subtype, descr in watch_models[watch_type].items():
                            if subtype in li_post:
                                self.subtype = subtype
                                # print('Subtype found (2): ', self.subtype)

                if not self.subtype:
                    for watch_type in watch_types:
                        for subtype, descr in watch_models[watch_type].items():
                            li_subt = subtype.split()
                            for subt in li_subt:
                                if subt in li_post:
                                    self.subtype = subtype
                                    # print('Subtype found (3): ', self.subtype)

            ### alleen werkt dit al niet altijd..
            # nu nog voor description


        else:
            self.errors.append("Brand '{0}' not found in database".format(self.brand))


    def clean_list(self, li_post):
        """Removes stopwords, punctuation from list items

        :param li li_post: list of tokens from Reddit post (title and comments)
        :rtype: li
        :return: cleaned list of tokens
        """
        stop_words = set(stopwords.words('english'))
        # remove stopwords
        li_post_clean = [w for w in li_post if w not in stop_words]
        # remove punctuation
        li_post_clean = [w for w in li_post_clean if w not in string.punctuation]
        # remove non-string tokens
        li_post_clean = [w for w in li_post_clean if w.isalpha()]
        # remove single character tokens
        li_post_clean = [w for w in li_post_clean if len(w) > 1]

        return li_post_clean


    def error_log(self):
        """Show error log"""
        for err in self.errors:
            print(err)
        if self.errors:
            return True



    def __find_brand(self, li_brand):
        """Finds the watch brand and add it as a property"""
        # for token in li_brand:
        #     if token in self.li_brands:
        #         self.brand = token
        #         # print('Brand found: ', self.brand)
        # if not self.brand:
        #     self.errors.append('Brand not found')


    def __google_vision(self):
        """Use Google Vision API if submission contains an image"""
        if self.submission.url.endswith('.jpg'):
                filename = 'images/{0}.jpg".format(submission)'
                urllib.request.urlretrieve(self.submission.url, filename)
                google_matches = self.googleVision(filename)
                return google_matches
        else:
            print('Submission does not consist of an image')



    def googleVision(filename):
        """Returns best matches based on Google Vision Cloud API

        :param str: filename of the image
        :rtype: li
        :return: list of logo and brand matches found in image
        """
        matches = []

        # Instantiates a client
        client = vision.ImageAnnotatorClient()

        # The name of the image file to annotate
        file_path = os.path.join(os.path.dirname(__file__), filename)

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


    def __split_pipe(self, filename):
        """Splits pipe-delimited file and returns list of items

        :param str: filename
        :rtype: li
        :return: items that are pipe-delimited in first line of filename
        """
        for line in open(filename, 'r'):
            return line.split('|')


    def __str__(self):
        """print the watch brand, model and subtype"""
        if self.brand and self.model and self.subtype:
            print(self.post)

        return "{0}: {1}, {2}".format(self.brand, self.model, self.subtype)








def main():

    # with open('watch_brands.txt', 'r') as brands_file:
    #     for line in brands_file:
    #         brands = line.split('|')


    # with open('watch_models.txt', 'r') as models_file:
    #     for line in models_file:
    #         models = line.split('|')

    # di_types = pickle.load(open('brands_models.pickle', 'rb'))

    # with open('watches.txt', 'w') as out_file:
    #     for brand, tuples in di_types.items():
    #         out_file.write(brand + '|' )
    #         for model, rest in tuples.items():
    #             out_file.write(model + '|')
    #             for subtype, description in rest.items():
    #                 out_file.write(subtype + '|' + description + '|')

    # with open('watches.txt', 'r') as all_watches_file:
    #     for line in all_watches_file:
    #         all_watches = line.split('|')

    # for b in brands:
    #     if b not in all_watches:
    #         all_watches.append(b)

    # for m in models:
    #     if m not in all_watches:
    #         all_watches.append(m)

    # with open('all_watches.txt', 'w') as all_file:
    #     all_file.write("|".join(all_watches))



    with open('../../Reddit secrets/secrets.txt') as f:
        keys = f.read().split('|')
    reddit = praw.Reddit(client_id=keys[0],
                         client_secret=keys[1],
                         user_agent=keys[2],
                         username=keys[3],
                         password=keys[4])
    subreddit = reddit.subreddit('Watchexchange')

    # initialize SpaCy English model
    # nlp = spacy.load("en_core_web_sm")

    for submission in subreddit.new(limit=5):
        if submission.title.startswith('[WTS]'):
            watch = Watch(submission)
            # print(watch.post)
            # print(submission.title)
            # print(watch)
            # if watch.error_log():
            #     print(submission.title)
            print()



# nu nog kijken of we wel overal die ~~ en ** hebben staan
# nu nog terug naar de PRIJS, kijken of we die goed catchen haha

if __name__ == '__main__':
    main()

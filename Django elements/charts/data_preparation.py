from .models import *

from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import seaborn as sns
import numpy as np
import time
import re
import json


def hashtag_demographics(route, label):
    """Return most-used hashtags."""
    dataset = {'hateval': Hashtag.objects.filter(tweet__hateval=True),
               'offenseval': Hashtag.objects.filter(tweet__offenseval=True),
               'all': Hashtag.objects.all()}
    db = dataset.get(route)

    if label == 'abuse':
        db = db.filter(tweet__pre_annotation='abuse')
    elif label == 'no-abuse':
        db = db.filter(tweet__pre_annotation='no-abuse')

    db_hashtags_c = db.distinct().order_by('-count')[:15]

    hashtag_labels = [h.text for h in db_hashtags_c]
    hashtag_values = [h.count for h in db_hashtags_c]
    hashtag_palette = sns.color_palette("Blues_r", len(hashtag_labels)).as_hex()

    return hashtag_labels, hashtag_values, hashtag_palette


def creation_date_demographics(route, label):
    """Return tweet creation dates."""
    dataset = {'hateval': Tweet.objects.filter(hateval=True),
               'offenseval': Tweet.objects.filter(offenseval=True),
               'all': Tweet.objects.all()}
    db = dataset.get(route)

    if label == 'abuse':
        db = db.filter(pre_annotation='abuse')
    elif label == 'no-abuse':
        db = db.filter(pre_annotation='no-abuse')

    db = db.values_list('created_at', flat=True)

    created = [int(time.mktime(t.timetuple())) * 1000 for t in db if t]
    created.sort()

    return created


def text_demographics(route, label, vectorizer):
    """Return most used words by tf-idf or count."""
    dataset = {'hateval': Tweet.objects.filter(hateval=True),
               'offenseval': Tweet.objects.filter(offenseval=True),
               'all': Tweet.objects.all()}
    db = dataset.get(route)

    if label == 'abuse':
        db = db.filter(pre_annotation='abuse')
    elif label == 'no-abuse':
        db = db.filter(pre_annotation='no-abuse')

    if vectorizer == 'tfidf':
        corpus = [tw.text for tw in Tweet.objects.filter(active=True)]
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        X = tfidf_vectorizer.fit_transform(corpus)
        scores = zip(tfidf_vectorizer.get_feature_names(),
                     np.asarray(X.sum(axis=0)).ravel())
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:15]
        items = [(score[0], round(score[1], 1)) for score in sorted_scores]

    elif vectorizer == 'count':
        db_text = db.values_list('text', flat=True)
        stop_words = stopwords.words('english')
        stop_words += ['I', 'RT', 'The']  # added own stop-words
        tknzr = TweetTokenizer()

        bow = {}
        for text in db_text:
            tokens = tknzr.tokenize(text)
            for token in tokens:
                token = re.sub(r'[^\w\s]', '', token)
                if token and token not in stop_words:
                    bow[token] = bow.get(token, 0) + 1

        items = sorted(bow.items(), key=lambda x: x[1], reverse=True)[:15]

    labels, values = zip(*items)
    colors = sns.cubehelix_palette(len(values)).as_hex()
    colors.reverse()

    return list(labels), list(values), colors


def user_demographics(route, label):
    """Return active/non-active user ratios"""
    dataset = {'hateval': Tweet.objects.filter(hateval=True, exception__isnull=False),
               'offenseval': Tweet.objects.filter(offenseval=True, exception__isnull=False),
               'all': Tweet.objects.filter(exception__isnull=False)}

    db_exc = dataset.get(route)

    if label == 'abuse':
        db_exc = db_exc.filter(pre_annotation='abuse')
    elif label == 'no-abuse':
        db_exc = db_exc.filter(pre_annotation='no-abuse')

    db_exc = db_exc.distinct().values_list('exception', flat=True)

    exceptions = {}
    for exc in db_exc:
        json_exc = json.loads(exc)
        if len(json_exc) > 1:
            string = "[{0}] {1}".format(json_exc['code'], json_exc['message'][:-1])
            exceptions[string] = exceptions.get(string, 0) + 1

    '''Get the unique/non-unique ratio'''
    unique_users_w_reply = TwitterUser.objects.filter(nr_tweets__lt=2,
                                                      twitter_user__in_reply_to_status_id__isnull=False,
                                                      twitter_user__in_reply_to_self=False).count()
    unique_users = TwitterUser.objects.filter(nr_tweets__lt=2).count()
    non_unique_users = TwitterUser.objects.filter(nr_tweets__gt=1).count()

    user_labels = ['unique users w/ in_reply_to_status_id to others', 'other unique users', 'non-unique users'] + list(exceptions.keys())
    user_values = [unique_users_w_reply, unique_users, non_unique_users] + list(exceptions.values())
    palette = ['#007bff', '#ffc107'] + sns.color_palette("Reds_r", len(user_labels)-1).as_hex()

    return user_labels, user_values, palette

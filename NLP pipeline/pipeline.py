#!/usr/bin/env python3
# File name: pipeline.py
# Description: An exemplary NLP pipiline with scikit-learn
# Authors: Louis de Bruijn & Gaetana Ruggiero
# Date: 11-03-2020

import sys
import argparse
import logging
from logging import critical, error, info, warning, debug

import numpy as np
import seaborn as sn
import pandas as pd
import random

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer

import nltk
from nltk.probability import FreqDist
import matplotlib.pyplot as plt


def parse_arguments():
    """Read arguments from a command line"""
    parser = argparse.ArgumentParser(description='Please add arguments')
    parser.add_argument('-v', '--verbose', metavar='verbosity', type=int, default=3,
        help='Verbosity of logging: 0 -critical, 1 -error, 2 -warning, 3 -info, 4 -debug')
    parser.add_argument('--input', metavar='FILE', required=True,
        help='txt file containing the data')
    parser.add_argument('--binary', action='store_true',
        help='Set if you want binary classification')

    args = parser.parse_args()
    verbose = {0: logging.CRITICAL, 1: logging.ERROR, 2: logging.WARNING, 3: logging.INFO, 4: logging.DEBUG}
    logging.basicConfig(format='%(message)s', level=verbose[args.verbose], stream=sys.stdout)

    return args


def read_corpus(corpus_file, binary):
    """Read input document and return the textual reviews and the sentiment or genre.

    :param corpus_file: newlime delimited file with a review on each line
    :type corpus_file: .txt file
    :param binary: flag for binary classification task
    :type binary: bool

    :rtype: (list, list)
    :return: reviews, classes
    """
    documents = []
    labels = []
    with open(corpus_file, 'r', encoding='utf-8') as f:
        for line in f:
            tokens = line.strip().split()

            documents.append(tokens[3:])

            if binary:
                # 2-class problem: positive vs negative
                labels.append(tokens[1])
            else:
                # 6-class problem: books, camera, dvd, health, music, software
                labels.append(tokens[0])

    return documents, labels


def shuffle_split(documents, labels, split):
    """Shuffle data to ensure random class distribution in train/test split.

    :param documents: all textual reviews in corpus
    :type documents: list of strings
    :param labels: all class labels in corpus
    :type labels: list of strings
    :param split: boundary for train/test sets
    :type split: int

    :rtype: (list, list, list)
    :return: documents train-set, documents test-set, labels train-set, labels test-set
    """
    tuples = [(doc, label) for doc, label in zip(documents, labels)]
    random.shuffle(tuples)
    X, Y = zip(*tuples)

    split_point = int(split*len(X))

    Xtrain = X[:split_point]
    Ytrain = Y[:split_point]
    Xtest = X[split_point:]
    Ytest = Y[split_point:]

    return Xtrain, Xtest, Ytrain, Ytest


def prior_probabilities(classes):
    """Compute prior probabilities for all class labels.

    :param classes: class labels for all documents in corpus
    :type classes: list

    :rtype: dict
    :return: prior probabilities for each unique class in corpus
    """
    dic = {}
    freq = FreqDist(classes)
    for k, v in freq.items():
        prior = freq[k] / len(classes)
        dic[k] = round(prior, 3)

    return dic


def baseline_classifier(Xtest, Ytest):
    """Baseline by randomly assigning a label to each document."""
    label_list = [label for label in set(Ytest)]  # random.choice cannot index a set, so needs to be a list
    baseline = [random.choice(label_list) for sent in Xtest]

    return baseline


def tokenize_pos(tokens):
    """Add POS-tags to each token.

    :param tokens: tokens (words) in a document
    :type tokens: list of strings

    :rtype: list of strings
    :return: list of tokens with _POS-{pos-tag} appended to each token
    """
    return [token+"_POS-"+tag for token, tag in nltk.pos_tag(tokens)]


class LengthFeatures(BaseEstimator, TransformerMixin):
    """Feature engineer the length of each feature."""
    def fit(self, x, y=None):
        return self

    def _get_features(self, doc):
        return {"words": len(doc), "unique_words": len(set(doc))}

    def transform(self, raw_documents):
        return [self._get_features(doc) for doc in raw_documents]


def feature_union(count, tfidf, textstats):
    """Add features the pipeline.

    :param count: flag for including count-vectorised tokens with POS-tags
    :type count: bool
    :param tfidf: flag for including tf-idf-vectorised tokens
    :type tfidf: bool
    :param textstats: flag for including length-features and mapping-based vectorised tokens
    :type textstats: bool

    :rtype: sklearn.pipeline.Pipeline
    :return: classifier with all features included
    """
    tfidf_vec = TfidfVectorizer(preprocessor=lambda x: x, tokenizer=lambda x: x)
    count_vec = CountVectorizer(preprocessor=lambda x: x, tokenizer=lambda x: x, ngram_range=(2, 2))
    length_vec = Pipeline([('textstats', LengthFeatures()), ('vec', DictVectorizer())])

    features = []
    if count:
        features.append(('count', count_vec))
    if tfidf:
        features.append(('tfidf', tfidf_vec))
    if textstats:
        features.append(('textstats', length_vec))

    if len(features) < 1:
        critical("Please select one or multiple features.")
        exit()

    vec = FeatureUnion(features)
    classifier = Pipeline([('vec', vec), ('cls', MultinomialNB())])
    print(type(classifier))

    return classifier


def tabular_results(Xtest, Ytest, Yguess, prior_prob, posterior_prob):
    """Return table with classification results.

    :param Xtest: documents in test-set
    :type Xtest: list
    :param Ytest: class labels in test-set
    :type Ytest: list
    :param Yguess: predicted class labels for test-set
    :type Yguess: list
    :param prior_prob: prior probabilities per document
    :type prior_prob: dict
    :param posterior_prob: posterior probabilities per document
    :type posterior_prob: numpy.ndarray

    :rtype: pandas.core.frame.DataFrame
    :return: Tabular results from the classifier including
        the tokenized sentence, true & predicted label
        prior & posterior probabilities
    """
    maximum_array = posterior_prob.max(axis=1)

    df = pd.DataFrame(columns=['sentence', 'true_label', 'prior_probabilities', 'predicted_label', 'posterior_probabilities'])
    df['sentence'] = Xtest
    df['true_label'] = Ytest
    for index, row in df.iterrows():
        row['prior_probabilities'] = prior_prob[row['true_label']]
    df['predicted_label'] = Yguess
    df['posterior_probabilities'] = np.around(maximum_array, 3)

    return df


def class_report(label, Ytest, Yguess, show_matrix):
    """Show classification report and accuracy scores.

    :param label: classifiers' label
    :type label: str
    :param Ytest: labels from test-set
    :type Ytest: list
    :param Yguess: predictions from classifier
    :type Yguess: list
    :param show_matrix: flag for showing the confusion matrix
    :type show_matrix: bool
    """
    info('--{0}--'.format(label))
    info('accuracy score for {0}: {1}'.format(label, round(accuracy_score(Ytest, Yguess), 3)))

    debug(classification_report(Ytest, Yguess))

    if show_matrix:
        conf_matrix = confusion_matrix(Ytest, Yguess)
        vis(conf_matrix, set(Ytest))

    info('')


def vis(conf_mat, labels):
    """Prettify the confusion matrix.

    :param conf_mat: confusion_matrix from sklearn
    :type conf_mat: sklearn.metrics.confusion_matrix
    :param labels: class labels
    :type labels: set

    :rtype: matplotlib.pyplot.plot
    :return: a confusion matrix plot
    """
    df_cm = pd.DataFrame(conf_mat, index=[i for i in labels], columns=[i for i in labels])
    plt.figure(figsize=(10, 7))
    plt.title('Confusion matrix')
    sn.heatmap(df_cm, annot=True, fmt='g')
    plt.show()


def main():

    X, Y = read_corpus(args.input, args.binary)

    Xtrain, Xtest, Ytrain, Ytest = shuffle_split(X, Y, 0.8)

    prior_prob = prior_probabilities(Y)
    info('Prior probabilities per class: {0}'.format(prior_prob))

    classifier = feature_union(count=False, tfidf=True, textstats=False)
    classifier.fit(Xtrain, Ytrain)  # fit the classifier on the training set
    Yguess = classifier.predict(Xtest)  # predict the labels on the test set
    posterior_prob = classifier.predict_proba(Xtest)  # calculate posterior probabilities

    df = tabular_results(Xtest, Ytest, Yguess, prior_prob, posterior_prob)
    with pd.option_context('display.max_rows', 10, 'display.max_columns', None):
        debug(df)

    baseline = baseline_classifier(Xtest, Ytest)
    class_report("Baseline classifier", Ytest, baseline, show_matrix=False)

    class_report("Naive Bayes classifier", Ytest, Yguess, show_matrix=True)


if __name__ == '__main__':
    args = parse_arguments()
    if args.input:
        main()

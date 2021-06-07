#!/usr/bin/env python3
# File name: iaa.py
# Description: Computes Cohen and Fleiss kappa statistics
# Author: Louis de Bruijn
# Date: 14-07-2020

import json

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa


def cohen_kappa_function(ann1, ann2):
    """Computes Cohen kappa for pair-wise annotators.

    :param ann1: annotations provided by first annotator
    :type ann1: list
    :param ann2: annotations provided by second annotator
    :type ann2: list

    :rtype: float
    :return: Cohen kappa statistic
    """
    count = 0
    for an1, an2 in zip(ann1, ann2):
        if an1 == an2:
            count += 1
    A = count / len(ann1)  # observed agreement A (Po)

    uniq = set(ann1 + ann2)
    E = 0  # expected agreement E (Pe)
    for item in uniq:
        cnt1 = ann1.count(item)
        cnt2 = ann2.count(item)
        count = (cnt1 / len(ann1)) * (cnt2 / len(ann2))
        E += count

    return round((A - E) / (1 - E), 4)


def fleiss_kappa_function(M):
    """Computes Fleiss' kappa for group of annotators.

    :param M: a matrix of shape (:attr:'N', :attr:'k') with 'N' = number of subjects and 'k' = the number of categories.
        'M[i, j]' represent the number of raters who assigned the 'i'th subject to the 'j'th category.
    :type: numpy matrix

    :rtype: float
    :return: Fleiss' kappa score
    """
    N, k = M.shape  # N is # of items, k is # of categories
    n_annotators = float(np.sum(M[0, :]))  # # of annotators
    tot_annotations = N * n_annotators  # the total # of annotations
    category_sum = np.sum(M, axis=0)  # the sum of each category over all items

    # chance agreement
    p = category_sum / tot_annotations  # the distribution of each category over all annotations
    PbarE = np.sum(p * p)  # average chance agreement over all categories

    # observed agreement
    P = (np.sum(M * M, axis=1) - n_annotators) / (n_annotators * (n_annotators - 1))
    Pbar = np.sum(P) / N  # add all observed agreement chances per item and divide by amount of items

    return round((Pbar - PbarE) / (1 - PbarE), 4)


def main():

    with open("pairwise.json", "r") as cohen_f:
        pairwise = json.load(cohen_f)

    cohen_function = cohen_kappa_function(pairwise["ann2"], pairwise["ann6"])
    cohen_sklearn = cohen_kappa_score(pairwise["ann2"], pairwise["ann6"])

    with open("group1.json", "r") as fleiss_f:
        group1 = json.load(fleiss_f)

    df = pd.DataFrame(group1)
    matrix = df.values  # convert Pandas DataFrame to Numpy matrix

    fleiss_function = fleiss_kappa_function(matrix)
    fleiss_statsmodels = fleiss_kappa(matrix)

    print("\n--Our functions--")
    print("Cohen Kappa score for ann2 and ann6: {0}.".format(cohen_function))
    print("Fleiss Kappa score for group 1: {0}.".format(fleiss_function))

    print("\n--Imported functions--")
    print("Cohen Kappa score for ann2 and ann6: {0}.".format(cohen_sklearn))
    print("Fleiss Kappa score for group 1: {0}.".format(fleiss_statsmodels))


if __name__ == "__main__":
    main()

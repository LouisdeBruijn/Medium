import os
from typing import Generator, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cv import BoostedKFold
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold

from evaluation.plot import plot_evaluation


def _cross_val_predict(X: Sequence, y: Sequence, y_test: Sequence, splits: Generator, cv):
    """Custom `cross_val_predict`.

    `cross_validate` and `cross_val_score` only returns scores, insufficient for confusion matrix
    `cross_val_predict` does what we need, but cannot take test-set that is different in size than y
        which is the case for our BoostedKFold() split
    """
    y_predictions = np.empty(len(y_test))
    for (training_indices, testing_indices) in splits:
        lr = LogisticRegression(fit_intercept=True)
        lr.fit(X[training_indices], y[training_indices].ravel())
        y_predict = lr.predict(X[testing_indices])

        for idx_pred, y_pred in zip(testing_indices, y_predict):
            y_predictions[idx_pred] = y_pred

    plot_evaluation(
        y_test,
        y_predictions,
        title=f'{type(cv).__name__} {cv.n_splits}-folds {os.linesep} '
        f'accuracy {round(accuracy_score(y_test, y_predictions), 3)}',
    )


def test_boosted_kfold_with_custom_dataset():
    """Test BoostedKfold CV with custom data sample."""
    n_splits = 3

    data = pd.read_csv('cross_validation/data/sample.csv', index_col='id')
    X = data[['feature_1', 'feature_2']].to_numpy()
    y = data[['label']].to_numpy()
    groups = data[['sample']].replace({'random': 0, 'boosted': -1}, inplace=False).to_numpy()

    cv = BoostedKFold(n_splits=n_splits, shuffle=True)

    splits = cv.split(X, y, groups)
    random_sample = data[data['sample'] == 'random']
    y_random = random_sample[['label']].to_numpy()
    _cross_val_predict(X=X, y=y, y_test=y_random, splits=splits, cv=cv)

    splits = cv.split(X, y, groups)
    fig, ax = plt.subplots()
    cv.plot(X, y, groups, splits, ax, marker='o')
    plt.subplots_adjust(left=0.13, right=0.81)
    plt.show()


def test_boosted_kfold_unbalanced_dataset():
    """Test BoostedKfold CV with unbalanced dataset against StratifiedKfold."""
    # `flip_y` has to be 0 for the actual class proportions `weights` to exactly match
    X, y = make_classification(n_samples=1000, n_classes=2, weights=[0.95, 0.05], flip_y=0, shuffle=False)
    n_splits = 5

    # 80% of minority class of `n_samples` will be our boosted sample data
    groups = np.ones(len(y))
    boosted_sample_size = round(0.3 * 0.05 * len(groups))
    minority_class_indices = np.where(y == 1)[0]
    boosted_minority_class_indices = minority_class_indices[:boosted_sample_size]
    # replace indices of boosted samples value to `-1` for BoostedKFold
    groups[boosted_minority_class_indices] = -1

    y_random_indices = np.where(groups != -1)[0]
    y_random = y[y_random_indices]

    cv = BoostedKFold(n_splits=n_splits, shuffle=True)
    splits = cv.split(X, y, groups)
    _cross_val_predict(X=X, y=y, y_test=y_random, splits=splits, cv=cv)

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True)
    splits = cv.split(X, y)
    _cross_val_predict(X=X, y=y, y_test=y, splits=splits, cv=cv)


def main():
    """"""
    test_boosted_kfold_unbalanced_dataset()

    test_boosted_kfold_with_custom_dataset()


if __name__ == '__main__':
    main()

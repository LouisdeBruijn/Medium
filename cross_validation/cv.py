from typing import Generator, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import KFold, PredefinedSplit, StratifiedKFold


def plot_evaluation(y: Sequence, y_predict: Sequence, title: str = "CV"):
    """Plots the classification report and the confusion matrix."""

    conf_matrix = confusion_matrix(y, y_predict)
    labels = np.unique(y)
    df_cm = pd.DataFrame(conf_matrix, index=[i for i in labels], columns=[i for i in labels])

    clf_report = classification_report(y, y_predict, output_dict=True)
    df_clf = pd.DataFrame(clf_report).iloc[:, :-3].T

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    fig.suptitle(title)

    hm1 = sns.heatmap(df_cm, annot=True, fmt="g", cmap="crest", ax=ax1)
    hm1.set(title="Confusion matrix", xlabel="Predicted", ylabel="True")

    # adjusts heatmap so that ``support`` column is white
    norm = plt.Normalize(vmin=df_clf.iloc[:-1, :-1].min().min(), vmax=df_clf.iloc[:, :-1].max().max())
    cmap = plt.get_cmap("crest")
    cmap.set_over("white")

    hm2 = sns.heatmap(
        data=df_clf.copy(),
        xticklabels=df_clf.columns,
        yticklabels=df_clf.index,
        annot=df_clf.round(2),
        cmap=cmap,
        ax=ax2,
        norm=norm,
        fmt=".5g",
    )
    hm2.set(title=f"Classification report, accuracy {round(accuracy_score(y, y_predict), 2)}")
    plt.show()


def _cross_val_predict(X: Sequence, y: Sequence, y_test: Sequence, splits: Generator, cv):
    """Custom ``cross_val_predict``.

    ``cross_validate`` and ``cross_val_score`` only returns scores, insufficient for confusion matrix
    ``cross_val_predict`` does what we need, but cannot take test-set that is different in size than y
        which is the case for our BoostedKFold() split
    """
    y_predictions = np.empty(len(y_test))
    for (training_indices, testing_indices) in splits:
        lr = LogisticRegression(fit_intercept=True)
        lr.fit(X[training_indices], y[training_indices])
        y_predict = lr.predict(X[testing_indices])

        for idx_pred, y_pred in zip(testing_indices, y_predict):
            y_predictions[idx_pred] = y_pred

    plot_evaluation(y_test, y_predictions, title=f"{type(cv).__name__} {cv.n_splits}-folds")


class BoostedKFold:
    def __init__(self, n_splits=5, shuffle=False, random_state=None):
        """
        Args:
            n_splits (int, default=5):
                Number of folds. Must be at least 2.
            shuffle (bool, default=False):
                Whether to shuffle each class's samples before splitting into batches.
                Note that the samples within each split will not be shuffled.
                This implementation can only shuffle groups that have approximately the
                same y distribution, no global shuffle will be performed.
            random_state (int or RandomState instance, default=None):
                When `shuffle` is True, `random_state` affects the ordering of the
                indices, which controls the randomness of each fold for each class.
                Otherwise, leave `random_state` as `None`.
                Pass an int for reproducible output across multiple function calls.
        """
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state

    def split(self, X: np.array, y: np.array, groups: Optional[np.array] = None):
        """Generate indices to split data into training and test set, excluding data in groups with value '-1'.

        boosted sample data == '-1' in the ``groups`` parameter
        random sample data != '-1' in the ``groups`` parameter

        Args:
            X (ndarray):
            y (ndarray):
            groups (ndarray): The groups '-1' for elements to be excluded

        Yields:
            train (ndarray): The training set indices for that split.
            test (ndarray): The testing set indices for that split.
        """
        # separate boosted sample data that have group ``-1``, from random sample data
        boosted_indices = np.where(groups == -1)[0]
        random_indices = np.where(groups != -1)[0]

        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=self.shuffle)
        # split the randomly sampled indices that are to be included in the test-set in ``n_splits`` splits
        stratified_random_splits = cv.split(X[random_indices], y[random_indices])

        random_sampled = [0] * len(random_indices)
        boosted_sampled = [-1] * len(boosted_indices)

        # converts the random stratified split test-set indices to the ``n_splits`` enumeration
        for split_nr, (_, testing_indices) in enumerate(stratified_random_splits):
            # defines which random sample datapoint is in which test-fold
            for test_idx in testing_indices:
                random_sampled[test_idx] = split_nr

        # concatenate the randomly sampled split numbers and the boosted sampling split numbers
        predefined_splits = random_sampled + boosted_sampled
        # boosted samples are not accounted for in the test-fold splits
        cv = PredefinedSplit(test_fold=predefined_splits)

        return cv.split(X)

    def plot(self, X: np.array, y: np.array, groups: np.array, splits: Sequence, ax, marker="_", lw=10):
        """Visualizes the CV split behavior."""
        cmap_samples = plt.cm.Spectral
        cmap_groups = plt.cm.Accent
        cmap_cv = plt.cm.coolwarm

        # iterate over the CV splits to visualise train/test data points per split
        for ii, (tr, tt) in enumerate(splits):
            # Fill in indices with the training/test groups
            indices = np.array([np.nan] * len(X))
            indices[tt] = 1
            indices[tr] = 0

            x_axis = [x + 0.5 for x in range(len(indices))]

            # Plot the cross validation split
            ax.scatter(
                x_axis,
                [ii + 0.5] * len(indices),
                c=indices,
                marker=marker,
                lw=lw,
                cmap=cmap_cv,
                vmin=-0.2,
                vmax=1.2,
            )

        x_axis = [x + 0.5 for x in range(len(X))]

        ax.scatter(  # plots the data classes
            x_axis, [self.n_splits + 0.5] * len(X), c=y, marker=marker, lw=lw, cmap=cmap_groups
        )

        ax.scatter(  # plots the data groups
            x_axis, [self.n_splits + 1.5] * len(X), c=groups, marker=marker, lw=lw, cmap=cmap_samples
        )

        # format the visualization
        yticklabels = list(range(self.n_splits)) + ["class", "group"]
        ax.set(
            yticks=np.arange(self.n_splits + 2) + 0.5,
            yticklabels=yticklabels,
            xlabel="Sample index",
            ylabel="CV iteration",
            ylim=[self.n_splits + 2.2, -0.2],
            xlim=[0, len(X)],
            xticks=x_axis,
            xticklabels=range(len(X)),
        )
        ax.set_title(f"{type(self).__name__}", fontsize=15)

        ax.legend(
            [
                Patch(color=cmap_cv(0.8)),
                Patch(color=cmap_cv(0.1)),
                Patch(color=cmap_groups(0.01)),
                Patch(color=cmap_groups(0.99)),
                Patch(color=cmap_samples(0.99)),
                Patch(color=cmap_samples(0.01)),
            ],
            ["Test", "Train", "0", "1", "Random", "Boosted"],
            loc=(1.02, 0.65),
        )

        return ax


def test_boosted_kfold():
    """"""

    n_splits = 3

    data = pd.read_csv("data/sample.csv", index_col="id")
    X = data[["feature_1", "feature_2"]].to_numpy()
    y = data[["label"]].to_numpy()
    groups = data[["sample"]].replace({"random": 0, "boosted": -1}, inplace=False).to_numpy()

    cv = BoostedKFold(n_splits=n_splits, shuffle=True)

    """
    splits = cv.split(X, y, groups)
    random_sample = data[data['sample'] == 'random']
    y_random = random_sample[['label']].to_numpy()
    _cross_val_predict(X=X, y=y, y_test=y_random, splits=splits, cv=cv)
    """

    splits = cv.split(X, y, groups)
    fig, ax = plt.subplots()
    cv.plot(X, y, groups, splits, ax, marker="o")
    plt.subplots_adjust(left=0.13, right=0.81)
    plt.show()


def main():
    """"""
    test_boosted_kfold()

    # ``flip_y`` has to be 0 for the actual class proportions ``weights`` to exactly match
    X, y = make_classification(n_samples=10000, n_features=4, n_classes=2, weights=[0.95, 0.05], flip_y=0)
    n_splits = 5

    groups = y.copy()
    boosted_n = round(0.8 * 0.05 * len(y))  # 80% of majority class (5%) of ``n_samples`` will be our boosted sampling
    boosted_ind = np.where(groups == 1)[0][:boosted_n]  # indices of boosted samples
    groups[boosted_ind] = -1  # replace indices of boosted samples value from ``1`` to ``-1`` for PredefinedSplit
    groups[groups == 1] = 0  # replace the randomly samples positive class values to ``0``

    y_random_indices = np.where(groups == 0)[0]
    y_random = y[y_random_indices]

    cv = BoostedKFold(n_splits=n_splits, shuffle=True)
    splits = cv.split(X, y, groups)
    _cross_val_predict(X=X, y=y, y_test=y_random, splits=splits, cv=cv)

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True)
    splits = cv.split(X, y)
    _cross_val_predict(X=X, y=y, y_test=y, splits=splits, cv=cv)

    cv = KFold(n_splits=n_splits, shuffle=True)
    splits = cv.split(X, y)
    _cross_val_predict(X=X, y=y, y_test=y, splits=splits, cv=cv)

    # model_ = (
    #     GridSearchCV(
    #         estimator=model_pipeline,
    #         param_grid=HYPERPARAMETERS,
    #         scoring=SCORING_METRIC,
    #         cv=cv,
    #         n_jobs=N_JOBS_HYPERPARAMETERS,
    #         verbose=VERBOSE,
    #         return_train_score=True)
    # ).fit(X=X, y=y['label'])


if __name__ == "__main__":
    main()

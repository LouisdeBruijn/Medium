from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from sklearn.model_selection import PredefinedSplit, StratifiedKFold


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

    def split(self, X: np.array, y: np.array, groups: np.array):
        """Generate indices to split data into training and test set, excluding data in groups with value '-1'.

        boosted sample data == '-1' in the ``groups`` parameter
        random sample data != '-1' in the ``groups`` parameter

        Args:
            X (ndarray): array-like of shape (n_samples, n_features)
                Training data, where `n_samples` is the number of samples and `n_features` is the number of features.
            y (ndarray): array-like of shape (n_samples,),
                The target variable for supervised learning problems.
            groups (ndarray): array-like of shape 1d: '-1' for elements to be excluded

        Yields:
            train (ndarray): The training set indices for that split.
            test (ndarray): The testing set indices for that split.
        """
        # separate boosted sample data that have group ``-1``, from random sample data
        boosted_indices = np.where(groups == -1)[0]
        random_indices = np.where(groups != -1)[0]

        skf = StratifiedKFold(n_splits=self.n_splits, shuffle=self.shuffle)
        # split the randomly sampled indices that are to be included in the test-set in ``n_splits`` splits
        stratified_random_splits = skf.split(X[random_indices], y[random_indices])

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
        ps = PredefinedSplit(test_fold=predefined_splits)

        return ps.split(X)

    def plot(self, X: np.array, y: np.array, groups: np.array, splits: Sequence, ax, marker='_', lw=10):
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

            # Plot the cross validation fold
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
        yticklabels = list(range(self.n_splits)) + ['class', 'group']
        ax.set(
            yticks=np.arange(self.n_splits + 2) + 0.5,
            yticklabels=yticklabels,
            xlabel='Sample index',
            ylabel='CV iteration',
            ylim=[self.n_splits + 2.2, -0.2],
            xlim=[0, len(X)],
            xticks=x_axis,
            xticklabels=range(len(X)),
        )
        ax.set_title(f'{type(self).__name__}', fontsize=15)

        ax.legend(
            [
                Patch(color=cmap_cv(0.8)),
                Patch(color=cmap_cv(0.1)),
                Patch(color=cmap_groups(0.01)),
                Patch(color=cmap_groups(0.99)),
                Patch(color=cmap_samples(0.99)),
                Patch(color=cmap_samples(0.01)),
            ],
            ['Test', 'Train', '0', '1', 'Random', 'Boosted'],
            loc=(1.02, 0.65),
        )

        return ax

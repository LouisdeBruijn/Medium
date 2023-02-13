from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix


def plot_evaluation(y: Sequence, y_predict: Sequence, title: str = 'CV', cmap: str = 'crest') -> None:
    """Plots the classification report and the confusion matrix."""
    labels = np.unique(y)

    conf_matrix = confusion_matrix(y, y_predict)
    df_cm = pd.DataFrame(conf_matrix, index=labels, columns=labels)

    clf_report = classification_report(y, y_predict, output_dict=True)
    df_clf = pd.DataFrame(clf_report).iloc[:, :-3].T

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle(title)

    hm1 = sns.heatmap(df_cm, annot=True, fmt='g', cmap=cmap, ax=ax1)
    hm1.set(title='Confusion matrix', xlabel='Predicted', ylabel='True')

    # adjusts the heatmap so that the `support` column is white,
    # otherwise the color gradient is skewed due to the high values in the `support` column
    norm = plt.Normalize(vmin=df_clf.iloc[:-1, :-1].min().min(), vmax=df_clf.iloc[:, :-1].max().max())
    cmap = plt.get_cmap(cmap)
    cmap.set_over('white')

    hm2 = sns.heatmap(
        data=df_clf.copy(),
        xticklabels=df_clf.columns,
        yticklabels=df_clf.index,
        annot=df_clf.round(2),
        cmap=cmap,
        ax=ax2,
        norm=norm,
        fmt='.5g',
    )
    hm2.set(title='Classification report')
    plt.show()

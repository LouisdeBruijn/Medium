import numpy as np
import seaborn as sns
from plot import plot_evaluation


def test_plot_evaluation():
    """"""
    y_predict = np.random.randint(2, size=1000)
    y_true = np.append(np.ones(300, dtype=int), np.zeros(700, dtype=int))

    plot_evaluation(y_true, y_predict, title='Beautiful evaluation metrics', cmap=sns.cubehelix_palette(as_cmap=True))


def main():
    """"""
    test_plot_evaluation()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3.6
# coding: utf-8

"""Création de zone tampon avec une décroissance sigmoïde."""


import numpy as np


def sigmoid(x, a, b):
    """Sigmod function.

    :param x: x values
    :param a: parameter a
    :param b: parameter b
    :return: y values.
    """
    return 1 / (1 + np.exp(a * x + b))


def zt_sigmoide(d, n):
    """Création de zone tampon avec un décroissance sigmoïde.

    :param d: distance totale (m).
    :param n: nombre de classe.
    :return: (limits, x values, y values)
    """
    lim = np.linspace(0, 1, n + 1, endpoint=True)  # limits
    x = np.array([lim[:-1], lim[1:]]).mean(axis=0)  # x
    y = sigmoid(x, a=12, b=-6)
    return lim * d, x * d, y


if __name__ == '__main__':

    # Exemple pour 10 classes sur une distance de 500 m
    n = 10
    d = 500

    import matplotlib.pyplot as plt
    plt.style.use('ggplot')

    lim, x, y = zt_sigmoide(d, n)

    for l1, l2, ey in zip(lim, lim[1:], y):
        plt.plot([l1, l2], [ey, ey], 'k')
    plt.plot(x, y, 'o')
    plt.show()


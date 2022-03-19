import numpy as np
from numpy.linalg import norm
from collections import namedtuple

Administration = namedtuple('Administration', ['demand', 'jacobi'])

class Government:
    def __init__(self, tax_rate, spending_rate, spending_distribution, balance):
        self._tax_rate = tax_rate
        self._spending_rate = spending_rate
        self._spending_distribution = spending_distribution / norm(spending_distribution)
        self._balance = balance

    def tax_income(self, income):
        taxes = income * self._tax_rate
        return (income - taxes, taxes)

    def govern(self, prices, tax_income):
        assert self._spending_distribution.shape == prices.shape
        money_to_spend = tax_income * self._spending_rate
        self._balance = self._balance + tax_income - money_to_spend
        spending_on_good = money_to_spend * self._spending_distribution
        demand = spending_on_good / prices
        return Administration(demand, np.zeros_like(prices))

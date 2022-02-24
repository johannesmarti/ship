import numpy as np
import scipy.optimize as so
from collections import namedtuple

def initial_consumption(num_goods):
    return np.full(num_goods, 0.01)

ConsumptionSolution = namedtuple('ConsumptionSolution', ['consumption', 'jacobi'])

def sqrt_utility(coefficients, consumption):
    return np.sum(np.sqrt(coefficients * consumption))

class SciPyConsumer:
    def __init__(self, utility, jacobi_factor = 0.01):
        self._utility = utility
        self._jacobi_factor = jacobi_factor

    def utility(self, consumption):
        return self._utility(consumption)

    def consume(self, prices, income_per_pop, init=None):
        num_goods = prices.size
    
        if init is None:
            init = initial_consumption(num_goods)

        def negative_utility(consumption):
            return -self.utility(consumption)
    
        bounds = [(0,None) for i in range(num_goods)]
        constraints = so.LinearConstraint(prices, lb=income_per_pop, ub=income_per_pop)
        res = so.minimize(negative_utility,
                          bounds=bounds,
                          constraints=constraints,
                          x0=init)
        return ConsumptionSolution(res.x, self._jacobi_factor * res.x)

class FlatConsumer:
    def __init__(self, coefficients):
        self._coefficients = coefficients

    def utility(self, consumption):
        return sqrt_utility(self._coefficients, consumption)

    def consume(self, prices, income_per_pop):
        assert prices.shape == self._coefficients.shape
        a = np.sum(self._coefficients / prices)
        # lambda can be interpreted as the price of 1 utility
        lambda_squared = income_per_pop / a
        solution_per_pop = lambda_squared * self._coefficients / (prices * prices)
        jacobi_diagonal = (-2) * solution_per_pop / prices
        return ConsumptionSolution(solution_per_pop, jacobi_diagonal)

    def supply_to_prices(self, income, supply):
        assert (income >= 0).all()
        assert (supply > 0).all()
        lbd = income / self.utility(supply)
        print("lbd", lbd)
        prices = lbd * np.sqrt(self._coefficients / supply)
        assert np.isclose(income, supply @ prices)
        return prices

SavingSolution = namedtuple('ConsumptionSolution', ['consumption', 'jacobi', 'savings'])

class SavingConsumer:
    def __init__(self, coefficients, utility_of_money):
        self._coefficients = np.append(coefficients, utility_of_money)

    def utility(self, consumption, savings):
        return sqrt_utility(self._coefficients,
                            np.append(consumption, savings))

    def consume(self, prices, income_per_pop):
        prices = np.append(prices, 1)
        assert prices.shape == self._coefficients.shape
        a = np.sum(self._coefficients / prices)
        # lambda can be interpreted as the price of 1 utility
        lambda_squared = income_per_pop / a
        solution_per_pop = lambda_squared * self._coefficients / (prices * prices)
        jacobi_diagonal = (-2) * solution_per_pop / prices
        return SavingSolution(solution_per_pop[:-1], jacobi_diagonal[:-1], solution_per_pop[-1])

class FixpointConsumer:
    def __init__(self, coefficients):
        self._coefficients = coefficients

    def utility(self, consumption):
        return sqrt_utility(self._coefficients, consumption)

    def consume(self, prices, income_per_pop, init_c=None):
        assert prices.shape == self._coefficients.shape
        num_goods = prices.shape[0]

        if init_c is None:
            init_c = initial_consumption(num_goods)

        def ut(c):
            util = np.sum(np.sqrt(self._coefficients * c))
            return util
    
        def comp_lbd(c):
            return (prices @ c) / ut(c)
    
        def comp_c(lbd):
            return lbd * lbd * self._coefficients / (prices * prices)

        def recalibrate(c):
            return c * (income_per_pop / (prices @ c))
    
        c = recalibrate(init_c)
        for i in range(2):
            lbd = comp_lbd(c)
            #print("lambda", lbd)
            c = recalibrate(comp_c(lbd))
    
        jacobi_diagonal = (-2) * c / prices
        return ConsumptionSolution(c, jacobi_diagonal)

def start_of_flat_slice(subst_groups):
    return sum(map(len, subst_groups))

GroupIndex = namedtuple('GroupIndex', ['substitution_coefficients', 'sl', 'i'])

def groups_with_slices(subst_groups):
    offset = 0
    i = 0
    for arr in subst_groups:
        end = offset + arr.size
        yield GroupIndex(arr,slice(offset, end),i)
        offset = end
        i += 1

# subst_coefficients is an list of arrays
def sqrt_subst_utility(coefficients, subst_groups, consumption):
    base_util = np.sum(np.sqrt(coefficients * consumption))

    def util_of_group(g):
        return np.sqrt(g.substitution_coefficients @ consumption[g.sl])

    group_utils = map(util_of_group, groups_with_slices(subst_groups))
    subst_util = sum(group_utils)
    return base_util + subst_util


def subst_ratio(coefficients, subst_coefficients, prices, init_c=None):
    num_substs = prices.size
    assert coefficients.size == num_substs
    assert subst_coefficients.size == num_substs

    if init_c is None:
        init_c = initial_consumption(num_substs)
        #print("initialize to", init_c)

    def ut(c):
        util = np.sum(np.sqrt(coefficients * c)) + np.sqrt(subst_coefficients @ c)
        return util

    def comp_delta(c):
        return (prices @ c) / ut(c)

    def comp_alpha(c):
        return 1 / np.sqrt(subst_coefficients @ c)

    def comp_c(alpha,delta):
        lower = prices - delta * alpha * subst_coefficients
        return delta * delta * coefficients / (lower * lower)

    c = init_c
    for i in range(3):
        alpha = comp_alpha(c)
        delta = comp_delta(c)
        c = comp_c(alpha,delta)

    c = c * (1000/(c@prices))
    return c


class SubstitutionConsumer:
    def __init__(self, coefficients, subst_groups):
        self._coefficients = coefficients
        self._subst_groups = subst_groups
        total_coeffs = coefficients.copy()
        for s_c, sl, _ in groups_with_slices(subst_groups):
            total_coeffs[sl] = total_coeffs[sl] + s_c
        self._total_coeffs = total_coeffs

    def utility(self, consumption):
        return sqrt_subst_utility(self._coefficients,
                                  self._subst_groups,
                                  consumption)

    def consume(self, prices, income_per_pop):
        start_flat = start_of_flat_slice(self._subst_groups)
        flat_prices = prices[start_flat:]
        flat_coefficients = self._coefficients[start_flat:]

        a = np.sum(flat_coefficients / flat_prices)
        def r(g):
            return subst_ratio(self._coefficients[g.sl], g.substitution_coefficients, prices[g.sl]) 
        ratios = list(map(r, groups_with_slices(self._subst_groups)))
            
        def al(g):
            return np.sum(np.sqrt(self._coefficients[g.sl] * ratios[g.i])) + np.sqrt(g.substitution_coefficients @ ratios[g.i])
        alphas = list(map(al, groups_with_slices(self._subst_groups)))

        def b(g):
            return alphas[g.i] * alphas[g.i] / (prices[g.sl] @ ratios[g.i])
        bs = map(b, groups_with_slices(self._subst_groups))

        # lambda can be interpreted as the price of 1 utility
        lambda_squared = income_per_pop / (sum(bs) + a)

        flat_solution = lambda_squared * flat_coefficients / (flat_prices * flat_prices)
        def c(g):
            r = lambda_squared * (alphas[g.i]/(prices[g.sl] @ ratios[g.i])) ** 2
            return r * ratios[g.i]

        solutions = list(map(c, groups_with_slices(self._subst_groups)))
        solutions.append(flat_solution)
        solution = np.concatenate(solutions)
    
        jacobi_diagonal = (-2) * (lambda_squared * self._total_coeffs /(prices * prices * prices))
    
        return ConsumptionSolution(solution, jacobi_diagonal)

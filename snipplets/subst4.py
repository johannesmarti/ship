import numpy as np

consumption = np.array([1,1,1,1,1,1,1,1,1,1,8,1,1,1,1,1,1,5,2,2,1,2,1,3])
coefficients = np.array([2,1,4,2,1,4,1,3,45,1,4,1,3,5,2,1,4,5,6,2,1,32,1,3])
subst_coefficients = [np.array([3,9,2]),
                      np.array([4,3]),
                      np.array([4,8,3]),
                      np.array([8,3,9,2,1]),
                      np.array([8,3])]


def groups_with_slices(subst_groups):
    offset = 0
    for arr in subst_groups:
        end = offset + arr.size
        yield (arr,slice(offset, end))
        offset = end

# subst_coefficients is an list of arrays
def sqrt_subst_utility(coefficients, subst_coefficients, consumption):
    base_util = np.sum(np.sqrt(coefficients * consumption))

    def util_of_group(arg):
        group = arg[0]
        sl = arg[1]
        return np.sqrt(group @ consumption[sl])

    group_utils = map(util_of_group, groups_with_slices(subst_coefficients))
    subst_util = sum(group_utils)

    return base_util + subst_util


print(sqrt_subst_utility(coefficients, subst_coefficients, consumption))

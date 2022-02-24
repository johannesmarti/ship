import numpy as np

matrix = np.array([
    [1,2,4],
    [0,1,-1],
    [2,0,-4],
    [3,-5,1]
])

prices = np.array([50,10,12])

print("considering the matrix\n" + np.array2string(matrix))
print("at prices", prices)
payoff_one_unit = matrix @ prices
print("leads to payoff per units", payoff_one_unit)
tasks_to_cancel = payoff_one_unit < 0
print("leads to cancel at", tasks_to_cancel)

matrix[tasks_to_cancel,] = 0
print("yeilds matrix\n" + np.array2string(matrix))

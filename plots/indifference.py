# importing the required modules
import matplotlib.pyplot as plt
import numpy as np
  
x = np.arange(1, 16, 0.1)

# sqrt(x) + sqrt(y) = c
# sqrt(y) = c - sqrt(x)
# y = (c - sqrt(x))^2

y1 = (np.maximum(1, 4 - np.sqrt(x)))**2
y2 = (np.maximum(1, 5 - np.sqrt(x)))**2
#y3 = (np.maximum(0, 6 - np.sqrt(x)))**2

# sqrt(x*z) = c
# x*z = c^2
# z = c^2 / x
z1 = (3.5)**2 / x
z2 = (4.2)**2 / x

  
# potting the points
plt.plot(x, y1)
plt.plot(x, y2)

plt.plot(x, z1)
plt.plot(x, z2)
# function to show the plot
plt.show()

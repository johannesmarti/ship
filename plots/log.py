# importing the required modules
import matplotlib.pyplot as plt
import numpy as np
  
x = np.arange(0, 2, 0.01)

y1 = np.log(x)
y2 = 1/2 * np.log(x)

  
# potting the points
plt.plot(x, y1)
plt.plot(x, y2)

# function to show the plot
plt.show()

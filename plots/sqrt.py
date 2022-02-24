# importing the required modules
import matplotlib.pyplot as plt
import numpy as np
  
x = np.arange(0, 1, 0.01)

#y1 = np.sqrt(x)
y2 = np.sqrt(x+(0.2*0.2)) - 0.2
#y3 = 10*np.sqrt(x/100)

  
# potting the points
#plt.plot(x, y1)
plt.plot(x, y2)
#plt.plot(x, y3)

# function to show the plot
plt.show()

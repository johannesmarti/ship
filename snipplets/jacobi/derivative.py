import numpy as np

def estimate_jacobian(f, point, epsilon):
    def partial_derivative(i):
        higher = np.copy(point)
        higher[i] = higher[i] + epsilon
        lower = np.copy(point)
        lower[i] = lower[i] - epsilon
        #print("\npartial derivative in", i, "at", point)
        #print("high", higher)
        #print("f high", f(higher))
        #print("low", lower)
        #print("f low", f(lower))
        #print("diff", f(higher) - f(lower))
        #print(2*epsilon)
        return (f(higher) - f(lower)) / (2*epsilon)
    #print("point", point)
    #print("point.shape", point.shape)
    #print(np.indices(point.shape)[0])
    return np.vectorize(partial_derivative, otypes=[np.float])(np.indices(point.shape)[0])

def print_estimation(f,x,epsilon):
    print("Jacobian at", x, "is", estimate_jacobian(f,x,epsilon), "for epsilon", epsilon)

def f(x):
    return 2.4 * x[0] * np.sqrt(x[0] * np.log(x[1]))

x = np.array([2.3,2.5])

#print_estimation(f,x,1)
#print_estimation(f,x,0.1)
#print_estimation(f,x,0.01)
#print_estimation(f,x,0.001)
#print_estimation(f,x,0.0001)
#print_estimation(f,x,0.00001)

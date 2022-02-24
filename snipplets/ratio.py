import numpy as np
import scipy.optimize as so

prices = np.array([10,20])

def f(x,p1,p2):
    if x == 0:
        x = 0.0000000001
    c1 = 1 / (p1 + x*p2)
    c2 = 1 / (p2 + p1/x)
    return (-1)*(np.sqrt(c1) + np.sqrt(c1 + c2) + np.sqrt(c2))

def g(x,p1,p2):
    if x == 0:
        x = 0.0000000001
    return (-1)*(1 + np.sqrt(1 + x) + np.sqrt(x))/np.sqrt(p1 + x*p2)

def ratio(p1,p2):
    #res = so.minimize_scalar(f,args=(p1,p2), method='brent')
    res = so.minimize_scalar(g,args=(p1,p2), bounds=(0.000001,10000), method='bounded')
    return res.x

def test(x):
    print(f(x,prices[0],prices[1]), "\t", x)


print(ratio(10,20))
print(1/ratio(10,20))

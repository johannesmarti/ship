import numpy as np

def f(a):
    print(a)
    return 4.34*a

print("vectorizing f")
fv = np.vectorize(f, otypes=[np.float])

print("mapping the f over an array")
ret = fv(np.array([1,2,3,7,5,3]))
print(ret)

print("mapping the f over indices")
print(np.indices((3,))[0])
ret = fv(np.indices((3,))[0])
print(ret)
print(ret.dtype)

print(ret.shape)
print(np.indices(ret.shape))


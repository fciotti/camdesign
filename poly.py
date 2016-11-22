import argparse
import numpy as np
from math import factorial
import matplotlib.pyplot as plt


# k-th derivative of x^n
def der(x, n, k):
    if k > n:
        return 0
    return factorial(n)/factorial(n-k)*x**(n-k)

parser = argparse.ArgumentParser(description='camdesign')
parser.add_argument('positions', help='path of positions'' file')
parser.add_argument('-n')
parser.add_argument('-o', type=int, help='matching O derivatives')
parser.add_argument('--radius', '-r')

args = parser.parse_args()

positions = list(map(int, open(args.positions).readlines()))

a = len(positions) + 1
d = a + args.o

# Vandermonde matrix
A = np.zeros((d, d))

B = np.zeros(d)

for row in range(0, a-1):
    B[row] = positions[row]
    for col in range(0, d):
        A[row, col] = (row/a)**col

# Match initial and final position
B[a-1] = B[0]
for col in range(0, d):
    A[a-1, col] = 1

# Match derivatives
for row in range(a, d):
    B[row] = 0
    for col in range(0, d):
        A[row, col] = der(1, col, row-a+1) - der(0, col, row-a+1)

c = np.linalg.solve(A, B)

print(A, '\n\n', B, '\n\n', c)

x = np.linspace(0, 1, num=200)
y = np.polyval(c[::-1], x)

print(x, y)
plt.plot(x, y)
plt.plot(np.linspace(0, 1*len(positions)/(len(positions)+1), num=len(positions)), positions)
plt.show()

import argparse
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import csv

# k-th derivative of x^n
def der(x,n,k):
    if(k > n): return 0
    return factorial(n)/factorial(n-k)*x**(n-k)

parser = argparse.ArgumentParser(description='camdesign')
parser.add_argument('positions', help='path of positions'' file')
parser.add_argument('-n', type=int, default=1)
parser.add_argument('--radius', '-r')

args = parser.parse_args()

n = args.n

with open("args.positions") as file:
    columns = zip(*[line for line in csv.reader(file, dialect="excel-tab")])
    positions = c

lines = open(args.positions).readlines()
positions = list(map(int, lines))
positions.append(positions[0])

xp = np.linspace(0,1,num=len(positions))

tck = interpolate.splrep(xp,positions,per=1)

step = 100

x1 = np.linspace(0,1,num=step)
y1 = interpolate.splev(x1,tck)

x = np.linspace(0,n,num=step*n)
y = np.tile(y1,n)
print(len(x),len(y))

plt.plot(x,y)
plt.plot(xp,positions)
plt.show()

import numpy as np
import pylab
import random

# define the number of steps
n = 100000

# creating two array for containing x and y coordinate
# of size equals to number of size and filled up with 0's
x = np.zeros(n)
y = np.zeros(n)

# filing the coordinates with variables
for i in range(1,n):
    val = random.randint(1,4)
    if val == 1:                          ## 向右边走
        x[i] = x[i - 1] + 1
        y[i] = y[i -1]
    elif val == 2:                       ## 向左走
        x[i] = x[i - 1] - 1
        y[i] = y[i -1]
    elif val == 3:                       ## 向上走
        x[i] = x[i - 1]
        y[i] = y[i - 1] + 1
    else:                                 ## 向下走
        x[i] = x[i - 1]
        y[i] = y[i -1] - 1

## plotting stuff:
pylab.title("Random Walk ($ n = " + str(n) + "$ steps)")
pylab.plot(x,y)
pylab.savefig("rand_walk" + str(n) + ".png",bbox_inches="tight",dpi=600)
pylab.show()

## In computer networks, random walks can model the number of transmission packets buffered at a server.
## In population genetics, random walk describes the statistical properties of genetic drift.
## In image segmentation, random walks are used to determine the labels (i.e., “object” or “background”) to associate with each pixel.
## In brain research, random walks and reinforced random walks are used to model cascades of neuron firing in the brain.
## Random walks have also been used to sample massive online graphs such as online social networks

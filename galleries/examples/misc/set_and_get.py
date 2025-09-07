





import matplotlib.pyplot as plt

import numpy as np



x = np.arange(0, 1.0, 0.01)

y1 = np.sin(2*np.pi*x)

y2 = np.sin(4*np.pi*x)

lines = plt.plot(x, y1, x, y2)

l1, l2 = lines

plt.setp(lines, linestyle='--')                           

plt.setp(l1, linewidth=2, color='r')                          

plt.setp(l2, linewidth=1, color='g')                              





print('Line setters')

plt.setp(l1)

print('Line getters')

plt.getp(l1)



print('Rectangle setters')

plt.setp(plt.gca().patch)

print('Rectangle getters')

plt.getp(plt.gca().patch)



t = plt.title('Hi mom')

print('Text setters')

plt.setp(t)

print('Text getters')

plt.getp(t)



plt.show()


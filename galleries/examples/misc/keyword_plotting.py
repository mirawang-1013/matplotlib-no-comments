



import matplotlib.pyplot as plt

import numpy as np



np.random.seed(19680801)



data = {'a': np.arange(50),

        'c': np.random.randint(0, 50, 50),

        'd': np.random.randn(50)}

data['b'] = data['a'] + 10 * np.random.randn(50)

data['d'] = np.abs(data['d']) * 100



fig, ax = plt.subplots()

ax.scatter('a', 'b', c='c', s='d', data=data)

ax.set(xlabel='entry a', ylabel='entry b')

plt.show()


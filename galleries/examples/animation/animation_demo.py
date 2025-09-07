



import matplotlib.pyplot as plt

import numpy as np



np.random.seed(19680801)

data = np.random.random((50, 50, 50))



fig, ax = plt.subplots()



for i, img in enumerate(data):

    ax.clear()

    ax.imshow(img)

    ax.set_title(f"frame {i}")

                                                      

    plt.pause(0.1)


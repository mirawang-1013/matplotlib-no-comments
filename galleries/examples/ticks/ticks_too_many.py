



    

                                                                    

                                                                    



import matplotlib.pyplot as plt

import numpy as np



fig, ax = plt.subplots(1, 2, layout='constrained', figsize=(6, 2.5))

x = ['1', '5', '2', '3']

y = [1, 4, 2, 3]

ax[0].plot(x, y, 'd')

ax[0].tick_params(axis='x', color='r', labelcolor='r')

ax[0].set_xlabel('Categories')

ax[0].set_title('Ticks seem out of order / misplaced')



                     

x = np.asarray(x, dtype='float')

ax[1].plot(x, y, 'd')

ax[1].set_xlabel('Floats')

ax[1].set_title('Ticks as expected')



    

                                                

                                                

                                                                           

                                                                    



fig, ax = plt.subplots(1, 2, figsize=(6, 2.5))

x = [f'{xx}' for xx in np.arange(100)]

y = np.arange(100)

ax[0].plot(x, y)

ax[0].tick_params(axis='x', color='r', labelcolor='r')

ax[0].set_title('Too many ticks')

ax[0].set_xlabel('Categories')



ax[1].plot(np.asarray(x, float), y)

ax[1].set_title('x converted to numbers')

ax[1].set_xlabel('Floats')



    

                                                                      

                                                                      

                                                                       

                                                                            

                 



fig, ax = plt.subplots(1, 2, layout='constrained', figsize=(6, 2.75))

x = ['2021-10-01', '2021-11-02', '2021-12-03', '2021-09-01']

y = [0, 2, 3, 1]

ax[0].plot(x, y, 'd')

ax[0].tick_params(axis='x', labelrotation=90, color='r', labelcolor='r')

ax[0].set_title('Dates out of order')



                       

x = np.asarray(x, dtype='datetime64[s]')

ax[1].plot(x, y, 'd')

ax[1].tick_params(axis='x', labelrotation=90)

ax[1].set_title('x converted to datetimes')



plt.show()




import matplotlib.pyplot as plt



plt.plot(range(10))



plt.title('Center Title')

plt.title('Left Title', loc='left')

plt.title('Right Title', loc='right')



plt.show()



    

                                                                    

                                                



fig, axs = plt.subplots(1, 2, layout='constrained')



ax = axs[0]

ax.plot(range(10))

ax.xaxis.set_label_position('top')

ax.set_xlabel('X-label')

ax.set_title('Center Title')



ax = axs[1]

ax.plot(range(10))

ax.xaxis.set_label_position('top')

ax.xaxis.tick_top()

ax.set_xlabel('X-label')

ax.set_title('Center Title')

plt.show()



    

                                                                        

                                                                              



fig, axs = plt.subplots(1, 2, layout='constrained')



ax = axs[0]

ax.plot(range(10))

ax.xaxis.set_label_position('top')

ax.set_xlabel('X-label')

ax.set_title('Manual y', y=1.0, pad=-14)



plt.rcParams['axes.titley'] = 1.0                                        

plt.rcParams['axes.titlepad'] = -14                       

ax = axs[1]

ax.plot(range(10))

ax.set_xlabel('X-label')

ax.set_title('rcParam y')



plt.show()


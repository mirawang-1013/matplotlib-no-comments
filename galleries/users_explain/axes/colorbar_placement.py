

import matplotlib.pyplot as plt

import numpy as np



                                         

np.random.seed(19680801)



fig, axs = plt.subplots(2, 2)

cmaps = ['RdBu_r', 'viridis']

for col in range(2):

    for row in range(2):

        ax = axs[row, col]

        pcm = ax.pcolormesh(np.random.random((20, 20)) * (col + 1),

                            cmap=cmaps[col])

        fig.colorbar(pcm, ax=ax)



    

                                                                       

                                                                               

                                     



fig, axs = plt.subplots(2, 2)

cmaps = ['RdBu_r', 'viridis']

for col in range(2):

    for row in range(2):

        ax = axs[row, col]

        pcm = ax.pcolormesh(np.random.random((20, 20)) * (col + 1),

                            cmap=cmaps[col])

    fig.colorbar(pcm, ax=axs[:, col], shrink=0.6)



    

                                                              

                                                            

                                                                    



fig, axs = plt.subplots(2, 1, figsize=(4, 5), sharex=True)

X = np.random.randn(20, 20)

axs[0].plot(np.sum(X, axis=0))

pcm = axs[1].pcolormesh(X)

fig.colorbar(pcm, ax=axs[1], shrink=0.6)



    

                                                                           

                                                                              

                                                                                



fig, axs = plt.subplots(2, 1, figsize=(4, 5), sharex=True, layout='constrained')

axs[0].plot(np.sum(X, axis=0))

pcm = axs[1].pcolormesh(X)

fig.colorbar(pcm, ax=axs[1], shrink=0.6)



    

                                                                 

                                                         

                          



fig, axs = plt.subplots(3, 3, layout='constrained')

for ax in axs.flat:

    pcm = ax.pcolormesh(np.random.random((20, 20)))



fig.colorbar(pcm, ax=axs[0, :2], shrink=0.6, location='bottom')

fig.colorbar(pcm, ax=[axs[0, 2]], location='bottom')

fig.colorbar(pcm, ax=axs[1:, :], location='right', shrink=0.6)

fig.colorbar(pcm, ax=[axs[2, 1]], location='left')



    

                                                         

                                                         

 

                                                                          

                                                                          

                                                                              

        



fig, axs = plt.subplots(3, 1, layout='constrained', figsize=(5, 5))

for ax, pad in zip(axs, [0.025, 0.05, 0.1]):

    pcm = ax.pcolormesh(np.random.randn(20, 20), cmap='viridis')

    fig.colorbar(pcm, ax=ax, pad=pad, label=f'pad: {pad}')

fig.suptitle("layout='constrained'")



    

                                                                           

                     



fig, axs = plt.subplots(3, 1, figsize=(5, 5))

for ax, pad in zip(axs, [0.025, 0.05, 0.1]):

    pcm = ax.pcolormesh(np.random.randn(20, 20), cmap='viridis')

    fig.colorbar(pcm, ax=ax, pad=pad, label=f'pad: {pad}')

fig.suptitle("No layout manager")



    

                               

                               

 

                                                                     

                                                                   

                                                                        

           

 

                      

                      

 

                                                                         

                                                                               

                                                                             

                                



fig, ax = plt.subplots(layout='constrained', figsize=(4, 4))

pcm = ax.pcolormesh(np.random.randn(20, 20), cmap='viridis')

ax.set_ylim([-4, 20])

cax = ax.inset_axes([0.3, 0.07, 0.4, 0.04])

fig.colorbar(pcm, cax=cax, orientation='horizontal')



    

                                                                      

                                                                   

                                     



fig, ax = plt.subplots(layout='constrained', figsize=(4, 4))

pcm = ax.pcolormesh(np.random.randn(20, 20), cmap='viridis')

ax.set_ylim([-4, 20])

cax = ax.inset_axes([7.5, -1.7, 5, 1.2], transform=ax.transData)

fig.colorbar(pcm, cax=cax, orientation='horizontal')



    

                                               

                                               

 

                                                                            

                                                                               

                                                                     



fig, ax = plt.subplots(layout='constrained', figsize=(4, 4))

pcm = ax.imshow(np.random.randn(10, 10), cmap='viridis')

fig.colorbar(pcm, ax=ax)



    

                                                                            

                                                                            

                                                                           

                                        



fig, ax = plt.subplots(layout='compressed', figsize=(4, 4))

pcm = ax.imshow(np.random.randn(10, 10), cmap='viridis')

ax.set_title("Colorbar with layout='compressed'", fontsize='medium')

fig.colorbar(pcm, ax=ax)



    

                                                                               

                                                                             

                                                                          

                                                              



fig, ax = plt.subplots(layout='constrained', figsize=(4, 4))

pcm = ax.imshow(np.random.randn(10, 10), cmap='viridis')

cax = ax.inset_axes([1.04, 0.0, 0.05, 1.0])                            

ax.set_title('Colorbar with inset_axes', fontsize='medium')

fig.colorbar(pcm, cax=cax)



    

                                                                              

                                                                             

                                                                               



fig, ax = plt.subplots(layout='constrained', figsize=(4, 4))

pcm = ax.imshow(np.random.randn(10, 10), cmap='viridis')

cax = ax.inset_axes([1.04, 0.0, 0.05, 1.0])

ax.set_title('Colorbar with inset_axes', fontsize='medium')

fig.colorbar(pcm, cax=cax)



    

              

 

                                                                            

 

                                            

                                           


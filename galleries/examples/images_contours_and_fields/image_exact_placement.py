



                                      



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.patches as mpatches



                

N = 450

x = np.arange(N) / N

y = np.arange(N) / N



X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2)

f0 = 5

k = 100

a = np.sin(np.pi * 2 * (f0 * R + k * R**2 / 2))

A = a[:100, :300]

B = A[:40, :200]



                                              

fig, axs = plt.subplots(1, 2, facecolor='aliceblue')



axs[0].imshow(A, vmin=-1, vmax=1)

axs[1].imshow(B, vmin=-1, vmax=1)





def annotate_rect(ax):

                                                      

    rect = mpatches.Rectangle((0, 0), 200, 40, linewidth=1,

                              edgecolor='r', facecolor='none')

    ax.add_patch(rect)

    return rect



annotate_rect(axs[0])



    

                                                                               

                                                                      

 

                                                                                   

                                                                                    

                                                                           

                                                                                     

                                                                           

 

                                                                                     

                                                                                     

                                                                                 

                                                                           



fig, axs = plt.subplots(1, 2, width_ratios=[300/200, 1],

                        figsize=(6.4, 2), facecolor='aliceblue')



axs[0].imshow(A, vmin=-1, vmax=1)

annotate_rect(axs[0])



axs[1].imshow(B, vmin=-1, vmax=1)

    

                                                                         

                                                                                        

                                                                             

             



fig, axs = plt.subplots(1, 2, width_ratios=[300/200, 1],

                        figsize=(6.4, 2), facecolor='aliceblue')



axs[0].imshow(A, vmin=-1, vmax=1)

annotate_rect(axs[0])



axs[0].set_anchor('NW')

axs[1].imshow(B, vmin=-1, vmax=1)

axs[1].set_anchor('NW')



    

                    

                    

                                                                         

                                                                    

                                                                  

                                                                     

 

                                                                              

                                                                            

                                          

                                                                       

                                                                       

                                          



dpi = 100                          



                                        

buffer = 0.35 * dpi          



                            

left = buffer

bottom = buffer

ny, nx = np.shape(A)

posA = [left, bottom, nx, ny]

                                                                           

fig_height = bottom + ny + buffer



                                             

left = left + nx + buffer



ny, nx = np.shape(B)

                                                                       

bottom = fig_height - buffer - ny

posB = [left, bottom, nx, ny]



                                          

fig_width = left + nx + buffer



                            

fig = plt.figure(figsize=(fig_width / dpi, fig_height / dpi), facecolor='aliceblue')



                                                                      

ax = fig.add_axes((posA[0] / fig_width, posA[1] / fig_height,

                   posA[2] / fig_width, posA[3] / fig_height))

ax.imshow(A, vmin=-1, vmax=1)

annotate_rect(ax)



ax = fig.add_axes((posB[0] / fig_width, posB[1] / fig_height,

                   posB[2] / fig_width, posB[3] / fig_height))

ax.imshow(B, vmin=-1, vmax=1)

plt.show()

    

                                                                              

                                                                          

                                                                              

                                                  

 

                            

 

                                                                              

                     

 

                                    

                                          

 

           

 

                      

                    

                      

                     






import matplotlib.pyplot as plt

                                     

import numpy as np



from matplotlib.colors import Normalize





def normal_pdf(x, mean, var):

    return np.exp(-(x - mean)**2 / (2*var))





                                                 

xmin, xmax, ymin, ymax = (0, 100, 0, 100)

n_bins = 100

xx = np.linspace(xmin, xmax, n_bins)

yy = np.linspace(ymin, ymax, n_bins)



                                                                        

means_high = [20, 50]

means_low = [50, 60]

var = [150, 200]



gauss_x_high = normal_pdf(xx, means_high[0], var[0])

gauss_y_high = normal_pdf(yy, means_high[1], var[0])



gauss_x_low = normal_pdf(xx, means_low[0], var[1])

gauss_y_low = normal_pdf(yy, means_low[1], var[1])



weights = (np.outer(gauss_y_high, gauss_x_high)

           - np.outer(gauss_y_low, gauss_x_low))



                                                                     

greys = np.full((*weights.shape, 3), 70, dtype=np.uint8)



                                                                     

vmax = np.abs(weights).max()

imshow_kwargs = {

    'vmax': vmax,

    'vmin': -vmax,

    'cmap': 'RdYlBu',

    'extent': (xmin, xmax, ymin, ymax),

}



fig, ax = plt.subplots()

ax.imshow(greys)

ax.imshow(weights, **imshow_kwargs)

ax.set_axis_off()



    

                          

                          

 

                                                                  

                                                                      

                                                                          

                                  



                                                                            

alphas = np.ones(weights.shape)

alphas[:, 30:] = np.linspace(1, 0, 70)



                             

                                                         

fig, ax = plt.subplots()

ax.imshow(greys)

ax.imshow(weights, alpha=alphas, **imshow_kwargs)

ax.set_axis_off()



    

                                                            

                                                            

 

                                                                             

                                                                              

                                                                       

                             



                                                

                                                                       

alphas = Normalize(0, .3, clip=True)(np.abs(weights))

alphas = np.clip(alphas, .4, 1)                                           



                             

                                                         

fig, ax = plt.subplots()

ax.imshow(greys)

ax.imshow(weights, alpha=alphas, **imshow_kwargs)



                                                          

ax.contour(weights[::-1], levels=[-.1, .1], colors='k', linestyles='-')

ax.set_axis_off()

plt.show()



ax.contour(weights[::-1], levels=[-.0001, .0001], colors='k', linestyles='-')

ax.set_axis_off()

plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                 

                                                                   

                                    

                                          


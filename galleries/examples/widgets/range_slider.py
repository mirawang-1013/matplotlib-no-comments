



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.widgets import RangeSlider



                       

np.random.seed(19680801)

N = 128

img = np.random.randn(N, N)



fig, axs = plt.subplots(1, 2, figsize=(10, 5))

fig.subplots_adjust(bottom=0.25)



im = axs[0].imshow(img)

axs[1].hist(img.flatten(), bins='auto')

axs[1].set_title('Histogram of pixel intensities')



                        

slider_ax = fig.add_axes((0.20, 0.1, 0.60, 0.03))

slider = RangeSlider(slider_ax, "Threshold", img.min(), img.max())



                                            

lower_limit_line = axs[1].axvline(slider.val[0], color='k')

upper_limit_line = axs[1].axvline(slider.val[1], color='k')





def update(val):

                                                          

                              



                                 

    im.norm.vmin = val[0]

    im.norm.vmax = val[1]



                                               

    lower_limit_line.set_xdata([val[0], val[0]])

    upper_limit_line.set_xdata([val[1], val[1]])



                                            

    fig.canvas.draw_idle()





slider.on_changed(update)

plt.show()



    

 

                            

 

                                                                              

                     

 

                                       


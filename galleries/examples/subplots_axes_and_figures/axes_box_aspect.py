



    

                                    

                                    

 

                                                            



import matplotlib.pyplot as plt

import numpy as np



fig1, ax = plt.subplots()



ax.set_xlim(300, 400)

ax.set_box_aspect(1)



plt.show()



    

                    

                    

 

                                                   

 

fig2, (ax, ax2) = plt.subplots(ncols=2, sharey=True)



ax.plot([1, 5], [0, 10])

ax2.plot([100, 500], [10, 15])



ax.set_box_aspect(1)

ax2.set_box_aspect(1)



plt.show()



    

                  

                  

 

                                                                          

                           

 



fig3, ax = plt.subplots()



ax2 = ax.twinx()



ax.plot([0, 10])

ax2.plot([12, 10])



ax.set_box_aspect(1)



plt.show()





    

                           

                           

 

                                                                    

                                                                          

                                                                               

                                                                         

 

                                                                          

                     



fig4, (ax, ax2) = plt.subplots(ncols=2, layout="constrained")



np.random.seed(19680801)                                           

im = np.random.rand(16, 27)

ax.imshow(im)



ax2.plot([23, 45])

ax2.set_box_aspect(im.shape[0]/im.shape[1])



plt.show()



    

                            

                            

 

                                                                            

                                                                      

                                                                            

                                                                            

         



fig5, axs = plt.subplots(2, 2, sharex="col", sharey="row",

                         gridspec_kw=dict(height_ratios=[1, 3],

                                          width_ratios=[3, 1]))

axs[0, 1].set_visible(False)

axs[0, 0].set_box_aspect(1/3)

axs[1, 0].set_box_aspect(1)

axs[1, 1].set_box_aspect(3/1)



np.random.seed(19680801)                                           

x, y = np.random.randn(2, 400) * [[.5], [180]]

axs[1, 0].scatter(x, y)

axs[0, 0].hist(x)

axs[1, 1].hist(y, orientation="horizontal")



plt.show()



    

                                 

                                 

 

                                                                         

                                                                       

                                                                   

                 



fig6, ax = plt.subplots()



ax.add_patch(plt.Circle((5, 3), 1))

ax.set_aspect("equal", adjustable="datalim")

ax.set_box_aspect(0.5)

ax.autoscale()



plt.show()



    

                              

                              

 

                                                                         

                                                               



fig7, axs = plt.subplots(2, 3, subplot_kw=dict(box_aspect=1),

                         sharex=True, sharey=True, layout="constrained")



for i, ax in enumerate(axs.flat):

    ax.scatter(i % 3, -((i // 3) - 0.5)*200, c=[plt.colormaps["hsv"](i / 6)], s=300)

plt.show()



    

 

                            

 

                                                                              

                     

 

                                            

 

           

 

                    

                  

                    


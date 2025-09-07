



    

                                                            

                                                                            

                                                                         

                                            

                                                               

                                           



import matplotlib.pyplot as plt



from mpl_toolkits.axes_grid1.inset_locator import inset_axes



fig, (ax, ax2) = plt.subplots(1, 2, figsize=[5.5, 2.8])



                                                        

                                      

axins = inset_axes(ax, width=1.3, height=0.9)



                                                                           

                           

axins2 = inset_axes(ax, width="30%", height="40%", loc="lower left")



                                                             

                                               

                                            

axins3 = inset_axes(ax2, width="30%", height=1., loc="upper left")



                                                                  

                                                                         

axins4 = inset_axes(ax2, width="20%", height="20%", loc="lower right", borderpad=1)



                               

for axi in [axins, axins2, axins3, axins4]:

    axi.tick_params(labelleft=False, labelbottom=False)



plt.show()





    

                                                                             

                                                                           

                                              

                                                                            

                   

 



fig = plt.figure(figsize=[5.5, 2.8])

ax = fig.add_subplot(121)



                                                                          

                                                                            

                                                 

                                                                             

                       

                                                                       

                                                                              

                                                                       

                                                                        



axins = inset_axes(ax, width="50%", height="75%",

                   bbox_to_anchor=(.2, .4, .6, .5),

                   bbox_transform=ax.transAxes, loc="lower left")



                                                                    

ax.add_patch(plt.Rectangle((.2, .4), .6, .5, ls="--", ec="c", fc="none",

                           transform=ax.transAxes))



                                                                             

                                                             

ax.set(xlim=(0, 10), ylim=(0, 10))





                                                                             

                                                                       

                                           

ax2 = fig.add_subplot(222)

axins2 = inset_axes(ax2, width="30%", height="50%")



ax3 = fig.add_subplot(224)

axins3 = inset_axes(ax3, width="100%", height="100%",

                    bbox_to_anchor=(.7, .5, .3, .5),

                    bbox_transform=ax3.transAxes)



                                                                    

ax2.add_patch(plt.Rectangle((0, 0), 1, 1, ls="--", lw=2, ec="c", fc="none"))

ax3.add_patch(plt.Rectangle((.7, .5), .3, .5, ls="--", lw=2,

                            ec="c", fc="none"))



                     

for axi in [axins2, axins3, ax2, ax3]:

    axi.tick_params(labelleft=False, labelbottom=False)



plt.show()





    

                                                                               

                                                                            

                                                                           

                                 

 



fig = plt.figure(figsize=[5.5, 2.8])

ax = fig.add_subplot(131)



                                  

axins = inset_axes(ax, width="100%", height="100%",

                   bbox_to_anchor=(1.05, .6, .5, .4),

                   bbox_transform=ax.transAxes, loc="upper left", borderpad=0)

axins.tick_params(left=False, right=True, labelleft=False, labelright=True)



                                                                       

                                                                  

                                              

axins2 = inset_axes(ax, width=0.5, height=0.4,

                    bbox_to_anchor=(0.33, 0.25),

                    bbox_transform=ax.transAxes, loc="lower left", borderpad=0)





ax2 = fig.add_subplot(133)

ax2.set_xscale("log")

ax2.set(xlim=(1e-6, 1e6), ylim=(-2, 6))



                                                                  

axins3 = inset_axes(ax2, width="100%", height="100%",

                    bbox_to_anchor=(1e-2, 2, 1e3, 3),

                    bbox_transform=ax2.transData, loc="upper left", borderpad=0)



                                                                            

                                 

from matplotlib.transforms import blended_transform_factory        



transform = blended_transform_factory(fig.transFigure, ax2.transAxes)

axins4 = inset_axes(ax2, width="16%", height="34%",

                    bbox_to_anchor=(0, 0, 1, 1),

                    bbox_transform=transform, loc="lower center", borderpad=0)



plt.show()


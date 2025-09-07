



import matplotlib.pyplot as plt



from matplotlib.transforms import ScaledTranslation



    

fig, axs = plt.subplot_mosaic([['a)', 'c)'], ['b)', 'c)'], ['d)', 'd)']],

                              layout='constrained')

for label, ax in axs.items():

                                        

                                                      

                                                             

                                       

                                

    ax.annotate(

        label,

        xy=(0, 1), xycoords='axes fraction',

        xytext=(+0.5, -0.5), textcoords='offset fontsize',

        fontsize='medium', verticalalignment='top', fontfamily='serif',

        bbox=dict(facecolor='0.7', edgecolor='none', pad=3.0))



    

fig, axs = plt.subplot_mosaic([['a)', 'c)'], ['b)', 'c)'], ['d)', 'd)']],

                              layout='constrained')

for label, ax in axs.items():

                                            

                                                      

                                                                        

                                 

    ax.text(

        0.0, 1.0, label, transform=(

            ax.transAxes + ScaledTranslation(-20/72, +7/72, fig.dpi_scale_trans)),

        fontsize='medium', va='bottom', fontfamily='serif')



    

                                                                          

                                 



fig, axs = plt.subplot_mosaic([['a)', 'c)'], ['b)', 'c)'], ['d)', 'd)']],

                              layout='constrained')

for label, ax in axs.items():

    ax.set_title('Normal Title', fontstyle='italic')

    ax.set_title(label, fontfamily='serif', loc='left', fontsize='medium')



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                  

                                         

                                       

                                      


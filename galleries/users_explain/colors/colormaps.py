



                                     



from colorspacious import cspace_converter



import matplotlib.pyplot as plt

import numpy as np



import matplotlib as mpl



    

 

                                                                   

                                       



cmaps = {}



gradient = np.linspace(0, 1, 256)

gradient = np.vstack((gradient, gradient))





def plot_color_gradients(category, cmap_list):

                                                                   

    nrows = len(cmap_list)

    figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22

    fig, axs = plt.subplots(nrows=nrows + 1, figsize=(6.4, figh))

    fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,

                        left=0.2, right=0.99)

    axs[0].set_title(f'{category} colormaps', fontsize=14)



    for ax, name in zip(axs, cmap_list):

        ax.imshow(gradient, aspect='auto', cmap=mpl.colormaps[name])

        ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,

                transform=ax.transAxes)



                                                                      

    for ax in axs:

        ax.set_axis_off()



                                   

    cmaps[category] = cmap_list





    

            

            

 

                                                                               

                                                                              

                                                                              

                                                                                 

                                                                                 

                                                                                

                  



plot_color_gradients('Perceptually Uniform Sequential',

                     ['viridis', 'plasma', 'inferno', 'magma', 'cividis'])



    



plot_color_gradients('Sequential',

                     ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',

                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',

                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'])



    

             

             

 

                                                                             

                                                                                 

                                                                               

                                                                              

                                                                                  

                                                                                 

                                



plot_color_gradients('Sequential (2)',

                     ['binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',

                      'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',

                      'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper'])



    

           

           

 

                                                                              

                                                                               

                                                                               

                                                                             

                                                                             

                                                                                

 

                                                                             

                                                                            

                                                       



plot_color_gradients('Diverging',

                     ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',

                      'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',

                      'berlin', 'managua', 'vanimo'])



    

        

        

 

                                                                         

                                                                               

                                                                                

                                                                                

                                                                         

                                                                         

                                           

 

                                                                               

                                                                               

                                                                               

                                                                   

                 



plot_color_gradients('Cyclic', ['twilight', 'twilight_shifted', 'hsv'])



    

             

             

 

                                                                                  

                                                                                  

                                                                                  

                                                                  



plot_color_gradients('Qualitative',

                     ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',

                      'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',

                      'tab20c'])



    

               

               

 

                                                                    

                                                                     

                                                                        

                                                                      

                                                                  

                                                               

                                                              

                                                                        

                                                                        

                                                  

 

                                                                              

                                                                              

                                                                           

                                                        





plot_color_gradients('Miscellaneous',

                     ['flag', 'prism', 'ocean', 'gist_earth', 'terrain',

                      'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',

                      'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',

                      'turbo', 'nipy_spectral', 'gist_ncar'])



plt.show()



    

                                   

                                   

 

                                                                   

                                                            

                      



mpl.rcParams.update({'font.size': 12})



                                                               

_DSUBS = {'Perceptually Uniform Sequential': 5, 'Sequential': 6,

          'Sequential (2)': 6, 'Diverging': 6, 'Cyclic': 3,

          'Qualitative': 4, 'Miscellaneous': 6}



                                            

_DC = {'Perceptually Uniform Sequential': 1.4, 'Sequential': 0.7,

       'Sequential (2)': 1.4, 'Diverging': 1.4, 'Cyclic': 1.4,

       'Qualitative': 1.4, 'Miscellaneous': 1.4}



                                  

x = np.linspace(0.0, 1.0, 100)



         

for cmap_category, cmap_list in cmaps.items():



                                                      

                                         

    dsub = _DSUBS.get(cmap_category, 6)

    nsubplots = int(np.ceil(len(cmap_list) / dsub))



                                                                    

    fig, axs = plt.subplots(nrows=nsubplots, squeeze=False,

                            figsize=(7, 2.6*nsubplots))



    for i, ax in enumerate(axs.flat):



        locs = []                             



        for j, cmap in enumerate(cmap_list[i*dsub:(i+1)*dsub]):



                                                                     

                                                                   

            rgb = mpl.colormaps[cmap](x)[np.newaxis, :, :3]

            lab = cspace_converter("sRGB1", "CAM02-UCS")(rgb)



                                                                      

                                                                         

                               

                                                  



            if cmap_category == 'Sequential':

                                                                               

                                                                          

                y_ = lab[0, ::-1, 0]

                c_ = x[::-1]

            else:

                y_ = lab[0, :, 0]

                c_ = x



            dc = _DC.get(cmap_category, 1.4)                            

            ax.scatter(x + j*dc, y_, c=c_, cmap=cmap, s=300, linewidths=0.0)



                                                 

            if cmap_category in ('Perceptually Uniform Sequential',

                                 'Sequential'):

                locs.append(x[-1] + j*dc)

            elif cmap_category in ('Diverging', 'Qualitative', 'Cyclic',

                                   'Miscellaneous', 'Sequential (2)'):

                locs.append(x[int(x.size/2.)] + j*dc)



                                 

                                                                          

                                                                 

        ax.set_xlim(axs[0, 0].get_xlim())

        ax.set_ylim(0.0, 100.0)



                                     

        ax.xaxis.set_ticks_position('top')

        ticker = mpl.ticker.FixedLocator(locs)

        ax.xaxis.set_major_locator(ticker)

        formatter = mpl.ticker.FixedFormatter(cmap_list[i*dsub:(i+1)*dsub])

        ax.xaxis.set_major_formatter(formatter)

        ax.xaxis.set_tick_params(rotation=50)

        ax.set_ylabel('Lightness $L^*$', fontsize=12)



    ax.set_xlabel(cmap_category + ' colormaps', fontsize=14)



    fig.tight_layout(h_pad=0.0, pad=1.5)

    plt.show()





    

                      

                      

 

                                                                       

                                                                       

                                                                   

                                                               

           

 

                                                                           

                                                                        

                                                                              

                                                                            

                                                                               

                                                                          

                                                                               

                      

 

                                                                         

                                                                             

                                                                        

                                                                             

                                                                    

                                                                             

                                                                       

                                                                           

                                                                               

                                                                           

                                                                             

                                                                             

                                                                         

                                                                              

                                                                             

                                                                      



mpl.rcParams.update({'font.size': 14})



                                   

x = np.linspace(0.0, 1.0, 100)



gradient = np.linspace(0, 1, 256)

gradient = np.vstack((gradient, gradient))





def plot_color_gradients(cmap_category, cmap_list):

    fig, axs = plt.subplots(nrows=len(cmap_list), ncols=2)

    fig.subplots_adjust(top=0.95, bottom=0.01, left=0.2, right=0.99,

                        wspace=0.05)

    fig.suptitle(cmap_category + ' colormaps', fontsize=14, y=1.0, x=0.6)



    for ax, name in zip(axs, cmap_list):



                                      

        rgb = mpl.colormaps[name](x)[np.newaxis, :, :3]



                                                                      

        lab = cspace_converter("sRGB1", "CAM02-UCS")(rgb)

        L = lab[0, :, 0]

        L = np.float32(np.vstack((L, L, L)))



        ax[0].imshow(gradient, aspect='auto', cmap=mpl.colormaps[name])

        ax[1].imshow(L, aspect='auto', cmap='binary_r', vmin=0., vmax=100.)

        pos = list(ax[0].get_position().bounds)

        x_text = pos[0] - 0.01

        y_text = pos[1] + pos[3]/2.

        fig.text(x_text, y_text, name, va='center', ha='right', fontsize=10)



                                                                      

    for ax in axs.flat:

        ax.set_axis_off()



    plt.show()





for cmap_category, cmap_list in cmaps.items():



    plot_color_gradients(cmap_category, cmap_list)



    

                           

                           

 

                                                                        

                                                                               

                                                                    

 

                                                                          

                                                                              

                                 

 

 

            

            

 

                                                                                         

                                                                                                                  

                                                                               

                                                                  

                                                                                                                                    

                                                                                                            

                                                        

                                                                       

                                                     

                                                     

                                                                                       

                                                                    


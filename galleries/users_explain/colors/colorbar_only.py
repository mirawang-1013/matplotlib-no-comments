



import matplotlib.pyplot as plt



import matplotlib as mpl



    

                           

                           

                                                                    

 

                                                                          

                                                                              

                                                                                

                            

 

 

                                                          



fig, ax = plt.subplots(figsize=(6, 1), layout='constrained')



norm = mpl.colors.Normalize(vmin=5, vmax=10)



colorizer = mpl.colorizer.Colorizer(norm=norm, cmap="cool")



fig.colorbar(mpl.colorizer.ColorizingArtist(colorizer),

             cax=ax, orientation='horizontal', label='Some Units')



    

                                               

                                               

                                                                               

                                                                        

                                                                             

                                                                             

                     



fig, ax = plt.subplots(layout='constrained')



colorizer = mpl.colorizer.Colorizer(norm=mpl.colors.Normalize(0, 1), cmap='magma')



fig.colorbar(mpl.colorizer.ColorizingArtist(colorizer),

             ax=ax, orientation='vertical', label='a colorbar label')



    

                                                           

                                                           

                                                                        

                                                                           

                                                                               

                                                                             

                                               



fig, ax = plt.subplots(figsize=(6, 1), layout='constrained')



cmap = mpl.colormaps["viridis"]

bounds = [-1, 2, 5, 7, 12, 15]

norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend='both')



colorizer = mpl.colorizer.Colorizer(norm=norm, cmap='viridis')



fig.colorbar(mpl.colorizer.ColorizingArtist(colorizer),

             cax=ax, orientation='horizontal',

             label="Discrete intervals with extend='both' keyword")



    

                                

                                

                                                                         

                                                                           

                                                                        

                                   

 

                                                           

 

                                                                           

                                                                        

                                                                       

                      

                                                                   

                                                                           

         



fig, ax = plt.subplots(figsize=(6, 1), layout='constrained')



cmap = mpl.colors.ListedColormap(

    ['red', 'green', 'blue', 'cyan'], under='yellow', over='magenta')

bounds = [1, 2, 4, 7, 8]

norm = mpl.colors.BoundaryNorm(bounds, cmap.N)



colorizer = mpl.colorizer.Colorizer(norm=norm, cmap=cmap)



fig.colorbar(

    mpl.colorizer.ColorizingArtist(colorizer),

    cax=ax, orientation='horizontal',

    extend='both',

    spacing='proportional',

    label='Discrete intervals, some other units',

)



    

                                        

                                        

                                                                              

                                                     

                                                                       



fig, ax = plt.subplots(figsize=(6, 1), layout='constrained')



cmap = mpl.colors.ListedColormap(

    ['royalblue', 'cyan', 'yellow', 'orange'], over='red', under='blue')

bounds = [-1.0, -0.5, 0.0, 0.5, 1.0]

norm = mpl.colors.BoundaryNorm(bounds, cmap.N)



colorizer = mpl.colorizer.Colorizer(norm=norm, cmap=cmap)



fig.colorbar(

    mpl.colorizer.ColorizingArtist(colorizer),

    cax=ax, orientation='horizontal',

    extend='both', extendfrac='auto',

    spacing='uniform',

    label='Custom extension lengths, some other units',

)



plt.show()


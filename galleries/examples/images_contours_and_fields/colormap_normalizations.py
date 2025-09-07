



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.colors as colors



N = 100



    

         

         

                                                                                    

                                                                                        

                                                        

 

                                                                                      

                                      



X, Y = np.mgrid[-3:3:complex(0, N), -2:2:complex(0, N)]

Z1 = np.exp(-X**2 - Y**2)

Z2 = np.exp(-(X * 10)**2 - (Y * 10)**2)

Z = Z1 + 50 * Z2



fig, ax = plt.subplots(2, 1)



pcm = ax[0].pcolor(X, Y, Z, cmap='PuBu_r', shading='nearest')

fig.colorbar(pcm, ax=ax[0], extend='max', label='linear scaling')



pcm = ax[1].pcolor(X, Y, Z, cmap='PuBu_r', shading='nearest',

                   norm=colors.LogNorm(vmin=Z.min(), vmax=Z.max()))

fig.colorbar(pcm, ax=ax[1], extend='max', label='LogNorm')



    

           

           

                                                                                    

                                                                                       

                     

 

                                                    



X, Y = np.mgrid[0:3:complex(0, N), 0:2:complex(0, N)]

Z = (1 + np.sin(Y * 10)) * X**2



fig, ax = plt.subplots(2, 1)



pcm = ax[0].pcolormesh(X, Y, Z, cmap='PuBu_r', shading='nearest')

fig.colorbar(pcm, ax=ax[0], extend='max', label='linear scaling')



pcm = ax[1].pcolormesh(X, Y, Z, cmap='PuBu_r', shading='nearest',

                       norm=colors.PowerNorm(gamma=0.5))

fig.colorbar(pcm, ax=ax[1], extend='max', label='PowerNorm')



    

            

            

                                                                                       

                                                                                    

                                              

 

                                                                              

                

 

                                                              



X, Y = np.mgrid[-3:3:complex(0, N), -2:2:complex(0, N)]

Z1 = np.exp(-X**2 - Y**2)

Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)

Z = (5 * Z1 - Z2) * 2



fig, ax = plt.subplots(2, 1)



pcm = ax[0].pcolormesh(X, Y, Z, cmap='RdBu_r', shading='nearest',

                       vmin=-np.max(Z))

fig.colorbar(pcm, ax=ax[0], extend='both', label='linear scaling')



pcm = ax[1].pcolormesh(X, Y, Z, cmap='RdBu_r', shading='nearest',

                       norm=colors.SymLogNorm(linthresh=0.015,

                                              vmin=-10.0, vmax=10.0, base=10))

fig.colorbar(pcm, ax=ax[1], extend='both', label='SymLogNorm')



    

             

             

                                                                                      

                                                                      





                                                               

                                                              

class MidpointNormalize(colors.Normalize):

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):

        self.midpoint = midpoint

        super().__init__(vmin, vmax, clip)



    def __call__(self, value, clip=None):

                                                                          

                           

        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]

        return np.ma.masked_array(np.interp(value, x, y))





    

fig, ax = plt.subplots(2, 1)



pcm = ax[0].pcolormesh(X, Y, Z, cmap='RdBu_r', shading='nearest',

                       vmin=-np.max(Z))

fig.colorbar(pcm, ax=ax[0], extend='both', label='linear scaling')



pcm = ax[1].pcolormesh(X, Y, Z, cmap='RdBu_r', shading='nearest',

                       norm=MidpointNormalize(midpoint=0))

fig.colorbar(pcm, ax=ax[1], extend='both', label='Custom norm')



    

              

              

                                                                               

                                                                                    

                                                            



fig, ax = plt.subplots(3, 1, layout='constrained')



pcm = ax[0].pcolormesh(X, Y, Z, cmap='RdBu_r', shading='nearest',

                       vmin=-np.max(Z))

fig.colorbar(pcm, ax=ax[0], extend='both', orientation='vertical',

             label='linear scaling')



                                                   

bounds = np.linspace(-2, 2, 11)

norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)

pcm = ax[1].pcolormesh(X, Y, Z, cmap='RdBu_r', shading='nearest',

                       norm=norm)

fig.colorbar(pcm, ax=ax[1], extend='both', orientation='vertical',

             label='BoundaryNorm\nlinspace(-2, 2, 11)')



                                                  

bounds = np.array([-1, -0.5, 0, 2.5, 5])

norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)

pcm = ax[2].pcolormesh(X, Y, Z, cmap='RdBu_r', shading='nearest',

                       norm=norm)

fig.colorbar(pcm, ax=ax[2], extend='both', orientation='vertical',

             label='BoundaryNorm\n[-1, -0.5, 0, 2.5, 5]')



plt.show()


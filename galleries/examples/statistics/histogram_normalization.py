



import matplotlib.pyplot as plt

import numpy as np



rng = np.random.default_rng(19680801)



xdata = np.array([1.2, 2.3, 3.3, 3.1, 1.7, 3.4, 2.1, 1.25, 1.3])

xbins = np.array([1, 2, 3, 4])



                                                          

                                                  

style = {'facecolor': 'none', 'edgecolor': 'C0', 'linewidth': 3}



fig, ax = plt.subplots()

ax.hist(xdata, bins=xbins, **style)



                                         

ax.plot(xdata, 0*xdata, 'd')

ax.set_ylabel('Number per bin')

ax.set_xlabel('x bins (dx=1.0)')



    

                

                

 

                                                                            

                                                                             

                             



xbins = np.arange(1, 4.5, 0.5)



fig, ax = plt.subplots()

ax.hist(xdata, bins=xbins, **style)

ax.plot(xdata, 0*xdata, 'd')

ax.set_ylabel('Number per bin')

ax.set_xlabel('x bins (dx=0.5)')



    

                                                                          

                                                   



fig, ax = plt.subplot_mosaic([['auto', 'n4']],

                             sharex=True, sharey=True, layout='constrained')



ax['auto'].hist(xdata, **style)

ax['auto'].plot(xdata, 0*xdata, 'd')

ax['auto'].set_ylabel('Number per bin')

ax['auto'].set_xlabel('x bins (auto)')



ax['n4'].hist(xdata, bins=4, **style)

ax['n4'].plot(xdata, 0*xdata, 'd')

ax['n4'].set_xlabel('x bins ("bins=4")')



    

                                            

                                            

 

                                                                              

                                                                               

                            



fig, ax = plt.subplots()

ax.hist(xdata, bins=xbins, density=True, **style)

ax.set_ylabel('Probability density [$V^{-1}$])')

ax.set_xlabel('x bins (dx=0.5 $V$)')



    

                                                                              

                                                                             

                                                                           

                                                 

         

 

                                                      

                                          

 

                                                          

                                                                               

                                                                               

                                                                               

                                                                               

                                       

 

                                                                               

                                                                              

                             

                                                                               

                                     



xdata = rng.normal(size=1000)

xpdf = np.arange(-4, 4, 0.1)

pdf = 1 / (np.sqrt(2 * np.pi)) * np.exp(-xpdf**2 / 2)



    

                                                                             

                                                                           

       



fig, ax = plt.subplot_mosaic([['False', 'True']], layout='constrained')

dx = 0.1

xbins = np.arange(-4, 4, dx)

ax['False'].hist(xdata, bins=xbins, density=False, histtype='step', label='Counts')



                                  

ax['False'].plot(xpdf, pdf * len(xdata) * dx, label=r'$N\,f_X(x)\,\delta x$')

ax['False'].set_ylabel('Count per bin')

ax['False'].set_xlabel('x bins [V]')

ax['False'].legend()



ax['True'].hist(xdata, bins=xbins, density=True, histtype='step', label='density')

ax['True'].plot(xpdf, pdf, label='$f_X(x)$')

ax['True'].set_ylabel('Probability density [$V^{-1}$]')

ax['True'].set_xlabel('x bins [$V$]')

ax['True'].legend()



    

                                                                              

                                                                        

                                                                               

                                                                            

                                                                               

                                                                               



fig, ax = plt.subplot_mosaic([['False', 'True']], layout='constrained')

dx = 0.1

xbins = np.hstack([np.arange(-4, -1.25, 6*dx), np.arange(-1.25, 4, dx)])

ax['False'].hist(xdata, bins=xbins, density=False, histtype='step', label='Counts')

ax['False'].plot(xpdf, pdf * len(xdata) * dx, label=r'$N\,f_X(x)\,\delta x_0$')

ax['False'].set_ylabel('Count per bin')

ax['False'].set_xlabel('x bins [V]')

ax['False'].legend()



ax['True'].hist(xdata, bins=xbins, density=True, histtype='step', label='density')

ax['True'].plot(xpdf, pdf, label='$f_X(x)$')

ax['True'].set_ylabel('Probability density [$V^{-1}$]')

ax['True'].set_xlabel('x bins [$V$]')

ax['True'].legend()



    

                                                                               

                               



fig, ax = plt.subplot_mosaic([['False', 'True']], layout='constrained')



              

ax['True'].plot(xpdf, pdf, '--', label='$f_X(x)$', color='k')



for nn, dx in enumerate([0.1, 0.4, 1.2]):

    xbins = np.arange(-4, 4, dx)

                         

    ax['False'].plot(xpdf, pdf*1000*dx, '--', color=f'C{nn}')

    ax['False'].hist(xdata, bins=xbins, density=False, histtype='step')



    ax['True'].hist(xdata, bins=xbins, density=True, histtype='step', label=dx)



         

ax['False'].set_xlabel('x bins [$V$]')

ax['False'].set_ylabel('Count per bin')

ax['True'].set_ylabel('Probability density [$V^{-1}$]')

ax['True'].set_xlabel('x bins [$V$]')

ax['True'].legend(fontsize='small', title='bin width:')



    

                                                                               

                                           

                                                                            

                                                                               

                                                                         

                                                                       

                                  



fig, ax = plt.subplots(layout='constrained', figsize=(3.5, 3))



for nn, dx in enumerate([0.1, 0.4, 1.2]):

    xbins = np.arange(-4, 4, dx)

    ax.hist(xdata, bins=xbins, weights=1/len(xdata) * np.ones(len(xdata)),

                   histtype='step', label=f'{dx}')

ax.set_xlabel('x bins [$V$]')

ax.set_ylabel('Bin count / N')

ax.legend(fontsize='small', title='bin width:')



    

                                                                              

                                                                             

                                                             



xdata2 = rng.normal(size=100)



fig, ax = plt.subplot_mosaic([['no_norm', 'density', 'weight']],

                             layout='constrained', figsize=(8, 4))



xbins = np.arange(-4, 4, 0.25)



ax['no_norm'].hist(xdata, bins=xbins, histtype='step')

ax['no_norm'].hist(xdata2, bins=xbins, histtype='step')

ax['no_norm'].set_ylabel('Counts')

ax['no_norm'].set_xlabel('x bins [$V$]')

ax['no_norm'].set_title('No normalization')



ax['density'].hist(xdata, bins=xbins, histtype='step', density=True)

ax['density'].hist(xdata2, bins=xbins, histtype='step', density=True)

ax['density'].set_ylabel('Probability density [$V^{-1}$]')

ax['density'].set_title('Density=True')

ax['density'].set_xlabel('x bins [$V$]')



ax['weight'].hist(xdata, bins=xbins, histtype='step',

                  weights=1 / len(xdata) * np.ones(len(xdata)),

                  label='N=1000')

ax['weight'].hist(xdata2, bins=xbins, histtype='step',

                  weights=1 / len(xdata2) * np.ones(len(xdata2)),

                  label='N=100')

ax['weight'].set_xlabel('x bins [$V$]')

ax['weight'].set_ylabel('Counts / N')

ax['weight'].legend(fontsize='small')

ax['weight'].set_title('Weight = 1/N')



plt.show()



    

 

                                                    

 

                            

 

                                                                              

                     

 

                                                             

                                       

                                        

                                        

                                    


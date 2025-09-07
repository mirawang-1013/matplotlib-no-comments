



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.cbook as cbook



                                    

r = cbook.get_sample_data('goog.npz')['price_data']

                                                  

fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)



pricemin = r["close"].min()



ax1.plot(r["date"], r["close"], lw=2)

ax2.fill_between(r["date"], pricemin, r["close"], alpha=0.7)



for ax in ax1, ax2:

    ax.grid(True)

    ax.label_outer()



ax1.set_ylabel('price')



fig.suptitle('Google (GOOG) daily closing price')

fig.autofmt_xdate()



    

                                                                       

                                                                        

                                                                   

                                                                      

                                                                

                                                                    

                                       

 

                                                                    

                                                                        

                                                                   

                                                                      

                                              



                                         

np.random.seed(19680801)



Nsteps, Nwalkers = 100, 250

t = np.arange(Nsteps)



                                                   

S1 = 0.004 + 0.02*np.random.randn(Nsteps, Nwalkers)

S2 = 0.002 + 0.01*np.random.randn(Nsteps, Nwalkers)



                                                         

X1 = S1.cumsum(axis=0)

X2 = S2.cumsum(axis=0)





                                                                      

                       

mu1 = X1.mean(axis=1)

sigma1 = X1.std(axis=1)

mu2 = X2.mean(axis=1)

sigma2 = X2.std(axis=1)



          

fig, ax = plt.subplots(1)

ax.plot(t, mu1, lw=2, label='mean population 1')

ax.plot(t, mu2, lw=2, label='mean population 2')

ax.fill_between(t, mu1+sigma1, mu1-sigma1, facecolor='C0', alpha=0.4)

ax.fill_between(t, mu2+sigma2, mu2-sigma2, facecolor='C1', alpha=0.4)

ax.set_title(r'random walkers empirical $\mu$ and $\pm \sigma$ interval')

ax.legend(loc='upper left')

ax.set_xlabel('num steps')

ax.set_ylabel('position')

ax.grid()



    

                                                                       

                                                                       

                                                                       

                                                                       

                                                                       

                                                                       

                                                                     

                                                                     

                                                                     

                            



                                         

np.random.seed(1)



Nsteps = 500

t = np.arange(Nsteps)



mu = 0.002

sigma = 0.01



                        

S = mu + sigma*np.random.randn(Nsteps)

X = S.cumsum()



                                                        

lower_bound = mu*t - sigma*np.sqrt(t)

upper_bound = mu*t + sigma*np.sqrt(t)



fig, ax = plt.subplots(1)

ax.plot(t, X, lw=2, label='walker position')

ax.plot(t, mu*t, lw=1, label='population mean', color='C0', ls='--')

ax.fill_between(t, lower_bound, upper_bound, facecolor='C0', alpha=0.4,

                label='1 sigma range')

ax.legend(loc='upper left')



                                                                  

                                                 

ax.fill_between(t, upper_bound, X, where=X > upper_bound, fc='red', alpha=0.4)

ax.fill_between(t, lower_bound, X, where=X < lower_bound, fc='red', alpha=0.4)

ax.set_xlabel('num steps')

ax.set_ylabel('position')

ax.grid()



    

                                                                            

                                                                  

                                                                           

                                                         



plt.show()



    

           

 

                   

                            

                        

                      


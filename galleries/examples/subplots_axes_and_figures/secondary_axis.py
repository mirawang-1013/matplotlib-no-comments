



import datetime



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.dates as mdates



fig, ax = plt.subplots(layout='constrained')

x = np.arange(0, 360, 1)

y = np.sin(2 * x * np.pi / 180)

ax.plot(x, y)

ax.set_xlabel('angle [degrees]')

ax.set_ylabel('signal')

ax.set_title('Sine wave')





def deg2rad(x):

    return x * np.pi / 180





def rad2deg(x):

    return x * 180 / np.pi





secax = ax.secondary_xaxis('top', functions=(deg2rad, rad2deg))

secax.set_xlabel('angle [rad]')

plt.show()



    

                                                                       

                                                                   

                                                                      



fig, ax = plt.subplots(layout='constrained')

x = np.arange(0, 10)

np.random.seed(19680801)

y = np.random.randn(len(x))

ax.plot(x, y)

ax.set_xlabel('X')

ax.set_ylabel('Y')

ax.set_title('Random data')



                                                                         

secax = ax.secondary_xaxis(0, transform=ax.transData)

secax.set_xlabel('Axis at Y = 0')

plt.show()



    

                                                                   

                

 

           

 

                                                                          

                             



fig, ax = plt.subplots(layout='constrained')

x = np.arange(0.02, 1, 0.02)

np.random.seed(19680801)

y = np.random.randn(len(x)) ** 2

ax.loglog(x, y)

ax.set_xlabel('f [Hz]')

ax.set_ylabel('PSD')

ax.set_title('Random spectrum')





def one_over(x):

    

    x = np.array(x, float)

    near_zero = np.isclose(x, 0)

    x[near_zero] = np.inf

    x[~near_zero] = 1 / x[~near_zero]

    return x





                                       

inverse = one_over





secax = ax.secondary_xaxis('top', functions=(one_over, inverse))

secax.set_xlabel('period [s]')

plt.show()



    

                                                                                      

                                                                                       

                                                                                    

                                                                               

 

           

 

                                                                       

                                                                               

                                                                        

                                                                            

                                  



fig, ax = plt.subplots(layout='constrained')

x1_vals = np.arange(2, 11, 0.4)

                                                                   

x2_vals = x1_vals ** 2

ydata = 50.0 + 20 * np.random.randn(len(x1_vals))

ax.plot(x1_vals, ydata, label='Plotted data')

ax.plot(x1_vals, x2_vals, label=r'$x_2 = x_1^2$')

ax.set_xlabel(r'$x_1$')

ax.legend()



                                                                                      

x1n = np.linspace(0, 20, 201)

x2n = x1n**2





def forward(x):

    return np.interp(x, x1n, x2n)





def inverse(x):

    return np.interp(x, x2n, x1n)



                                                                           

ax.axvline(np.sqrt(40), color="grey", ls="--")

ax.axvline(10, color="grey", ls="--")

secax = ax.secondary_xaxis('top', functions=(forward, inverse))

secax.set_xticks([10, 20, 40, 60, 80, 100])

secax.set_xlabel(r'$x_2$')



plt.show()



    

                                                                       

                                                                   

                                                               

                   



dates = [datetime.datetime(2018, 1, 1) + datetime.timedelta(hours=k * 6)

         for k in range(240)]

temperature = np.random.randn(len(dates)) * 4 + 6.7

fig, ax = plt.subplots(layout='constrained')



ax.plot(dates, temperature)

ax.set_ylabel(r'$T\ [^oC]$')

ax.xaxis.set_tick_params(rotation=70)





def date2yday(x):

    

    y = x - mdates.date2num(datetime.datetime(2018, 1, 1))

    return y





def yday2date(x):

    

    y = x + mdates.date2num(datetime.datetime(2018, 1, 1))

    return y





secax_x = ax.secondary_xaxis('top', functions=(date2yday, yday2date))

secax_x.set_xlabel('yday [2018]')





def celsius_to_fahrenheit(x):

    return x * 1.8 + 32





def fahrenheit_to_celsius(x):

    return (x - 32) / 1.8





secax_y = ax.secondary_yaxis(

    'right', functions=(celsius_to_fahrenheit, fahrenheit_to_celsius))

secax_y.set_ylabel(r'$T\ [^oF]$')





def celsius_to_anomaly(x):

    return (x - np.mean(temperature))





def anomaly_to_celsius(x):

    return (x + np.mean(temperature))





                                  

secax_y2 = ax.secondary_yaxis(

    1.2, functions=(celsius_to_anomaly, anomaly_to_celsius))

secax_y2.set_ylabel(r'$T - \overline{T}\ [^oC]$')





plt.show()



    

 

                            

 

                                                                              

                     

 

                                             

                                             

 

           

 

                    

                    

                    






import matplotlib.pyplot as plt

import numpy as np



import matplotlib.dates as mdates



rng = np.random.default_rng(19680801)



fig, ax = plt.subplots(layout='constrained', figsize=(4, 4))



ax.plot(np.arange(30))



sec = ax.secondary_xaxis(location=0)

sec.set_xticks([5, 15, 25], labels=['\nOughts', '\nTeens', '\nTwenties'])



    

                                                                              

                                                                             

                                                                          

                                                                              

               

 

                                                                          

                                                                             

                 



fig, ax = plt.subplots(layout='constrained', figsize=(7, 4))



ax.plot(['cats', 'dogs', 'pigs', 'snakes', 'lizards', 'chickens',

         'eagles', 'herons', 'buzzards'],

        rng.normal(size=9), 'o')



                    

sec = ax.secondary_xaxis(location=0)

sec.set_xticks([1, 3.5, 6.5], labels=['\n\nMammals', '\n\nReptiles', '\n\nBirds'])

sec.tick_params('x', length=0)



                            

sec2 = ax.secondary_xaxis(location=0)

sec2.set_xticks([-0.5, 2.5, 4.5, 8.5], labels=[])

sec2.tick_params('x', length=40, width=1.5)

ax.set_xlim(-0.6, 8.6)



    

                                                                            

                                                                             

                                                                              

                                     

 

                                                                              

                                                                               

                                                                            

                                                



fig, ax = plt.subplots(layout='constrained', figsize=(7, 4))



time = np.arange(np.datetime64('2020-01-01'), np.datetime64('2020-03-31'),

                 np.timedelta64(1, 'D'))



ax.plot(time, rng.random(size=len(time)))



                       

ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))



                   

sec = ax.secondary_xaxis(location=-0.075)

sec.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))



                                                                               

                                                                               

sec.xaxis.set_major_formatter(mdates.DateFormatter('  %b'))

sec.tick_params('x', length=0)

sec.spines['bottom'].set_linewidth(0)



                                                                        

                  

sec.set_xlabel('Dates (2020)')



plt.show()


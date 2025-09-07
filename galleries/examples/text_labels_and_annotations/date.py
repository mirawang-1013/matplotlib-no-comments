



import matplotlib.pyplot as plt



import matplotlib.cbook as cbook

import matplotlib.dates as mdates



                                                                             

                                                                            

                                                                           

                  

data = cbook.get_sample_data('goog.npz')['price_data']



fig, axs = plt.subplots(3, 1, figsize=(6.4, 7), layout='constrained')

                      

for ax in axs:

    ax.plot('date', 'adj_close', data=data)

                                                           

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))

    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    ax.grid(True)

    ax.set_ylabel(r'Price [\$]')



                    

ax = axs[0]

ax.set_title('DefaultFormatter', loc='left', y=0.85, x=0.02, fontsize='medium')



ax = axs[1]

ax.set_title('ConciseFormatter', loc='left', y=0.85, x=0.02, fontsize='medium')

ax.xaxis.set_major_formatter(

    mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))



ax = axs[2]

ax.set_title('Manual DateFormatter', loc='left', y=0.85, x=0.02,

             fontsize='medium')

                                                           

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))

                                                                       

ax.xaxis.set_tick_params(rotation=30, rotation_mode='xtick')



plt.show()


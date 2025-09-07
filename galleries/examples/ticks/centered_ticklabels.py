



import matplotlib.pyplot as plt



import matplotlib.cbook as cbook

import matplotlib.dates as dates

import matplotlib.ticker as ticker



                                                

r = cbook.get_sample_data('goog.npz')['price_data']

r = r[-250:]                         



fig, ax = plt.subplots()

ax.plot(r["date"], r["adj_close"])



ax.xaxis.set_major_locator(dates.MonthLocator())

                                                                     

ax.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=16))



                                                 

ax.xaxis.set_major_formatter(ticker.NullFormatter())

ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))



                             

ax.tick_params(axis='x', which='minor', tick1On=False, tick2On=False)



imid = len(r) // 2

ax.set_xlabel(str(r["date"][imid].item().year))

plt.show()




import datetime



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.dates as mdates



    

                               



base = datetime.datetime(2005, 2, 1)

dates = [base + datetime.timedelta(hours=(2 * i)) for i in range(732)]

N = len(dates)

np.random.seed(19680801)

y = np.cumsum(np.random.randn(N))



fig, axs = plt.subplots(3, 1, layout='constrained', figsize=(6, 6))

lims = [(np.datetime64('2005-02'), np.datetime64('2005-04')),

        (np.datetime64('2005-02-03'), np.datetime64('2005-02-15')),

        (np.datetime64('2005-02-03 11:00'), np.datetime64('2005-02-04 13:20'))]

for nn, ax in enumerate(axs):

    ax.plot(dates, y)

    ax.set_xlim(lims[nn])

    ax.tick_params(axis='x', rotation=40, rotation_mode='xtick')

axs[0].set_title('Default Date Formatter')

plt.show()



    

                                                                       

                                                                  

                                                                          

                                                                



fig, axs = plt.subplots(3, 1, layout='constrained', figsize=(6, 6))

for nn, ax in enumerate(axs):

    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)

    formatter = mdates.ConciseDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)

    ax.xaxis.set_major_formatter(formatter)



    ax.plot(dates, y)

    ax.set_xlim(lims[nn])

axs[0].set_title('Concise Date Formatter')



plt.show()



    

                                                                           

                                                                       

          



import matplotlib.units as munits



converter = mdates.ConciseDateConverter()

munits.registry[np.datetime64] = converter

munits.registry[datetime.date] = converter

munits.registry[datetime.datetime] = converter



fig, axs = plt.subplots(3, 1, figsize=(6, 6), layout='constrained')

for nn, ax in enumerate(axs):

    ax.plot(dates, y)

    ax.set_xlim(lims[nn])

axs[0].set_title('Concise Date Formatter')



plt.show()



    

                              

                              

 

                                                                            

                                             

 

                                                                          

                                                                     

                                                                          

                                                                            

                                                                        

                                                                             

                                                                          

                                             

                                                                             

                                                                         

                                                                  

 

                                                                            

                                

 

                                                                      

                   



fig, axs = plt.subplots(3, 1, layout='constrained', figsize=(6, 6))



for nn, ax in enumerate(axs):

    locator = mdates.AutoDateLocator()

    formatter = mdates.ConciseDateFormatter(locator)

    formatter.formats = ['%y',                          

                         '%b',                                

                         '%d',                              

                         '%H:%M',         

                         '%H:%M',         

                         '%S.%f', ]        

                                              

    formatter.zero_formats = [''] + formatter.formats[:-1]

                                                                        

                

    formatter.zero_formats[3] = '%d-%b'



    formatter.offset_formats = ['',

                                '%Y',

                                '%b %Y',

                                '%d %b %Y',

                                '%d %b %Y',

                                '%d %b %Y %H:%M', ]

    ax.xaxis.set_major_locator(locator)

    ax.xaxis.set_major_formatter(formatter)



    ax.plot(dates, y)

    ax.set_xlim(lims[nn])

axs[0].set_title('Concise Date Formatter')



plt.show()



    

                                           

                                           

 

                                                                             

                                                                             

                                                                 



import datetime



formats = ['%y',                                  

           '%b',                              

           '%d',                            

           '%H:%M',       

           '%H:%M',       

           '%S.%f', ]        

                                                       

zero_formats = [''] + formats[:-1]

                                                                             

zero_formats[3] = '%d-%b'

offset_formats = ['',

                  '%Y',

                  '%b %Y',

                  '%d %b %Y',

                  '%d %b %Y',

                  '%d %b %Y %H:%M', ]



converter = mdates.ConciseDateConverter(

    formats=formats, zero_formats=zero_formats, offset_formats=offset_formats)



munits.registry[np.datetime64] = converter

munits.registry[datetime.date] = converter

munits.registry[datetime.datetime] = converter



fig, axs = plt.subplots(3, 1, layout='constrained', figsize=(6, 6))

for nn, ax in enumerate(axs):

    ax.plot(dates, y)

    ax.set_xlim(lims[nn])

axs[0].set_title('Concise Date Formatter registered non-default')



plt.show()


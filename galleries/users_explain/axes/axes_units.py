



import numpy as np



import matplotlib.dates as mdates

import matplotlib.units as munits



import matplotlib.pyplot as plt



fig, ax = plt.subplots(figsize=(5.4, 2), layout='constrained')

time = np.arange('1980-01-01', '1980-06-25', dtype='datetime64[D]')

x = np.arange(len(time))

ax.plot(time, x)



    

 

                                                                          

                                                                            

                                                                            

                                                                               

                  



fig, ax = plt.subplots(figsize=(5.4, 2), layout='constrained')

time = np.arange('1980-01-01', '1980-06-25', dtype='datetime64[D]')

x = np.arange(len(time))

ax.plot(time, x)

                              

ax.plot(0, 0, 'd')

ax.text(0, 0, ' Float x=0', rotation=45)



    

 

                                                                              

                                                 

                                                                              

                                                                             

                                                                



fig, ax = plt.subplots(figsize=(5.4, 2), layout='constrained')

time = np.arange('1980-01-01', '1980-06-25', dtype='datetime64[D]')

x = np.arange(len(time))

ax.plot(time, x)

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=np.arange(1, 13, 2)))

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

ax.set_xlabel('1980')



    

 

                                                                       

                                                                             

                                                                               

                                                                         

                                                                               



plt.rcParams['date.converter'] = 'concise'



fig, ax = plt.subplots(figsize=(5.4, 2), layout='constrained')

time = np.arange('1980-01-01', '1980-06-25', dtype='datetime64[D]')

x = np.arange(len(time))

ax.plot(time, x)



    

 

                                                                              

                                                                          

                                                             

                     



fig, axs = plt.subplots(2, 1, figsize=(5.4, 3), layout='constrained')

for ax in axs.flat:

    time = np.arange('1980-01-01', '1980-06-25', dtype='datetime64[D]')

    x = np.arange(len(time))

    ax.plot(time, x)



                            

axs[0].set_xlim(np.datetime64('1980-02-01'), np.datetime64('1980-04-01'))



                        

                                                                

axs[1].set_xlim(3683, 3683+60)



    

 

                                      

                                      

 

                                                                       

                                                             

                           



data = {'apple': 10, 'orange': 15, 'lemon': 5, 'lime': 20}

names = list(data.keys())

values = list(data.values())



fig, axs = plt.subplots(1, 3, figsize=(7, 3), sharey=True, layout='constrained')

axs[0].bar(names, values)

axs[1].scatter(names, values)

axs[2].plot(names, values)

fig.suptitle('Categorical Plotting')



    

 

                                                                         

                                                                             

                                                                           

                



fig, ax = plt.subplots(figsize=(5, 3), layout='constrained')

ax.bar(names, values)



                            

ax.scatter(['lemon', 'apple'], [7, 12])



                                                                                

ax.plot(['pear', 'orange', 'apple', 'lemon'], [13, 10, 7, 12], color='C1')





    

 

                                                                               

                                                                               

            

 

                                                                               

                                                                            

                                                                            

                                                                          

                                                                            

                           



fig, ax = plt.subplots(figsize=(5, 3), layout='constrained')

ax.bar(names, values)

                                         

args = {'rotation': 70, 'color': 'C1',

        'bbox': {'color': 'white', 'alpha': .7, 'boxstyle': 'round'}}





                           

ax.plot(0, 2, 'd', color='C1')

ax.text(0, 3, 'Float x=0', **args)



                           

ax.plot(2, 2, 'd', color='C1')

ax.text(2, 3, 'Float x=2', **args)



                       

ax.plot(4, 2, 'd', color='C1')

ax.text(4, 3, 'Float x=4', **args)



                         

ax.plot(2.5, 2, 'd', color='C1')

ax.text(2.5, 3, 'Float x=2.5', **args)



    

 

                                                                      

                                                      



fig, axs = plt.subplots(2, 1, figsize=(5, 5), layout='constrained')

ax = axs[0]

ax.bar(names, values)

ax.set_xlim('orange', 'lemon')

ax.set_xlabel('limits set with categories')

ax = axs[1]

ax.bar(names, values)

ax.set_xlim(0.5, 2.5)

ax.set_xlabel('limits set with floats')



    

 

                                                                              

                                                                              

                                                                             

                                                                             

                                          



fig, ax = plt.subplots(figsize=(5.4, 2.5), layout='constrained')

x = [str(xx) for xx in np.arange(100)]                   

ax.plot(x, np.arange(100))

ax.set_xlabel('x is list of strings')



    

 

                                                                                 



fig, ax = plt.subplots(figsize=(5.4, 2.5), layout='constrained')

x = np.asarray(x, dtype='float')                   

ax.plot(x, np.arange(100))

ax.set_xlabel('x is array of floats')



    

 

                                                        

                                                        

 

                                                                         

                                                                          

                                                                            

                                                                        

 

                                               



fig, axs = plt.subplots(3, 1, figsize=(6.4, 7), layout='constrained')

x = np.arange(100)

ax = axs[0]

ax.plot(x, x)

label = f'Converter: {ax.xaxis.get_converter()}\n '

label += f'Locator: {ax.xaxis.get_major_locator()}\n'

label += f'Formatter: {ax.xaxis.get_major_formatter()}\n'

ax.set_xlabel(label)



ax = axs[1]

time = np.arange('1980-01-01', '1980-06-25', dtype='datetime64[D]')

x = np.arange(len(time))

ax.plot(time, x)

label = f'Converter: {ax.xaxis.get_converter()}\n '

label += f'Locator: {ax.xaxis.get_major_locator()}\n'

label += f'Formatter: {ax.xaxis.get_major_formatter()}\n'

ax.set_xlabel(label)



ax = axs[2]

data = {'apple': 10, 'orange': 15, 'lemon': 5, 'lime': 20}

names = list(data.keys())

values = list(data.values())

ax.plot(names, values)

label = f'Converter: {ax.xaxis.get_converter()}\n '

label += f'Locator: {ax.xaxis.get_major_locator()}\n'

label += f'Formatter: {ax.xaxis.get_major_formatter()}\n'

ax.set_xlabel(label)



    

 

                           

                           

 

                                                                               

                                                                       

                             

 

                                                                        

                                                                             

                                                                       

                                                                              

                                                  



for k, v in munits.registry.items():

    print(f"type: {k};\n    converter: {type(v)}")



    

 

                                                                              

                                                                     

                                                                                  

                                                      

 

                                                                     

                                                                 

                                                                          

                                                                            

                                                                     

                                               


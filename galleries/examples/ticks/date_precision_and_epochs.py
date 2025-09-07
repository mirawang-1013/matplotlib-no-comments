

import datetime



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.dates as mdates





def _reset_epoch_for_tutorial():

    

    mdates._reset_epoch_test_example()





    

          

          

 

                                                                     

                                                                            

          



old_epoch = '0000-12-31T00:00:00'

new_epoch = '1970-01-01T00:00:00'



_reset_epoch_for_tutorial()                                           

mdates.set_epoch(old_epoch)                           



date1 = datetime.datetime(2000, 1, 1, 0, 10, 0, 12,

                          tzinfo=datetime.timezone.utc)

mdate1 = mdates.date2num(date1)

print('Before Roundtrip: ', date1, 'Matplotlib date:', mdate1)

date2 = mdates.num2date(mdate1)

print('After Roundtrip:  ', date2)



    

                                                                  

                                



date1 = datetime.datetime(10, 1, 1, 0, 10, 0, 12,

                          tzinfo=datetime.timezone.utc)

mdate1 = mdates.date2num(date1)

print('Before Roundtrip: ', date1, 'Matplotlib date:', mdate1)

date2 = mdates.num2date(mdate1)

print('After Roundtrip:  ', date2)



    

                                                                    

                                                                        

                                                                       

                                                                       



try:

    mdates.set_epoch(new_epoch)                                    

except RuntimeError as e:

    print('RuntimeError:', str(e))



    

                                                                            

                                            



_reset_epoch_for_tutorial()                                      

mdates.set_epoch(new_epoch)



date1 = datetime.datetime(2020, 1, 1, 0, 10, 0, 12,

                          tzinfo=datetime.timezone.utc)

mdate1 = mdates.date2num(date1)

print('Before Roundtrip: ', date1, 'Matplotlib date:', mdate1)

date2 = mdates.num2date(mdate1)

print('After Roundtrip:  ', date2)



    

            

            

 

                                                                         

                                                                            

                                                                             

                                        



_reset_epoch_for_tutorial()                                           

mdates.set_epoch(new_epoch)



date1 = np.datetime64('2000-01-01T00:10:00.000012')

mdate1 = mdates.date2num(date1)

print('Before Roundtrip: ', date1, 'Matplotlib date:', mdate1)

date2 = mdates.num2date(mdate1)

print('After Roundtrip:  ', date2)



    

          

          

 

                                                                           

                                                                             

                       



_reset_epoch_for_tutorial()                                           

mdates.set_epoch(old_epoch)



x = np.arange('2000-01-01T00:00:00.0', '2000-01-01T00:00:00.000100',

              dtype='datetime64[us]')

                                                  

xold = np.array([mdates.num2date(mdates.date2num(d)) for d in x])

y = np.arange(0, len(x))



                                             

_reset_epoch_for_tutorial()                                           

mdates.set_epoch(new_epoch)



fig, ax = plt.subplots(layout='constrained')

ax.plot(xold, y)

ax.set_title('Epoch: ' + mdates.get_epoch())

ax.xaxis.set_tick_params(rotation=40)

plt.show()



    

                                                                    



fig, ax = plt.subplots(layout='constrained')

ax.plot(x, y)

ax.set_title('Epoch: ' + mdates.get_epoch())

ax.xaxis.set_tick_params(rotation=40)

plt.show()



_reset_epoch_for_tutorial()                                           



    

 

                            

 

                                                                              

                     

 

                                  

                                  

                                   




import matplotlib.pyplot as plt

import numpy as np



                                         

np.random.seed(19680801)



dt = 0.0005

t = np.arange(0.0, 20.5, dt)

s1 = np.sin(2 * np.pi * 100 * t)

s2 = 2 * np.sin(2 * np.pi * 400 * t)



                            

s2[t <= 10] = s2[12 <= t] = 0



                             

nse = 0.01 * np.random.random(size=len(t))



x = s1 + s2 + nse              

NFFT = 1024                                        

Fs = 1/dt                          



fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

ax1.plot(t, x)

ax1.set_ylabel('Signal')



Pxx, freqs, bins, im = ax2.specgram(x, NFFT=NFFT, Fs=Fs)

                                                    

                        

                               

                                      

                                                                       

ax2.set_xlabel('Time (s)')

ax2.set_ylabel('Frequency (Hz)')

ax2.set_xlim(0, 20)



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                     


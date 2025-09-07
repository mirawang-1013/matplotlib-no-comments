



import matplotlib.pyplot as plt

import numpy as np



np.random.seed(19680801)



pts = np.random.rand(30)*.2

                                                                       

pts[[3, 14]] += .8



                                                                  

                                                                       

                                                                        

                                                   

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

fig.subplots_adjust(hspace=0.05)                             



                                 

ax1.plot(pts)

ax2.plot(pts)



                                                            

ax1.set_ylim(.78, 1.)                 

ax2.set_ylim(0, .22)                    



                                    

ax1.spines.bottom.set_visible(False)

ax2.spines.top.set_visible(False)

ax1.xaxis.tick_top()

ax1.tick_params(labeltop=False)                                    

ax2.xaxis.tick_bottom()



                                                    

                                                                    

                                                    

                                                                            

                                                                            

                                       



d = .5                                                                   

kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,

              linestyle="none", color='k', mec='k', mew=1, clip_on=False)

ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)

ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)





plt.show()



    

           

 

                    

                    

                        


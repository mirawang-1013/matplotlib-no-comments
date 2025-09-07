



import warnings



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.collections import LineCollection





def colored_line(x, y, c, ax=None, **lc_kwargs):

    

    if "array" in lc_kwargs:

        warnings.warn(

            'The provided "array" keyword argument will be overridden',

            UserWarning,

            stacklevel=2,

        )



    xy = np.stack((x, y), axis=-1)

    xy_mid = np.concat(

        (xy[0, :][None, :], (xy[:-1, :] + xy[1:, :]) / 2, xy[-1, :][None, :]), axis=0

    )

    segments = np.stack((xy_mid[:-1, :], xy, xy_mid[1:, :]), axis=-2)

               

                                                                          

                                                                    

                                                                    

                                                                               



    lc_kwargs["array"] = c

    lc = LineCollection(segments, **lc_kwargs)



                                          

    ax = ax or plt.gca()

    ax.add_collection(lc)



    return lc





                                                    

                                                           

t = np.linspace(-7.4, -0.5, 200)

x = 0.9 * np.sin(t)

y = 0.9 * np.cos(1.6 * t)

color = np.linspace(0, 2, t.size)



                                         

fig1, ax1 = plt.subplots()

lines = colored_line(x, y, color, ax1, linewidth=10, cmap="plasma")

fig1.colorbar(lines)                      



ax1.set_title("Color at each point")



plt.show()



                                                                    

                                                                              

                                                                              

                                                                               

                         

x = [0, 1, 2, 3, 4]

y = [0, 1, 2, 1, 1]

c = [1, 2, 3, 4, 5]

fig, ax = plt.subplots()

ax.scatter(x, y, c=c, cmap='rainbow')

colored_line(x, y, c=c, ax=ax, cmap='rainbow')



plt.show()



                                                                    

                             

                             

 





def colored_line_between_pts(x, y, c, ax, **lc_kwargs):

    

    if "array" in lc_kwargs:

        warnings.warn('The provided "array" keyword argument will be overridden')



                                                                                

    if len(c) != len(x) - 1:

        warnings.warn(

            "The c argument should have a length one less than the length of x and y. "

            "If it has the same length, use the colored_line function instead."

        )



                                                                          

                                                                               

                                                                                 

                                                                  

    points = np.array([x, y]).T.reshape(-1, 1, 2)

    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = LineCollection(segments, **lc_kwargs)



                                          

    lc.set_array(c)



    return ax.add_collection(lc)





                                                    

x = np.linspace(0, 3 * np.pi, 500)

y = np.sin(x)

dydx = np.cos(0.5 * (x[:-1] + x[1:]))                    



fig2, ax2 = plt.subplots()

line = colored_line_between_pts(x, y, dydx, ax2, linewidth=2, cmap="viridis")

fig2.colorbar(line, ax=ax2, label="dy/dx")



ax2.set_xlim(x.min(), x.max())

ax2.set_ylim(-1.1, 1.1)

ax2.set_title("Color between points")



plt.show()



    

           

 

                   

                       

                    

                        


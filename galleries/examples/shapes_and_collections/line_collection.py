



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.collections import LineCollection



colors = ["indigo", "blue", "green", "yellow", "orange", "red"]



                                                  

theta = np.linspace(0, np.pi, 36)

radii = np.linspace(4, 5, num=len(colors))

arcs = [np.column_stack([r * np.cos(theta), r * np.sin(theta)]) for r in radii]



fig, ax = plt.subplots(figsize=(6.4, 3.2))

                                                                              

ax.set_xlim(-6, 6)

ax.set_ylim(0, 6)

ax.set_aspect("equal")                                  



                                               

                                                                                   

                                                                                   

line_collection = LineCollection(arcs, colors=colors, linewidths=4)

ax.add_collection(line_collection)



plt.show()



    

                                                                                   

                                                                                     

                                                                                    

                                          



num_arcs = 15

theta = np.linspace(0, np.pi, 36)

radii = np.linspace(4, 5.5, num=num_arcs)

arcs = [np.column_stack([r * np.cos(theta), r * np.sin(theta)]) for r in radii]



fig, ax = plt.subplots(figsize=(6.4, 3))

                                                                              

ax.set_xlim(-6, 6)

ax.set_ylim(0, 6)

ax.set_aspect("equal")                                  



                                                                 

line_collection = LineCollection(arcs, array=radii, cmap="rainbow")

ax.add_collection(line_collection)



fig.colorbar(line_collection, label="Radius")

ax.set_title("Line Collection with mapped colors")



plt.show()

    

 

                            

 

                                                                              

                     

 

                                              

                                                    

                                            

                                                                         


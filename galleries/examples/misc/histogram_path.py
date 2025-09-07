



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.patches as patches

import matplotlib.path as path



np.random.seed(19680801)                                           



                               

data = np.random.randn(1000)

n, bins = np.histogram(data, 50)



                                                     

left = bins[:-1]

right = bins[1:]

bottom = np.zeros(len(left))

top = bottom + n



                                                                     

                                   

XY = np.array([[left, left, right, right], [bottom, top, top, bottom]]).T



                     

barpath = path.Path.make_compound_path_from_polys(XY)



                                                   

patch = patches.PathPatch(barpath)

patch.sticky_edges.y[:] = [0]



fig, ax = plt.subplots()

ax.add_patch(patch)

ax.autoscale_view()

plt.show()



    

                                                         

                                                                          

                                                                



nrects = len(left)

nverts = nrects*(1+3+1)

verts = np.zeros((nverts, 2))

codes = np.ones(nverts, int) * path.Path.LINETO

codes[0::5] = path.Path.MOVETO

codes[4::5] = path.Path.CLOSEPOLY

verts[0::5, 0] = left

verts[0::5, 1] = bottom

verts[1::5, 0] = left

verts[1::5, 1] = top

verts[2::5, 0] = right

verts[2::5, 1] = top

verts[3::5, 0] = right

verts[3::5, 1] = bottom



barpath = path.Path(verts, codes)



                                                   

patch = patches.PathPatch(barpath)

patch.sticky_edges.y[:] = [0]



fig, ax = plt.subplots()

ax.add_patch(patch)

ax.autoscale_view()

plt.show()



    

 

                            

 

                                                                              

                     

 

                           

                                     

                        

                             

                                                           

                                       

                                              

 

                                         

 

                                              

                                  


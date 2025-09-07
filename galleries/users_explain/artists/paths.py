



import numpy as np



import matplotlib.pyplot as plt



import matplotlib.patches as patches

from matplotlib.path import Path



verts = [

   (0., 0.),                

   (0., 1.),             

   (1., 1.),              

   (1., 0.),                 

   (0., 0.),           

]



codes = [

    Path.MOVETO,

    Path.LINETO,

    Path.LINETO,

    Path.LINETO,

    Path.CLOSEPOLY,

]



path = Path(verts, codes)



fig, ax = plt.subplots()

patch = patches.PathPatch(path, facecolor='orange', lw=2)

ax.add_patch(patch)

ax.set_xlim(-2, 2)

ax.set_ylim(-2, 2)

plt.show()





    

                                         

 

                                                                               

                                                    

                                                                               

                                                                           

                                                                         

                                                  

                                                                              

                                                

                                                                              

                                                             

                                                                               

                                                                         

                                                                               

                                                                           

                                                                         

                                                                         

                                               

                                                                               

                                                                 

                                                                               

 

 

                 

 

 

                

                

 

                                                                        

                                  

                                                                    

                                                                        

                                                                  

                                                                   

                                                                     

       



verts = [

   (0., 0.),       

   (0.2, 1.),      

   (1., 0.8),      

   (0.8, 0.),      

]



codes = [

    Path.MOVETO,

    Path.CURVE4,

    Path.CURVE4,

    Path.CURVE4,

]



path = Path(verts, codes)



fig, ax = plt.subplots()

patch = patches.PathPatch(path, facecolor='none', lw=2)

ax.add_patch(patch)



xs, ys = zip(*verts)

ax.plot(xs, ys, 'x--', lw=2, color='black', ms=10)



ax.text(-0.05, -0.05, 'P0')

ax.text(0.15, 1.05, 'P1')

ax.text(1.05, 0.85, 'P2')

ax.text(0.85, -0.05, 'P3')



ax.set_xlim(-0.1, 1.1)

ax.set_ylim(-0.1, 1.1)

plt.show()



    

                    

 

                

                

 

                                                                      

                                                                     

                                             

                                                             

                                                                          

                                                                       

                                                                  

                                                                      

                                                                      

                                                                   

                                                                      

                                                                  

 

                                                                     

                                                                      

                                                                        

                                                              

                                                                      

                                                                   

                 

 

                                     

                                  

                                       

 

                                                               

                                                                        

                                              

 

                                                           

                                

                                

                                  

                      

 

                                                                     

                                                                        

                                                                    

                                                                        

                                                                           

                                                       

 

                             

                                   

                                                     

                                    

                                       

                           

                             

                           

                          

                            

                          

                            

                             

 

                                                        

                                                                  

 

                                       

                                                           

                                      

                         



fig, ax = plt.subplots()

                                         

np.random.seed(19680801)



                               

data = np.random.randn(1000)

n, bins = np.histogram(data, 100)



                                                     

left = np.array(bins[:-1])

right = np.array(bins[1:])

bottom = np.zeros(len(left))

top = bottom + n

nrects = len(left)



nverts = nrects*(1+3+1)

verts = np.zeros((nverts, 2))

codes = np.full(nverts, Path.LINETO, dtype=int)

codes[0::5] = Path.MOVETO

codes[4::5] = Path.CLOSEPOLY

verts[0::5, 0] = left

verts[0::5, 1] = bottom

verts[1::5, 0] = left

verts[1::5, 1] = top

verts[2::5, 0] = right

verts[2::5, 1] = top

verts[3::5, 0] = right

verts[3::5, 1] = bottom



barpath = Path(verts, codes)

patch = patches.PathPatch(barpath, facecolor='green',

                          edgecolor='yellow', alpha=0.5)

ax.add_patch(patch)



ax.set_xlim(left[0], right[-1])

ax.set_ylim(bottom.min(), top.max())



plt.show()


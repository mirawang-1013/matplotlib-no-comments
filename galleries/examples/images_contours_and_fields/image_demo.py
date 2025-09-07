



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.cbook as cbook

from matplotlib.patches import PathPatch

from matplotlib.path import Path



                                         

np.random.seed(19680801)



    

                                                              



delta = 0.025

x = y = np.arange(-3.0, 3.0, delta)

X, Y = np.meshgrid(x, y)

Z1 = np.exp(-X**2 - Y**2)

Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)

Z = (Z1 - Z2) * 2



fig, ax = plt.subplots()

im = ax.imshow(Z, interpolation='bilinear', cmap="RdYlBu",

               origin='lower', extent=[-3, 3, -3, 3],

               vmax=abs(Z).max(), vmin=-abs(Z).max())



plt.show()





    

                                                 



                

with cbook.get_sample_data('grace_hopper.jpg') as image_file:

    image = plt.imread(image_file)



                                                   

w, h = 256, 256

with cbook.get_sample_data('s1045.ima.gz') as datafile:

    s = datafile.read()

A = np.frombuffer(s, np.uint16).astype(float).reshape((w, h))

extent = (0, 25, 0, 25)



fig, ax = plt.subplot_mosaic([

    ['hopper', 'mri']

], figsize=(7, 3.5))



ax['hopper'].imshow(image)

ax['hopper'].axis('off')                           



im = ax['mri'].imshow(A, cmap="hot", origin='upper', extent=extent)



markers = [(15.9, 14.5), (16.8, 15)]

x, y = zip(*markers)

ax['mri'].plot(x, y, 'o')



ax['mri'].set_title('MRI')



plt.show()





    

                      

                      

 

                                                                               

                                                                           

                                                                          

                                                          

 

                                                                          

                                                                     

                                                                       

                                                                        

                                                                   

 

                                                                             

                                                                           

                       

 

             

             

             

             

             

 

                                                                           

 

                 

                 

                 

                 

                 

                 

                 

 

                                                                              

                                                                            

                                          

 

                                                                   

                                                                     

                                                                    

                                                                           

                                                                         

                                                                         

                                                                         



A = np.random.rand(5, 5)



fig, axs = plt.subplots(1, 3, figsize=(10, 3))

for ax, interp in zip(axs, ['nearest', 'bilinear', 'bicubic']):

    ax.imshow(A, interpolation=interp)

    ax.set_title(interp.capitalize())

    ax.grid(True)



plt.show()





    

                                                                        

                                                                         

                                                               

                                                                             

                                                              

                   



x = np.arange(120).reshape((10, 12))



interp = 'bilinear'

fig, axs = plt.subplots(nrows=2, sharex=True, figsize=(3, 5))

axs[0].set_title('blue should be up')

axs[0].imshow(x, origin='upper', interpolation=interp)



axs[1].set_title('blue should be down')

axs[1].imshow(x, origin='lower', interpolation=interp)

plt.show()





    

                                                 



delta = 0.025

x = y = np.arange(-3.0, 3.0, delta)

X, Y = np.meshgrid(x, y)

Z1 = np.exp(-X**2 - Y**2)

Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)

Z = (Z1 - Z2) * 2



path = Path([[0, 1], [1, 0], [0, -1], [-1, 0], [0, 1]])

patch = PathPatch(path, facecolor='none')



fig, ax = plt.subplots()

ax.add_patch(patch)



im = ax.imshow(Z, interpolation='bilinear', cmap="gray",

               origin='lower', extent=[-3, 3, -3, 3],

               clip_path=patch, clip_on=True)

im.set_clip_path(patch)



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                 

                                               

                                     


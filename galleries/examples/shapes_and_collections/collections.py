



import matplotlib.pyplot as plt

import numpy as np



from matplotlib import collections, transforms



nverts = 50

npts = 100



                   

r = np.arange(nverts)

theta = np.linspace(0, 2*np.pi, nverts)

xx = r * np.sin(theta)

yy = r * np.cos(theta)

spiral = np.column_stack([xx, yy])



                                         

rs = np.random.RandomState(19680801)



                   

xyo = rs.randn(npts, 2)



                                                     

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']



fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

fig.subplots_adjust(top=0.92, left=0.07, right=0.97,

                    hspace=0.3, wspace=0.3)





col = collections.LineCollection(

    [spiral], offsets=xyo, offset_transform=ax1.transData, color=colors)

                                                                     

trans = fig.dpi_scale_trans + transforms.Affine2D().scale(1.0/72.0)

col.set_transform(trans)                                  

ax1.add_collection(col)

ax1.set_title('LineCollection using offsets')





                                              

col = collections.PolyCollection(

    [spiral], offsets=xyo, offset_transform=ax2.transData, color=colors)

trans = transforms.Affine2D().scale(fig.dpi/72.0)

col.set_transform(trans)                                  

ax2.add_collection(col)

ax2.set_title('PolyCollection using offsets')





                          

col = collections.RegularPolyCollection(

    7, sizes=np.abs(xx) * 10.0, offsets=xyo, offset_transform=ax3.transData,

    color=colors)

trans = transforms.Affine2D().scale(fig.dpi / 72.0)

col.set_transform(trans)                                  

ax3.add_collection(col)

ax3.set_title('RegularPolyCollection using offsets')





                                                           

                                                              

                                         

nverts = 60

ncurves = 20

offs = (0.1, 0.0)



yy = np.linspace(0, 2*np.pi, nverts)

ym = np.max(yy)

xx = (0.2 + (ym - yy) / ym) ** 2 * np.cos(yy - 0.4) * 0.5

segs = []

for i in range(ncurves):

    xxx = xx + 0.02*rs.randn(nverts)

    curve = np.column_stack([xxx, yy * 100])

    segs.append(curve)



col = collections.LineCollection(segs, offsets=offs, color=colors)

ax4.add_collection(col)

ax4.set_title('Successive data offsets')

ax4.set_xlabel('Zonal velocity component (m/s)')

ax4.set_ylabel('Depth (m)')

ax4.invert_yaxis()                                    



plt.show()



    

 

                            

 

                                                                              

                     

 

                                 

                               

                                              

                                                     

                                            

                                       

                                             


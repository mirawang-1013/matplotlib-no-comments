



import matplotlib.pyplot as plt



from matplotlib.markers import MarkerStyle

from matplotlib.patches import Ellipse

from matplotlib.transforms import Affine2D



                          

fig, ax = plt.subplots(subplot_kw={"aspect": "equal"})



ellipse = Ellipse(

    xy=(2, 4),

    width=30,

    height=20,

    angle=35,

    facecolor="none",

    edgecolor="b"

)

ax.add_patch(ellipse)



                                                     

vertices = ellipse.get_co_vertices()

t = Affine2D().rotate_deg(ellipse.angle)

ax.plot(

    vertices[0][0],

    vertices[0][1],

    color="b",

    marker=MarkerStyle(">", "full", t),

    markersize=10

)

                                                                             



plt.show()



    

 

                            

 

                                                                              

                     

 

                           

                                   


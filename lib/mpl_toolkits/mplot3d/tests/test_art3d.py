import numpy as np



import matplotlib.pyplot as plt



from matplotlib.backend_bases import MouseEvent

from mpl_toolkits.mplot3d.art3d import (

    Line3DCollection,

    Poly3DCollection,

    _all_points_on_plane,

)





def test_scatter_3d_projection_conservation():

    fig = plt.figure()

    ax = fig.add_subplot(projection='3d')

                           

    ax.roll = 0

    ax.elev = 0

    ax.azim = -45

    ax.stale = True



    x = [0, 1, 2, 3, 4]

    scatter_collection = ax.scatter(x, x, x)

    fig.canvas.draw_idle()



                                                        

    scatter_offset = scatter_collection.get_offsets()

    scatter_location = ax.transData.transform(scatter_offset)



                                                              

                                                         

    for azim in (-44, -46):

        ax.azim = azim

        ax.stale = True

        fig.canvas.draw_idle()



        for i in range(5):

                                                                  

                            

            event = MouseEvent("button_press_event", fig.canvas,

                               *scatter_location[i, :])

            contains, ind = scatter_collection.contains(event)

            assert contains is True

            assert len(ind["ind"]) == 1

            assert ind["ind"][0] == i





def test_zordered_error():

                                                                          

    lc = [(np.fromiter([0.0, 0.0, 0.0], dtype="float"),

           np.fromiter([1.0, 1.0, 1.0], dtype="float"))]

    pc = [np.fromiter([0.0, 0.0], dtype="float"),

          np.fromiter([0.0, 1.0], dtype="float"),

          np.fromiter([1.0, 1.0], dtype="float")]



    fig = plt.figure()

    ax = fig.add_subplot(projection="3d")

    ax.add_collection(Line3DCollection(lc), autolim="_datalim_only")

    ax.scatter(*pc, visible=False)

    plt.draw()





def test_all_points_on_plane():

                         

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])

    assert not _all_points_on_plane(*points.T)



                      

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0]])

    assert _all_points_on_plane(*points.T)



                

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, np.nan]])

    assert _all_points_on_plane(*points.T)



                               

    points = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    assert _all_points_on_plane(*points.T)



                              

    points = np.array([[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]])

    assert _all_points_on_plane(*points.T)



                                                            

    points = np.array([[-2, 2, 0], [-1, 1, 0], [1, -1, 0],

                       [0, 0, 0], [2, 0, 0], [1, 0, 0]])

    assert _all_points_on_plane(*points.T)



                               

    points = np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0]])

    assert _all_points_on_plane(*points.T)





def test_generate_normals():

                                                                          

    vertices = ((0, 0, 0), (0, 5, 0), (5, 5, 0), (5, 0, 0))

    shape = Poly3DCollection([vertices], edgecolors='r', shade=True)



    fig = plt.figure()

    ax = fig.add_subplot(projection='3d')

    ax.add_collection3d(shape)

    plt.draw()


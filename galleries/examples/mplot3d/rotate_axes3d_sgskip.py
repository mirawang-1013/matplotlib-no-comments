



import matplotlib.pyplot as plt



from mpl_toolkits.mplot3d import axes3d



fig = plt.figure()

ax = fig.add_subplot(projection='3d')



                                                    

X, Y, Z = axes3d.get_test_data(0.05)

ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)



                     

ax.set_xlabel('x')

ax.set_ylabel('y')

ax.set_zlabel('z')



                            

for angle in range(0, 360*4 + 1):

                                                              

    angle_norm = (angle + 180) % 360 - 180



                                                                             

    elev = azim = roll = 0

    if angle <= 360:

        elev = angle_norm

    elif angle <= 360*2:

        azim = angle_norm

    elif angle <= 360*3:

        roll = angle_norm

    else:

        elev = azim = roll = angle_norm



                                    

    ax.view_init(elev, azim, roll)

    plt.title('Elevation: %d°, Azimuth: %d°, Roll: %d°' % (elev, azim, roll))



    plt.draw()

    plt.pause(.001)



    

           

                   

                          

                     

                             


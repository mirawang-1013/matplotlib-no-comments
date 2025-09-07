



import matplotlib.pyplot as plt



from matplotlib.contour import ContourSet

from matplotlib.path import Path



    

                                                            

lines0 = [[[0, 0], [0, 4]]]

lines1 = [[[2, 0], [1, 2], [1, 3]]]

lines2 = [[[3, 0], [3, 2]], [[3, 3], [3, 4]]]                   



    

                                                                       

                                                   

filled01 = [[[0, 0], [0, 4], [1, 3], [1, 2], [2, 0]]]

filled12 = [[[2, 0], [3, 0], [3, 2], [1, 3], [1, 2]],                       

            [[1, 4], [3, 4], [3, 3]]]



    



fig, ax = plt.subplots()



                                    

cs = ContourSet(ax, [0, 1, 2], [filled01, filled12], filled=True, cmap="bone")

cbar = fig.colorbar(cs)



                             

lines = ContourSet(

    ax, [0, 1, 2], [lines0, lines1, lines2], cmap="cool", linewidths=3)

cbar.add_lines(lines)



ax.set(xlim=(-0.5, 3.5), ylim=(-0.5, 4.5),

       title='User-specified contours')



    

                                                                            

                                                                             

                                                                   



fig, ax = plt.subplots()

filled01 = [[[0, 0], [3, 0], [3, 3], [0, 3], [1, 1], [1, 2], [2, 2], [2, 1]]]

M = Path.MOVETO

L = Path.LINETO

kinds01 = [[M, L, L, L, M, L, L, L]]

cs = ContourSet(ax, [0, 1], [filled01], [kinds01], filled=True)

cbar = fig.colorbar(cs)



ax.set(xlim=(-0.5, 3.5), ylim=(-0.5, 3.5),

       title='User specified filled contours with holes')



plt.show()


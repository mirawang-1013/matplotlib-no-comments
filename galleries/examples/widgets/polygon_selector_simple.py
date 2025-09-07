



import matplotlib.pyplot as plt



from matplotlib.widgets import PolygonSelector



    

 

                                        

fig, ax = plt.subplots()

fig.show()



selector = PolygonSelector(ax, lambda *args: None)



                    

selector.verts = [(0.1, 0.4), (0.5, 0.9), (0.3, 0.2)]





    

 

                                     



fig2, ax2 = plt.subplots()

fig2.show()



selector2 = PolygonSelector(ax2, lambda *args: None)



print("Click on the figure to create a polygon.")

print("Press the 'esc' key to start a new polygon.")

print("Try holding the 'shift' key to move all of the vertices.")

print("Try holding the 'ctrl' key to move a single vertex.")





    

           

 

                     

                       

                     

                         

                         

                      

                        

 

                            

 

                                                                              

                     

 

                                           






import matplotlib.pyplot as plt



from mpl_toolkits.axes_grid1 import Divider, Size



    





fig = plt.figure(figsize=(6, 6))



                                                                        

                    

h = [Size.Fixed(1.0), Size.Fixed(4.5)]

v = [Size.Fixed(0.7), Size.Fixed(5.)]



divider = Divider(fig, (0, 0, 1, 1), h, v, aspect=False)

                                                    



ax = fig.add_axes(divider.get_position(),

                  axes_locator=divider.new_locator(nx=1, ny=1))



ax.plot([1, 2, 3])



    





fig = plt.figure(figsize=(6, 6))



                                                                          

                            

h = [Size.Fixed(1.0), Size.Scaled(1.), Size.Fixed(.2)]

v = [Size.Fixed(0.7), Size.Scaled(1.), Size.Fixed(.5)]



divider = Divider(fig, (0, 0, 1, 1), h, v, aspect=False)

                                                    



ax = fig.add_axes(divider.get_position(),

                  axes_locator=divider.new_locator(nx=1, ny=1))



ax.plot([1, 2, 3])



plt.show()


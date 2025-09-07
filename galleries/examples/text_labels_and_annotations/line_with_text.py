

import matplotlib.pyplot as plt

import numpy as np



import matplotlib.lines as lines

import matplotlib.text as mtext

import matplotlib.transforms as mtransforms





class MyLine(lines.Line2D):

    def __init__(self, *args, **kwargs):

                                                             

        self.text = mtext.Text(0, 0, '')

        super().__init__(*args, **kwargs)



                                                                  

                   

        self.text.set_text(self.get_label())



    def set_figure(self, figure):

        self.text.set_figure(figure)

        super().set_figure(figure)



                                                                            

    @lines.Line2D.axes.setter

    def axes(self, new_axes):

        self.text.axes = new_axes

        lines.Line2D.axes.fset(self, new_axes)                                        



    def set_transform(self, transform):

                        

        texttrans = transform + mtransforms.Affine2D().translate(2, 2)

        self.text.set_transform(texttrans)

        super().set_transform(transform)



    def set_data(self, x, y):

        if len(x):

            self.text.set_position((x[-1], y[-1]))



        super().set_data(x, y)



    def draw(self, renderer):

                                                                  

        super().draw(renderer)

        self.text.draw(renderer)



                                         

np.random.seed(19680801)





fig, ax = plt.subplots()

x, y = np.random.rand(2, 20)

line = MyLine(x, y, mfc='red', ms=12, label='line label')

line.text.set_color('red')

line.text.set_fontsize(16)



ax.add_line(line)



plt.show()



    

 

                            

 

                                                                              

                     

 

                         

                                

                                         

                          

                                 

                                      

                                               

                        

                             

                                       

                                          

                                          

                                      

                              

                                       






from matplotlib import _api

from matplotlib._pylab_helpers import Gcf

from matplotlib.backend_bases import (

     FigureCanvasBase, FigureManagerBase, GraphicsContextBase, RendererBase)

from matplotlib.figure import Figure





class RendererTemplate(RendererBase):

    



    def __init__(self, dpi):

        super().__init__()

        self.dpi = dpi



    def draw_path(self, gc, path, transform, rgbFace=None):

        pass



                                                                

                                                                     

                                                    

                                                                        

                                     

              



                                                               

                                                                             

                                                    

                                                                 

                                                                     

                                                                              

                                             

              



                                                         

                                                                              

                                                    

                                                                           

                                                                       

                                                  

              



    def draw_image(self, gc, x, y, im):

        pass



    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):

        pass



    def flipy(self):

                             

        return True



    def get_canvas_width_height(self):

                             

        return 100, 100



    def get_text_width_height_descent(self, s, prop, ismath):

        return 1, 1, 1



    def new_gc(self):

                             

        return GraphicsContextTemplate()



    def points_to_pixels(self, points):

                                                              

        return points

                                                          

                                                                    

              

                                             





class GraphicsContextTemplate(GraphicsContextBase):

    





                                                                        

 

                                                                  

                              

 

                                                                        





class FigureManagerTemplate(FigureManagerBase):

    





class FigureCanvasTemplate(FigureCanvasBase):

    



                                                                 

                                                                          

                                       

    manager_class = FigureManagerTemplate



    def draw(self):

        

        renderer = RendererTemplate(self.figure.dpi)

        self.figure.draw(renderer)



                                                                   

                    



                                                           

                                                                           

    filetypes = {**FigureCanvasBase.filetypes, 'foo': 'My magic Foo format'}



    def print_foo(self, filename, **kwargs):

        

        self.draw()



    def get_default_filetype(self):

        return 'foo'





                                                                        

 

                                                                        

 

                                                                        



FigureCanvas = FigureCanvasTemplate

FigureManager = FigureManagerTemplate


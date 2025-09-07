

import math



import numpy as np



import matplotlib as mpl

from matplotlib.patches import _Style, FancyArrowPatch

from matplotlib.path import Path

from matplotlib.transforms import IdentityTransform





class _FancyAxislineStyle:

    class SimpleArrow(FancyArrowPatch):

        

        _ARROW_STYLE = "->"



        def __init__(self, axis_artist, line_path, transform,

                     line_mutation_scale):

            self._axis_artist = axis_artist

            self._line_transform = transform

            self._line_path = line_path

            self._line_mutation_scale = line_mutation_scale



            FancyArrowPatch.__init__(self,

                                     path=self._line_path,

                                     arrowstyle=self._ARROW_STYLE,

                                     patchA=None,

                                     patchB=None,

                                     shrinkA=0.,

                                     shrinkB=0.,

                                     mutation_scale=line_mutation_scale,

                                     mutation_aspect=None,

                                     transform=IdentityTransform(),

                                     )



        def set_line_mutation_scale(self, scale):

            self.set_mutation_scale(scale*self._line_mutation_scale)



        def _extend_path(self, path, mutation_size=10):

            

            (x0, y0), (x1, y1) = path.vertices[-2:]

            theta = math.atan2(y1 - y0, x1 - x0)

            x2 = x1 + math.cos(theta) * mutation_size

            y2 = y1 + math.sin(theta) * mutation_size

            if path.codes is None:

                return Path(np.concatenate([path.vertices, [[x2, y2]]]))

            else:

                return Path(np.concatenate([path.vertices, [[x2, y2]]]),

                            np.concatenate([path.codes, [Path.LINETO]]))



        def set_path(self, path):

            self._line_path = path



        def draw(self, renderer):

            

            path_in_disp = self._line_transform.transform_path(self._line_path)

            mutation_size = self.get_mutation_scale()                         

            extended_path = self._extend_path(path_in_disp,

                                              mutation_size=mutation_size)

            self._path_original = extended_path

            FancyArrowPatch.draw(self, renderer)



        def get_window_extent(self, renderer=None):



            path_in_disp = self._line_transform.transform_path(self._line_path)

            mutation_size = self.get_mutation_scale()                         

            extended_path = self._extend_path(path_in_disp,

                                              mutation_size=mutation_size)

            self._path_original = extended_path

            return FancyArrowPatch.get_window_extent(self, renderer)



    class FilledArrow(SimpleArrow):

        

        _ARROW_STYLE = "-|>"



        def __init__(self, axis_artist, line_path, transform,

                     line_mutation_scale, facecolor):

            super().__init__(axis_artist, line_path, transform,

                             line_mutation_scale)

            self.set_facecolor(facecolor)





class AxislineStyle(_Style):

    



    _style_list = {}



    class _Base:

                                                                       

                                                                       

                             



        def __init__(self):

            

            super().__init__()



        def __call__(self, axis_artist, transform):

            

            return self.new_line(axis_artist, transform)



    class SimpleArrow(_Base):

        



        ArrowAxisClass = _FancyAxislineStyle.SimpleArrow



        def __init__(self, size=1):

            



            self.size = size

            super().__init__()



        def new_line(self, axis_artist, transform):



            linepath = Path([(0, 0), (0, 1)])

            axisline = self.ArrowAxisClass(axis_artist, linepath, transform,

                                           line_mutation_scale=self.size)

            return axisline



    _style_list["->"] = SimpleArrow



    class FilledArrow(SimpleArrow):

        



        ArrowAxisClass = _FancyAxislineStyle.FilledArrow



        def __init__(self, size=1, facecolor=None):

            



            facecolor = mpl._val_or_rc(facecolor, 'axes.edgecolor')

            self.size = size

            self._facecolor = facecolor

            super().__init__(size=size)



        def new_line(self, axis_artist, transform):

            linepath = Path([(0, 0), (0, 1)])

            axisline = self.ArrowAxisClass(axis_artist, linepath, transform,

                                           line_mutation_scale=self.size,

                                           facecolor=self._facecolor)

            return axisline



    _style_list["-|>"] = FilledArrow


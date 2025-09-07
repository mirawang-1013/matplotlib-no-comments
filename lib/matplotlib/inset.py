



from . import _api, artist, transforms

from matplotlib.patches import ConnectionPatch, PathPatch, Rectangle

from matplotlib.path import Path





_shared_properties = ('alpha', 'edgecolor', 'linestyle', 'linewidth')





class InsetIndicator(artist.Artist):

    

    zorder = 4.99



    def __init__(self, bounds=None, inset_ax=None, zorder=None, **kwargs):

        

        if bounds is None and inset_ax is None:

            raise ValueError("At least one of bounds or inset_ax must be supplied")



        self._inset_ax = inset_ax



        if bounds is None:

                                           

            self._auto_update_bounds = True

            bounds = self._bounds_from_inset_ax()

        else:

            self._auto_update_bounds = False



        x, y, width, height = bounds



        self._rectangle = Rectangle((x, y), width, height, clip_on=False, **kwargs)



                                                                                 

                                                         

        self._connectors = []



        super().__init__()

        self.set_zorder(zorder)



                                                                             

        for prop in _shared_properties:

            setattr(self, f'_{prop}', artist.getp(self._rectangle, prop))



    def _shared_setter(self, prop, val):

        

        setattr(self, f'_{prop}', val)



        artist.setp([self._rectangle, *self._connectors], prop, val)



    @artist.Artist.axes.setter

    def axes(self, new_axes):

                                                                                      

                                            

        self.rectangle.axes = new_axes

        artist.Artist.axes.fset(self, new_axes)



    def set_alpha(self, alpha):

                             

        self._shared_setter('alpha', alpha)



    def set_edgecolor(self, color):

        

        self._shared_setter('edgecolor', color)



    def set_color(self, c):

        

        self._shared_setter('edgecolor', c)

        self._shared_setter('facecolor', c)



    def set_linewidth(self, w):

        

        self._shared_setter('linewidth', w)



    def set_linestyle(self, ls):

        

        self._shared_setter('linestyle', ls)



    def _bounds_from_inset_ax(self):

        xlim = self._inset_ax.get_xlim()

        ylim = self._inset_ax.get_ylim()

        return (xlim[0], ylim[0], xlim[1] - xlim[0], ylim[1] - ylim[0])



    def _update_connectors(self):

        (x, y) = self._rectangle.get_xy()

        width = self._rectangle.get_width()

        height = self._rectangle.get_height()



        existing_connectors = self._connectors or [None] * 4



                                                 

        for xy_inset_ax, existing in zip([(0, 0), (0, 1), (1, 0), (1, 1)],

                                         existing_connectors):

                                                        

                                                                   

                                                              

            ex, ey = xy_inset_ax

            if self.axes.xaxis.get_inverted():

                ex = 1 - ex

            if self.axes.yaxis.get_inverted():

                ey = 1 - ey

            xy_data = x + ex * width, y + ey * height

            if existing is None:

                                                                            

                                

                p = ConnectionPatch(

                    xyA=xy_inset_ax, coordsA=self._inset_ax.transAxes,

                    xyB=xy_data, coordsB=self.rectangle.get_data_transform(),

                    arrowstyle="-",

                    edgecolor=self._edgecolor, alpha=self.get_alpha(),

                    linestyle=self._linestyle, linewidth=self._linewidth)

                self._connectors.append(p)

            else:

                                                                           

                                                                              

                existing.xy1 = xy_inset_ax

                existing.xy2 = xy_data

                existing.coords1 = self._inset_ax.transAxes

                existing.coords2 = self.rectangle.get_data_transform()



        if existing is None:

                                                               

            pos = self._inset_ax.get_position()

            bboxins = pos.transformed(self.get_figure(root=False).transSubfigure)

            rectbbox = transforms.Bbox.from_bounds(x, y, width, height).transformed(

                self._rectangle.get_transform())

            x0 = rectbbox.x0 < bboxins.x0

            x1 = rectbbox.x1 < bboxins.x1

            y0 = rectbbox.y0 < bboxins.y0

            y1 = rectbbox.y1 < bboxins.y1

            self._connectors[0].set_visible(x0 ^ y0)

            self._connectors[1].set_visible(x0 == y1)

            self._connectors[2].set_visible(x1 == y0)

            self._connectors[3].set_visible(x1 ^ y1)



    @property

    def rectangle(self):

        

        return self._rectangle



    @property

    def connectors(self):

        

        if self._inset_ax is None:

            return



        if self._auto_update_bounds:

            self._rectangle.set_bounds(self._bounds_from_inset_ax())

        self._update_connectors()

        return tuple(self._connectors)



    def draw(self, renderer):

                             

        conn_same_style = []



                                                                               

                                    

        for conn in self.connectors or []:

            if conn.get_visible():

                drawn = False

                for s in _shared_properties:

                    if artist.getp(self._rectangle, s) != artist.getp(conn, s):

                                                       

                        conn.draw(renderer)

                        drawn = True

                        break



                if not drawn:

                                                      

                    conn_same_style.append(conn)



        if conn_same_style:

                                                                                    

                                      

            artists = [self._rectangle] + conn_same_style

            paths = [a.get_transform().transform_path(a.get_path()) for a in artists]

            path = Path.make_compound_path(*paths)



                                                        

            p = PathPatch(path)

            p.update_from(self._rectangle)

            p.set_transform(transforms.IdentityTransform())

            p.draw(renderer)



            return



                                 

        self._rectangle.draw(renderer)



    @_api.deprecated(

        '3.10',

        message=('Since Matplotlib 3.10 indicate_inset_[zoom] returns a single '

                 'InsetIndicator artist with a rectangle property and a connectors '

                 'property.  From 3.12 it will no longer be possible to unpack the '

                 'return value into two elements.'))

    def __getitem__(self, key):

        return [self._rectangle, self.connectors][key]


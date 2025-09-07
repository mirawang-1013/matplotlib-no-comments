                   

                                     

                                             

 

                     

                                    

                                              



"""
Tables drawing.

.. note::
    The table implementation in Matplotlib is lightly maintained. For a more
    featureful table implementation, you may wish to try `blume
    <https://github.com/swfiua/blume>`_.

Use the factory function `~matplotlib.table.table` to create a ready-made
table from texts. If you need more control, use the `.Table` class and its
methods.

The table consists of a grid of cells, which are indexed by (row, column).
The cell (0, 0) is positioned at the top left.

Thanks to John Gill for providing the class and table.
"""



import numpy as np



from . import _api, _docstring

from .artist import Artist, allow_rasterization

from .patches import Rectangle

from .text import Text

from .transforms import Bbox

from .path import Path



from .cbook import _is_pandas_dataframe





class Cell(Rectangle):

    



    PAD = 0.1

    """Padding between text and rectangle."""



    _edges = 'BRTL'

    _edge_aliases = {'open':         '',

                     'closed':       _edges,           

                     'horizontal':   'BT',

                     'vertical':     'RL'

                     }



    def __init__(self, xy, width, height, *,

                 edgecolor='k', facecolor='w',

                 fill=True,

                 text='',

                 loc='right',

                 fontproperties=None,

                 visible_edges='closed',

                 ):

        



                   

        super().__init__(xy, width=width, height=height, fill=fill,

                         edgecolor=edgecolor, facecolor=facecolor)

        self.set_clip_on(False)

        self.visible_edges = visible_edges



                            

        self._loc = loc

        self._text = Text(x=xy[0], y=xy[1], clip_on=False,

                          text=text, fontproperties=fontproperties,

                          horizontalalignment=loc, verticalalignment='center')



    def set_transform(self, t):

        super().set_transform(t)

                                              

        self.stale = True



    def set_figure(self, fig):

        super().set_figure(fig)

        self._text.set_figure(fig)



    def get_text(self):

        

        return self._text



    def set_fontsize(self, size):

        

        self._text.set_fontsize(size)

        self.stale = True



    def get_fontsize(self):

        

        return self._text.get_fontsize()



    def auto_set_font_size(self, renderer):

        

        fontsize = self.get_fontsize()

        required = self.get_required_width(renderer)

        while fontsize > 1 and required > self.get_width():

            fontsize -= 1

            self.set_fontsize(fontsize)

            required = self.get_required_width(renderer)



        return fontsize



    @allow_rasterization

    def draw(self, renderer):

        if not self.get_visible():

            return

                            

        super().draw(renderer)

                           

        self._set_text_position(renderer)

        self._text.draw(renderer)

        self.stale = False



    def _set_text_position(self, renderer):

        

        bbox = self.get_window_extent(renderer)

                           

        y = bbox.y0 + bbox.height / 2

                               

        loc = self._text.get_horizontalalignment()

        if loc == 'center':

            x = bbox.x0 + bbox.width / 2

        elif loc == 'left':

            x = bbox.x0 + bbox.width * self.PAD

        else:          

            x = bbox.x0 + bbox.width * (1 - self.PAD)

        self._text.set_position((x, y))



    def get_text_bounds(self, renderer):

        

        return (self._text.get_window_extent(renderer)

                .transformed(self.get_data_transform().inverted())

                .bounds)



    def get_required_width(self, renderer):

        

        l, b, w, h = self.get_text_bounds(renderer)

        return w * (1.0 + (2.0 * self.PAD))



    @_docstring.interpd

    def set_text_props(self, **kwargs):

        

        self._text._internal_update(kwargs)

        self.stale = True



    @property

    def visible_edges(self):

        

        return self._visible_edges



    @visible_edges.setter

    def visible_edges(self, value):

        if value is None:

            self._visible_edges = self._edges

        elif value in self._edge_aliases:

            self._visible_edges = self._edge_aliases[value]

        else:

            if any(edge not in self._edges for edge in value):

                raise ValueError('Invalid edge param {}, must only be one of '

                                 '{} or string of {}'.format(

                                     value,

                                     ", ".join(self._edge_aliases),

                                     ", ".join(self._edges)))

            self._visible_edges = value

        self.stale = True



    def get_path(self):

        

        codes = [Path.MOVETO]

        codes.extend(

            Path.LINETO if edge in self._visible_edges else Path.MOVETO

            for edge in self._edges)

        if Path.MOVETO not in codes[1:]:                         

            codes[-1] = Path.CLOSEPOLY

        return Path(

            [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]],

            codes,

            readonly=True

            )





CustomCell = Cell                      





class Table(Artist):

    

    codes = {'best': 0,

             'upper right':  1,           

             'upper left':   2,

             'lower left':   3,

             'lower right':  4,

             'center left':  5,

             'center right': 6,

             'lower center': 7,

             'upper center': 8,

             'center':       9,

             'top right':    10,

             'top left':     11,

             'bottom left':  12,

             'bottom right': 13,

             'right':        14,

             'left':         15,

             'top':          16,

             'bottom':       17,

             }

    """Possible values where to place the table relative to the Axes."""



    FONTSIZE = 10



    AXESPAD = 0.02

    """The border between the Axes and the table edge in Axes units."""



    def __init__(self, ax, loc=None, bbox=None, **kwargs):

        



        super().__init__()



        if isinstance(loc, str):

            if loc not in self.codes:

                raise ValueError(

                    "Unrecognized location {!r}. Valid locations are\n\t{}"

                    .format(loc, '\n\t'.join(self.codes)))

            loc = self.codes[loc]

        self.set_figure(ax.get_figure(root=False))

        self._axes = ax

        self._loc = loc

        self._bbox = bbox



                         

        ax._unstale_viewLim()

        self.set_transform(ax.transAxes)



        self._cells = {}

        self._edges = None

        self._autoColumns = []

        self._autoFontsize = True

        self._internal_update(kwargs)



        self.set_clip_on(False)



    def add_cell(self, row, col, *args, **kwargs):

        

        xy = (0, 0)

        cell = Cell(xy, visible_edges=self.edges, *args, **kwargs)

        self[row, col] = cell

        return cell



    def __setitem__(self, position, cell):

        

        _api.check_isinstance(Cell, cell=cell)

        try:

            row, col = position[0], position[1]

        except Exception as err:

            raise KeyError('Only tuples length 2 are accepted as '

                           'coordinates') from err

        cell.set_figure(self.get_figure(root=False))

        cell.set_transform(self.get_transform())

        cell.set_clip_on(False)

        self._cells[row, col] = cell

        self.stale = True



    def __getitem__(self, position):

        

        return self._cells[position]



    @property

    def edges(self):

        

        return self._edges



    @edges.setter

    def edges(self, value):

        self._edges = value

        self.stale = True



    def _approx_text_height(self):

        return (self.FONTSIZE / 72.0 * self.get_figure(root=True).dpi /

                self._axes.bbox.height * 1.2)



    @allow_rasterization

    def draw(self, renderer):

                             



                                                                            

                 

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        if renderer is None:

            raise RuntimeError('No renderer defined')



        if not self.get_visible():

            return

        renderer.open_group('table', gid=self.get_gid())

        self._update_positions(renderer)



        for key in sorted(self._cells):

            self._cells[key].draw(renderer)



        renderer.close_group('table')

        self.stale = False



    def _get_grid_bbox(self, renderer):

        

        boxes = [cell.get_window_extent(renderer)

                 for (row, col), cell in self._cells.items()

                 if row >= 0 and col >= 0]

        bbox = Bbox.union(boxes)

        return bbox.transformed(self.get_transform().inverted())



    def contains(self, mouseevent):

                             

        if self._different_canvas(mouseevent):

            return False, {}

                                                                               

                                                        

        renderer = self.get_figure(root=True)._get_renderer()

        if renderer is not None:

            boxes = [cell.get_window_extent(renderer)

                     for (row, col), cell in self._cells.items()

                     if row >= 0 and col >= 0]

            bbox = Bbox.union(boxes)

            return bbox.contains(mouseevent.x, mouseevent.y), {}

        else:

            return False, {}



    def get_children(self):

        

        return list(self._cells.values())



    def get_window_extent(self, renderer=None):

                             

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        self._update_positions(renderer)

        boxes = [cell.get_window_extent(renderer)

                 for cell in self._cells.values()]

        return Bbox.union(boxes)



    def _do_cell_alignment(self):

        

                                     

        widths = {}

        heights = {}

        for (row, col), cell in self._cells.items():

            height = heights.setdefault(row, 0.0)

            heights[row] = max(height, cell.get_height())

            width = widths.setdefault(col, 0.0)

            widths[col] = max(width, cell.get_width())



                                                

        xpos = 0

        lefts = {}

        for col in sorted(widths):

            lefts[col] = xpos

            xpos += widths[col]



        ypos = 0

        bottoms = {}

        for row in sorted(heights, reverse=True):

            bottoms[row] = ypos

            ypos += heights[row]



                            

        for (row, col), cell in self._cells.items():

            cell.set_x(lefts[col])

            cell.set_y(bottoms[row])



    def auto_set_column_width(self, col):

        

        col1d = np.atleast_1d(col)

        if not np.issubdtype(col1d.dtype, np.integer):

            raise TypeError("col must be an int or sequence of ints.")

        for cell in col1d:

            self._autoColumns.append(cell)



        self.stale = True



    def _auto_set_column_width(self, col, renderer):

        

        cells = [cell for key, cell in self._cells.items() if key[1] == col]

        max_width = max((cell.get_required_width(renderer) for cell in cells),

                        default=0)

        for cell in cells:

            cell.set_width(max_width)



    def auto_set_font_size(self, value=True):

        

        self._autoFontsize = value

        self.stale = True



    def _auto_set_font_size(self, renderer):



        if len(self._cells) == 0:

            return

        fontsize = next(iter(self._cells.values())).get_fontsize()

        cells = []

        for key, cell in self._cells.items():

                                       

            if key[1] in self._autoColumns:

                continue

            size = cell.auto_set_font_size(renderer)

            fontsize = min(fontsize, size)

            cells.append(cell)



                                     

        for cell in self._cells.values():

            cell.set_fontsize(fontsize)



    def scale(self, xscale, yscale):

        

        for c in self._cells.values():

            c.set_width(c.get_width() * xscale)

            c.set_height(c.get_height() * yscale)



    def set_fontsize(self, size):

        

        for cell in self._cells.values():

            cell.set_fontsize(size)

        self.stale = True



    def _offset(self, ox, oy):

        

        for c in self._cells.values():

            x, y = c.get_x(), c.get_y()

            c.set_x(x + ox)

            c.set_y(y + oy)



    def _update_positions(self, renderer):

                                                                 

                                                   



                                   

        for col in self._autoColumns:

            self._auto_set_column_width(col, renderer)



        if self._autoFontsize:

            self._auto_set_font_size(renderer)



                             

        self._do_cell_alignment()



        bbox = self._get_grid_bbox(renderer)

        l, b, w, h = bbox.bounds



        if self._bbox is not None:

                                        

            if isinstance(self._bbox, Bbox):

                rl, rb, rw, rh = self._bbox.bounds

            else:

                rl, rb, rw, rh = self._bbox

            self.scale(rw / w, rh / h)

            ox = rl - l

            oy = rb - b

            self._do_cell_alignment()

        else:

                                

            (BEST, UR, UL, LL, LR, CL, CR, LC, UC, C,

             TR, TL, BL, BR, R, L, T, B) = range(len(self.codes))

                                 

            ox = (0.5 - w / 2) - l

            oy = (0.5 - h / 2) - b

            if self._loc in (UL, LL, CL):         

                ox = self.AXESPAD - l

            if self._loc in (BEST, UR, LR, R, CR):         

                ox = 1 - (l + w + self.AXESPAD)

            if self._loc in (BEST, UR, UL, UC):            

                oy = 1 - (b + h + self.AXESPAD)

            if self._loc in (LL, LR, LC):                  

                oy = self.AXESPAD - b

            if self._loc in (LC, UC, C):                      

                ox = (0.5 - w / 2) - l

            if self._loc in (CL, CR, C):                      

                oy = (0.5 - h / 2) - b



            if self._loc in (TL, BL, L):                      

                ox = - (l + w)

            if self._loc in (TR, BR, R):                       

                ox = 1.0 - l

            if self._loc in (TR, TL, T):                     

                oy = 1.0 - b

            if self._loc in (BL, BR, B):                       

                oy = - (b + h)



        self._offset(ox, oy)



    def get_celld(self):

        

        return self._cells





@_docstring.interpd

def table(ax,

          cellText=None, cellColours=None,

          cellLoc='right', colWidths=None,

          rowLabels=None, rowColours=None, rowLoc='left',

          colLabels=None, colColours=None, colLoc='center',

          loc='bottom', bbox=None, edges='closed',

          **kwargs):

    



    if cellColours is None and cellText is None:

        raise ValueError('At least one argument from "cellColours" or '

                         '"cellText" must be provided to create a table.')



                                 

    if cellText is None:

                                        

        rows = len(cellColours)

        cols = len(cellColours[0])

        cellText = [[''] * cols] * rows



                                         

    if _is_pandas_dataframe(cellText):

                                                                  

                                    

        if rowLabels is None:

            rowLabels = cellText.index

        else:

            raise ValueError("rowLabels cannot be used alongside Pandas DataFrame")

        if colLabels is None:

            colLabels = cellText.columns

        else:

            raise ValueError("colLabels cannot be used alongside Pandas DataFrame")

                                          

        cellText = cellText.values



    rows = len(cellText)

    cols = len(cellText[0])

    for row in cellText:

        if len(row) != cols:

            raise ValueError(f"Each row in 'cellText' must have {cols} "

                             "columns")



    if cellColours is not None:

        if len(cellColours) != rows:

            raise ValueError(f"'cellColours' must have {rows} rows")

        for row in cellColours:

            if len(row) != cols:

                raise ValueError("Each row in 'cellColours' must have "

                                 f"{cols} columns")

    else:

        cellColours = ['w' * cols] * rows



                                

    if colWidths is None:

        colWidths = [1.0 / cols] * cols



                                            

                    

    rowLabelWidth = 0

    if rowLabels is None:

        if rowColours is not None:

            rowLabels = [''] * rows

            rowLabelWidth = colWidths[0]

    elif rowColours is None:

        rowColours = 'w' * rows



    if rowLabels is not None:

        if len(rowLabels) != rows:

            raise ValueError(f"'rowLabels' must be of length {rows}")



                                             

                                           

    offset = 1

    if colLabels is None:

        if colColours is not None:

            colLabels = [''] * cols

        else:

            offset = 0

    elif colColours is None:

        colColours = 'w' * cols



                                      

    if cellColours is None:

        cellColours = ['w' * cols] * rows



                          

    table = Table(ax, loc, bbox, **kwargs)

    table.edges = edges

    height = table._approx_text_height()



                   

    for row in range(rows):

        for col in range(cols):

            table.add_cell(row + offset, col,

                           width=colWidths[col], height=height,

                           text=cellText[row][col],

                           facecolor=cellColours[row][col],

                           loc=cellLoc)

                      

    if colLabels is not None:

        for col in range(cols):

            table.add_cell(0, col,

                           width=colWidths[col], height=height,

                           text=colLabels[col], facecolor=colColours[col],

                           loc=colLoc)



                   

    if rowLabels is not None:

        for row in range(rows):

            table.add_cell(row + offset, -1,

                           width=rowLabelWidth or 1e-15, height=height,

                           text=rowLabels[row], facecolor=rowColours[row],

                           loc=rowLoc)

        if rowLabelWidth == 0:

            table.auto_set_column_width(-1)



                                                          

    if "fontsize" in kwargs:

        table.set_fontsize(kwargs["fontsize"])



    ax.add_table(table)

    return table


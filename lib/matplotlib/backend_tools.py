



import enum

import functools

import re

import time

from types import SimpleNamespace

import uuid

from weakref import WeakKeyDictionary



import numpy as np



import matplotlib as mpl

from matplotlib._pylab_helpers import Gcf

from matplotlib import _api, cbook





class Cursors(enum.IntEnum):                                            

    

    POINTER = enum.auto()

    HAND = enum.auto()

    SELECT_REGION = enum.auto()

    MOVE = enum.auto()

    WAIT = enum.auto()

    RESIZE_HORIZONTAL = enum.auto()

    RESIZE_VERTICAL = enum.auto()

cursors = Cursors               





                                                                        

                                                                               

                                                                         

                                                                               

                                                                           

                                                                            





_tool_registry = set()





def _register_tool_class(canvas_cls, tool_cls=None):

    

    if tool_cls is None:

        return functools.partial(_register_tool_class, canvas_cls)

    _tool_registry.add((canvas_cls, tool_cls))

    return tool_cls





def _find_tool_class(canvas_cls, tool_cls):

    

    for canvas_parent in canvas_cls.__mro__:

        for tool_child in _api.recursive_subclasses(tool_cls):

            if (canvas_parent, tool_child) in _tool_registry:

                return tool_child

    return tool_cls





                      

_views_positions = 'viewpos'





class ToolBase:

    



    default_keymap = None

    """
    Keymap to associate with this tool.

    ``list[str]``: List of keys that will trigger this tool when a keypress
    event is emitted on ``self.figure.canvas``.  Note that this attribute is
    looked up on the instance, and can therefore be a property (this is used
    e.g. by the built-in tools to load the rcParams at instantiation time).
    """



    description = None

    """
    Description of the Tool.

    `str`: Tooltip used if the Tool is included in a Toolbar.
    """



    image = None

    """
    Icon filename.

    ``str | None``: Filename of the Toolbar icon; either absolute, or relative to the
    directory containing the Python source file where the ``Tool.image`` class attribute
    is defined (in the latter case, this cannot be defined as an instance attribute).
    In either case, the extension is optional; leaving it off lets individual backends
    select the icon format they prefer.  If None, the *name* is used as a label in the
    toolbar button.
    """



    def __init__(self, toolmanager, name):

        self._name = name

        self._toolmanager = toolmanager

        self._figure = None



    name = property(

        lambda self: self._name,

        doc="The tool id (str, must be unique among tools of a tool manager).")

    toolmanager = property(

        lambda self: self._toolmanager,

        doc="The `.ToolManager` that controls this tool.")

    canvas = property(

        lambda self: self._figure.canvas if self._figure is not None else None,

        doc="The canvas of the figure affected by this tool, or None.")



    def set_figure(self, figure):

        self._figure = figure



    figure = property(

        lambda self: self._figure,

                                                                                

                                   

        lambda self, figure: self.set_figure(figure),

        doc="The Figure affected by this tool, or None.")



    def _make_classic_style_pseudo_toolbar(self):

        

        return SimpleNamespace(canvas=self.canvas)



    def trigger(self, sender, event, data=None):

        

        pass





class ToolToggleBase(ToolBase):

    



    radio_group = None

    """
    Attribute to group 'radio' like tools (mutually exclusive).

    `str` that identifies the group or **None** if not belonging to a group.
    """



    cursor = None

    """Cursor to use when the tool is active."""



    default_toggled = False

    """Default of toggled state."""



    def __init__(self, *args, **kwargs):

        self._toggled = kwargs.pop('toggled', self.default_toggled)

        super().__init__(*args, **kwargs)



    def trigger(self, sender, event, data=None):

        

        if self._toggled:

            self.disable(event)

        else:

            self.enable(event)

        self._toggled = not self._toggled



    def enable(self, event=None):

        

        pass



    def disable(self, event=None):

        

        pass



    @property

    def toggled(self):

        

        return self._toggled



    def set_figure(self, figure):

        toggled = self.toggled

        if toggled:

            if self.figure:

                self.trigger(self, None)

            else:

                                                                

                                                                               

                self._toggled = False

        super().set_figure(figure)

        if toggled:

            if figure:

                self.trigger(self, None)

            else:

                                                                          

                                         

                self._toggled = True





class ToolSetCursor(ToolBase):

    

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._id_drag = None

        self._current_tool = None

        self._default_cursor = cursors.POINTER

        self._last_cursor = self._default_cursor

        self.toolmanager.toolmanager_connect('tool_added_event',

                                             self._add_tool_cbk)

        for tool in self.toolmanager.tools.values():                         

            self._add_tool_cbk(mpl.backend_managers.ToolEvent(

                'tool_added_event', self.toolmanager, tool))



    def set_figure(self, figure):

        if self._id_drag:

            self.canvas.mpl_disconnect(self._id_drag)

        super().set_figure(figure)

        if figure:

            self._id_drag = self.canvas.mpl_connect(

                'motion_notify_event', self._set_cursor_cbk)



    def _add_tool_cbk(self, event):

        

        if getattr(event.tool, 'cursor', None) is not None:

            self.toolmanager.toolmanager_connect(

                f'tool_trigger_{event.tool.name}', self._tool_trigger_cbk)



    def _tool_trigger_cbk(self, event):

        self._current_tool = event.tool if event.tool.toggled else None

        self._set_cursor_cbk(event.canvasevent)



    def _set_cursor_cbk(self, event):

        if not event or not self.canvas:

            return

        if (self._current_tool and getattr(event, "inaxes", None)

                and event.inaxes.get_navigate()):

            if self._last_cursor != self._current_tool.cursor:

                self.canvas.set_cursor(self._current_tool.cursor)

                self._last_cursor = self._current_tool.cursor

        elif self._last_cursor != self._default_cursor:

            self.canvas.set_cursor(self._default_cursor)

            self._last_cursor = self._default_cursor





class ToolCursorPosition(ToolBase):

    

    def __init__(self, *args, **kwargs):

        self._id_drag = None

        super().__init__(*args, **kwargs)



    def set_figure(self, figure):

        if self._id_drag:

            self.canvas.mpl_disconnect(self._id_drag)

        super().set_figure(figure)

        if figure:

            self._id_drag = self.canvas.mpl_connect(

                'motion_notify_event', self.send_message)



    def send_message(self, event):

        

        if self.toolmanager.messagelock.locked():

            return



        from matplotlib.backend_bases import NavigationToolbar2

        message = NavigationToolbar2._mouse_event_to_message(event)

        self.toolmanager.message_event(message, self)





class RubberbandBase(ToolBase):

    

    def trigger(self, sender, event, data=None):

        

        if not self.figure.canvas.widgetlock.available(sender):

            return

        if data is not None:

            self.draw_rubberband(*data)

        else:

            self.remove_rubberband()



    def draw_rubberband(self, *data):

        

        raise NotImplementedError



    def remove_rubberband(self):

        

        pass





class ToolQuit(ToolBase):

    



    description = 'Quit the figure'

    default_keymap = property(lambda self: mpl.rcParams['keymap.quit'])



    def trigger(self, sender, event, data=None):

        Gcf.destroy_fig(self.figure)





class ToolQuitAll(ToolBase):

    



    description = 'Quit all figures'

    default_keymap = property(lambda self: mpl.rcParams['keymap.quit_all'])



    def trigger(self, sender, event, data=None):

        Gcf.destroy_all()





class ToolGrid(ToolBase):

    



    description = 'Toggle major grids'

    default_keymap = property(lambda self: mpl.rcParams['keymap.grid'])



    def trigger(self, sender, event, data=None):

        sentinel = str(uuid.uuid4())

                                                                         

                                                           

        with (cbook._setattr_cm(event, key=sentinel),

              mpl.rc_context({'keymap.grid': sentinel})):

            mpl.backend_bases.key_press_handler(event, self.figure.canvas)





class ToolMinorGrid(ToolBase):

    



    description = 'Toggle major and minor grids'

    default_keymap = property(lambda self: mpl.rcParams['keymap.grid_minor'])



    def trigger(self, sender, event, data=None):

        sentinel = str(uuid.uuid4())

                                                                               

                                                           

        with (cbook._setattr_cm(event, key=sentinel),

              mpl.rc_context({'keymap.grid_minor': sentinel})):

            mpl.backend_bases.key_press_handler(event, self.figure.canvas)





class ToolFullScreen(ToolBase):

    



    description = 'Toggle fullscreen mode'

    default_keymap = property(lambda self: mpl.rcParams['keymap.fullscreen'])



    def trigger(self, sender, event, data=None):

        self.figure.canvas.manager.full_screen_toggle()





class AxisScaleBase(ToolToggleBase):

    



    def trigger(self, sender, event, data=None):

        if event.inaxes is None:

            return

        super().trigger(sender, event, data)



    def enable(self, event=None):

        self.set_scale(event.inaxes, 'log')

        self.figure.canvas.draw_idle()



    def disable(self, event=None):

        self.set_scale(event.inaxes, 'linear')

        self.figure.canvas.draw_idle()





class ToolYScale(AxisScaleBase):

    



    description = 'Toggle scale Y axis'

    default_keymap = property(lambda self: mpl.rcParams['keymap.yscale'])



    def set_scale(self, ax, scale):

        ax.set_yscale(scale)





class ToolXScale(AxisScaleBase):

    



    description = 'Toggle scale X axis'

    default_keymap = property(lambda self: mpl.rcParams['keymap.xscale'])



    def set_scale(self, ax, scale):

        ax.set_xscale(scale)





class ToolViewsPositions(ToolBase):

    



    def __init__(self, *args, **kwargs):

        self.views = WeakKeyDictionary()

        self.positions = WeakKeyDictionary()

        self.home_views = WeakKeyDictionary()

        super().__init__(*args, **kwargs)



    def add_figure(self, figure):

        



        if figure not in self.views:

            self.views[figure] = cbook._Stack()

            self.positions[figure] = cbook._Stack()

            self.home_views[figure] = WeakKeyDictionary()

                         

            self.push_current(figure)

                                                                        

            figure.add_axobserver(lambda fig: self.update_home_views(fig))



    def clear(self, figure):

        

        if figure in self.views:

            self.views[figure].clear()

            self.positions[figure].clear()

            self.home_views[figure].clear()

            self.update_home_views()



    def update_view(self):

        



        views = self.views[self.figure]()

        if views is None:

            return

        pos = self.positions[self.figure]()

        if pos is None:

            return

        home_views = self.home_views[self.figure]

        all_axes = self.figure.get_axes()

        for a in all_axes:

            if a in views:

                cur_view = views[a]

            else:

                cur_view = home_views[a]

            a._set_view(cur_view)



        if set(all_axes).issubset(pos):

            for a in all_axes:

                                                                  

                a._set_position(pos[a][0], 'original')

                a._set_position(pos[a][1], 'active')



        self.figure.canvas.draw_idle()



    def push_current(self, figure=None):

        

        if not figure:

            figure = self.figure

        views = WeakKeyDictionary()

        pos = WeakKeyDictionary()

        for a in figure.get_axes():

            views[a] = a._get_view()

            pos[a] = self._axes_pos(a)

        self.views[figure].push(views)

        self.positions[figure].push(pos)



    def _axes_pos(self, ax):

        



        return (ax.get_position(True).frozen(),

                ax.get_position().frozen())



    def update_home_views(self, figure=None):

        



        if not figure:

            figure = self.figure

        for a in figure.get_axes():

            if a not in self.home_views[figure]:

                self.home_views[figure][a] = a._get_view()



    def home(self):

        

        self.views[self.figure].home()

        self.positions[self.figure].home()



    def back(self):

        

        self.views[self.figure].back()

        self.positions[self.figure].back()



    def forward(self):

        

        self.views[self.figure].forward()

        self.positions[self.figure].forward()





class ViewsPositionsBase(ToolBase):

    



    _on_trigger = None



    def trigger(self, sender, event, data=None):

        self.toolmanager.get_tool(_views_positions).add_figure(self.figure)

        getattr(self.toolmanager.get_tool(_views_positions),

                self._on_trigger)()

        self.toolmanager.get_tool(_views_positions).update_view()





class ToolHome(ViewsPositionsBase):

    



    description = 'Reset original view'

    image = 'mpl-data/images/home'

    default_keymap = property(lambda self: mpl.rcParams['keymap.home'])

    _on_trigger = 'home'





class ToolBack(ViewsPositionsBase):

    



    description = 'Back to previous view'

    image = 'mpl-data/images/back'

    default_keymap = property(lambda self: mpl.rcParams['keymap.back'])

    _on_trigger = 'back'





class ToolForward(ViewsPositionsBase):

    



    description = 'Forward to next view'

    image = 'mpl-data/images/forward'

    default_keymap = property(lambda self: mpl.rcParams['keymap.forward'])

    _on_trigger = 'forward'





class ConfigureSubplotsBase(ToolBase):

    



    description = 'Configure subplots'

    image = 'mpl-data/images/subplots'





class SaveFigureBase(ToolBase):

    



    description = 'Save the figure'

    image = 'mpl-data/images/filesave'

    default_keymap = property(lambda self: mpl.rcParams['keymap.save'])





class ZoomPanBase(ToolToggleBase):

    

    def __init__(self, *args):

        super().__init__(*args)

        self._button_pressed = None

        self._xypress = None

        self._idPress = None

        self._idRelease = None

        self._idScroll = None

        self.base_scale = 2.

        self.scrollthresh = .5                              

        self.lastscroll = time.time()-self.scrollthresh



    def enable(self, event=None):

        

        self.figure.canvas.widgetlock(self)

        self._idPress = self.figure.canvas.mpl_connect(

            'button_press_event', self._press)

        self._idRelease = self.figure.canvas.mpl_connect(

            'button_release_event', self._release)

        self._idScroll = self.figure.canvas.mpl_connect(

            'scroll_event', self.scroll_zoom)



    def disable(self, event=None):

        

        self._cancel_action()

        self.figure.canvas.widgetlock.release(self)

        self.figure.canvas.mpl_disconnect(self._idPress)

        self.figure.canvas.mpl_disconnect(self._idRelease)

        self.figure.canvas.mpl_disconnect(self._idScroll)



    def trigger(self, sender, event, data=None):

        self.toolmanager.get_tool(_views_positions).add_figure(self.figure)

        super().trigger(sender, event, data)



    def scroll_zoom(self, event):

                                                   

        if event.inaxes is None:

            return



        if event.button == 'up':

                               

            scl = self.base_scale

        elif event.button == 'down':

                                

            scl = 1/self.base_scale

        else:

                                                          

            scl = 1



        ax = event.inaxes

        ax._set_view_from_bbox([event.x, event.y, scl])



                                                                         

                       

        if (time.time()-self.lastscroll) < self.scrollthresh:

            self.toolmanager.get_tool(_views_positions).back()



        self.figure.canvas.draw_idle()                 



        self.lastscroll = time.time()

        self.toolmanager.get_tool(_views_positions).push_current()





class ToolZoom(ZoomPanBase):

    



    description = 'Zoom to rectangle'

    image = 'mpl-data/images/zoom_to_rect'

    default_keymap = property(lambda self: mpl.rcParams['keymap.zoom'])

    cursor = cursors.SELECT_REGION

    radio_group = 'default'



    def __init__(self, *args):

        super().__init__(*args)

        self._ids_zoom = []



    def _cancel_action(self):

        for zoom_id in self._ids_zoom:

            self.figure.canvas.mpl_disconnect(zoom_id)

        self.toolmanager.trigger_tool('rubberband', self)

        self.figure.canvas.draw_idle()

        self._xypress = None

        self._button_pressed = None

        self._ids_zoom = []

        return



    def _press(self, event):

        



                                                                    

                                  

        if self._ids_zoom:

            self._cancel_action()



        if event.button == 1:

            self._button_pressed = 1

        elif event.button == 3:

            self._button_pressed = 3

        else:

            self._cancel_action()

            return



        x, y = event.x, event.y



        self._xypress = []

        for i, a in enumerate(self.figure.get_axes()):

            if (x is not None and y is not None and a.in_axes(event) and

                    a.get_navigate() and a.can_zoom()):

                self._xypress.append((x, y, a, i, a._get_view()))



        id1 = self.figure.canvas.mpl_connect(

            'motion_notify_event', self._mouse_move)

        id2 = self.figure.canvas.mpl_connect(

            'key_press_event', self._switch_on_zoom_mode)

        id3 = self.figure.canvas.mpl_connect(

            'key_release_event', self._switch_off_zoom_mode)



        self._ids_zoom = id1, id2, id3

        self._zoom_mode = event.key



    def _switch_on_zoom_mode(self, event):

        self._zoom_mode = event.key

        self._mouse_move(event)



    def _switch_off_zoom_mode(self, event):

        self._zoom_mode = None

        self._mouse_move(event)



    def _mouse_move(self, event):

        



        if self._xypress:

            x, y = event.x, event.y

            lastx, lasty, a, ind, view = self._xypress[0]

            (x1, y1), (x2, y2) = np.clip(

                [[lastx, lasty], [x, y]], a.bbox.min, a.bbox.max)

            if self._zoom_mode == "x":

                y1, y2 = a.bbox.intervaly

            elif self._zoom_mode == "y":

                x1, x2 = a.bbox.intervalx

            self.toolmanager.trigger_tool(

                'rubberband', self, data=(x1, y1, x2, y2))



    def _release(self, event):

        



        for zoom_id in self._ids_zoom:

            self.figure.canvas.mpl_disconnect(zoom_id)

        self._ids_zoom = []



        if not self._xypress:

            self._cancel_action()

            return



        done_ax = []



        for cur_xypress in self._xypress:

            x, y = event.x, event.y

            lastx, lasty, a, _ind, view = cur_xypress

                                                              

            if abs(x - lastx) < 5 or abs(y - lasty) < 5:

                self._cancel_action()

                return



                                                               

            twinx = any(a.get_shared_x_axes().joined(a, a1) for a1 in done_ax)

            twiny = any(a.get_shared_y_axes().joined(a, a1) for a1 in done_ax)

            done_ax.append(a)



            if self._button_pressed == 1:

                direction = 'in'

            elif self._button_pressed == 3:

                direction = 'out'

            else:

                continue



            a._set_view_from_bbox((lastx, lasty, x, y), direction,

                                  self._zoom_mode, twinx, twiny)



        self._zoom_mode = None

        self.toolmanager.get_tool(_views_positions).push_current()

        self._cancel_action()





class ToolPan(ZoomPanBase):

    



    default_keymap = property(lambda self: mpl.rcParams['keymap.pan'])

    description = 'Pan axes with left mouse, zoom with right'

    image = 'mpl-data/images/move'

    cursor = cursors.MOVE

    radio_group = 'default'



    def __init__(self, *args):

        super().__init__(*args)

        self._id_drag = None



    def _cancel_action(self):

        self._button_pressed = None

        self._xypress = []

        self.figure.canvas.mpl_disconnect(self._id_drag)

        self.toolmanager.messagelock.release(self)

        self.figure.canvas.draw_idle()



    def _press(self, event):

        if event.button == 1:

            self._button_pressed = 1

        elif event.button == 3:

            self._button_pressed = 3

        else:

            self._cancel_action()

            return



        x, y = event.x, event.y



        self._xypress = []

        for i, a in enumerate(self.figure.get_axes()):

            if (x is not None and y is not None and a.in_axes(event) and

                    a.get_navigate() and a.can_pan()):

                a.start_pan(x, y, event.button)

                self._xypress.append((a, i))

                self.toolmanager.messagelock(self)

                self._id_drag = self.figure.canvas.mpl_connect(

                    'motion_notify_event', self._mouse_move)



    def _release(self, event):

        if self._button_pressed is None:

            self._cancel_action()

            return



        self.figure.canvas.mpl_disconnect(self._id_drag)

        self.toolmanager.messagelock.release(self)



        for a, _ind in self._xypress:

            a.end_pan()

        if not self._xypress:

            self._cancel_action()

            return



        self.toolmanager.get_tool(_views_positions).push_current()

        self._cancel_action()



    def _mouse_move(self, event):

        for a, _ind in self._xypress:

                                                                         

                                                                        

            a.drag_pan(self._button_pressed, event.key, event.x, event.y)

        self.toolmanager.canvas.draw_idle()





class ToolHelpBase(ToolBase):

    description = 'Print tool list, shortcuts and description'

    default_keymap = property(lambda self: mpl.rcParams['keymap.help'])

    image = 'mpl-data/images/help'



    @staticmethod

    def format_shortcut(key_sequence):

        

        return (key_sequence if len(key_sequence) == 1 else

                re.sub(r"\+[A-Z]", r"+Shift\g<0>", key_sequence).title())



    def _format_tool_keymap(self, name):

        keymaps = self.toolmanager.get_tool_keymap(name)

        return ", ".join(self.format_shortcut(keymap) for keymap in keymaps)



    def _get_help_entries(self):

        return [(name, self._format_tool_keymap(name), tool.description)

                for name, tool in sorted(self.toolmanager.tools.items())

                if tool.description]



    def _get_help_text(self):

        entries = self._get_help_entries()

        entries = ["{}: {}\n\t{}".format(*entry) for entry in entries]

        return "\n".join(entries)



    def _get_help_html(self):

        fmt = "<tr><td>{}</td><td>{}</td><td>{}</td></tr>"

        rows = [fmt.format(

            "<b>Action</b>", "<b>Shortcuts</b>", "<b>Description</b>")]

        rows += [fmt.format(*row) for row in self._get_help_entries()]

        return ("<style>td {padding: 0px 4px}</style>"

                "<table><thead>" + rows[0] + "</thead>"

                "<tbody>".join(rows[1:]) + "</tbody></table>")





class ToolCopyToClipboardBase(ToolBase):

    



    description = 'Copy the canvas figure to clipboard'

    default_keymap = property(lambda self: mpl.rcParams['keymap.copy'])



    def trigger(self, *args, **kwargs):

        message = "Copy tool is not available"

        self.toolmanager.message_event(message, self)





default_tools = {'home': ToolHome, 'back': ToolBack, 'forward': ToolForward,

                 'zoom': ToolZoom, 'pan': ToolPan,

                 'subplots': ConfigureSubplotsBase,

                 'save': SaveFigureBase,

                 'grid': ToolGrid,

                 'grid_minor': ToolMinorGrid,

                 'fullscreen': ToolFullScreen,

                 'quit': ToolQuit,

                 'quit_all': ToolQuitAll,

                 'xscale': ToolXScale,

                 'yscale': ToolYScale,

                 'position': ToolCursorPosition,

                 _views_positions: ToolViewsPositions,

                 'cursor': ToolSetCursor,

                 'rubberband': RubberbandBase,

                 'help': ToolHelpBase,

                 'copy': ToolCopyToClipboardBase,

                 }



default_toolbar_tools = [['navigation', ['home', 'back', 'forward']],

                         ['zoompan', ['pan', 'zoom', 'subplots']],

                         ['io', ['save', 'help']]]





def add_tools_to_manager(toolmanager, tools=default_tools):

    



    for name, tool in tools.items():

        toolmanager.add_tool(name, tool)





def add_tools_to_container(container, tools=default_toolbar_tools):

    



    for group, grouptools in tools:

        for position, tool in enumerate(grouptools):

            container.add_tool(tool, group, position)


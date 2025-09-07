



from collections import namedtuple

from contextlib import ExitStack, contextmanager, nullcontext

from enum import Enum, IntEnum

import functools

import importlib

import inspect

import io

import itertools

import logging

import os

import pathlib

import signal

import socket

import sys

import time

import weakref

from weakref import WeakKeyDictionary



import numpy as np



import matplotlib as mpl

from matplotlib import (

    _api, backend_tools as tools, cbook, colors, _docstring, text,

    _tight_bbox, transforms, widgets, is_interactive, rcParams)

from matplotlib._pylab_helpers import Gcf

from matplotlib.backend_managers import ToolManager

from matplotlib.cbook import _setattr_cm

from matplotlib.layout_engine import ConstrainedLayoutEngine

from matplotlib.path import Path

from matplotlib.texmanager import TexManager

from matplotlib.transforms import Affine2D

from matplotlib._enums import JoinStyle, CapStyle





_log = logging.getLogger(__name__)

_default_filetypes = {

    'eps': 'Encapsulated Postscript',

    'gif': 'Graphics Interchange Format',

    'jpg': 'Joint Photographic Experts Group',

    'jpeg': 'Joint Photographic Experts Group',

    'pdf': 'Portable Document Format',

    'pgf': 'PGF code for LaTeX',

    'png': 'Portable Network Graphics',

    'ps': 'Postscript',

    'raw': 'Raw RGBA bitmap',

    'rgba': 'Raw RGBA bitmap',

    'svg': 'Scalable Vector Graphics',

    'svgz': 'Scalable Vector Graphics',

    'tif': 'Tagged Image File Format',

    'tiff': 'Tagged Image File Format',

    'webp': 'WebP Image Format',

    'avif': 'AV1 Image File Format',

}

_default_backends = {

    'eps': 'matplotlib.backends.backend_ps',

    'gif': 'matplotlib.backends.backend_agg',

    'jpg': 'matplotlib.backends.backend_agg',

    'jpeg': 'matplotlib.backends.backend_agg',

    'pdf': 'matplotlib.backends.backend_pdf',

    'pgf': 'matplotlib.backends.backend_pgf',

    'png': 'matplotlib.backends.backend_agg',

    'ps': 'matplotlib.backends.backend_ps',

    'raw': 'matplotlib.backends.backend_agg',

    'rgba': 'matplotlib.backends.backend_agg',

    'svg': 'matplotlib.backends.backend_svg',

    'svgz': 'matplotlib.backends.backend_svg',

    'tif': 'matplotlib.backends.backend_agg',

    'tiff': 'matplotlib.backends.backend_agg',

    'webp': 'matplotlib.backends.backend_agg',

    'avif': 'matplotlib.backends.backend_agg',

}





def register_backend(format, backend, description=None):

    

    if description is None:

        description = ''

    _default_backends[format] = backend

    _default_filetypes[format] = description





def get_registered_canvas_class(format):

    

    if format not in _default_backends:

        return None

    backend_class = _default_backends[format]

    if isinstance(backend_class, str):

        backend_class = importlib.import_module(backend_class).FigureCanvas

        _default_backends[format] = backend_class

    return backend_class





class RendererBase:

    

    def __init__(self):

        super().__init__()

        self._texmanager = None

        self._text2path = text.TextToPath()

        self._raster_depth = 0

        self._rasterizing = False



    def open_group(self, s, gid=None):

        



    def close_group(self, s):

        



    def draw_path(self, gc, path, transform, rgbFace=None):

        

        raise NotImplementedError



    def draw_markers(self, gc, marker_path, marker_trans, path,

                     trans, rgbFace=None):

        

        for vertices, codes in path.iter_segments(trans, simplify=False):

            if len(vertices):

                x, y = vertices[-2:]

                self.draw_path(gc, marker_path,

                               marker_trans +

                               transforms.Affine2D().translate(x, y),

                               rgbFace)



    def draw_path_collection(self, gc, master_transform, paths, all_transforms,

                             offsets, offset_trans, facecolors, edgecolors,

                             linewidths, linestyles, antialiaseds, urls,

                             offset_position, *, hatchcolors=None):

        

        path_ids = self._iter_collection_raw_paths(master_transform,

                                                   paths, all_transforms)



        if hatchcolors is None:

            hatchcolors = []



        for xo, yo, path_id, gc0, rgbFace in self._iter_collection(

                gc, list(path_ids), offsets, offset_trans,

                facecolors, edgecolors, linewidths, linestyles,

                antialiaseds, urls, offset_position, hatchcolors=hatchcolors):

            path, transform = path_id

                                                                          

                                          

            if xo != 0 or yo != 0:

                                                                         

                                                                       

                                                                              

                transform = transform.frozen()

                transform.translate(xo, yo)

            self.draw_path(gc0, path, transform, rgbFace)



    def draw_quad_mesh(self, gc, master_transform, meshWidth, meshHeight,

                       coordinates, offsets, offsetTrans, facecolors,

                       antialiased, edgecolors):

        



        from matplotlib.collections import QuadMesh

        paths = QuadMesh._convert_mesh_to_paths(coordinates)



        if edgecolors is None:

            edgecolors = facecolors

        linewidths = np.array([gc.get_linewidth()], float)



        return self.draw_path_collection(

            gc, master_transform, paths, [], offsets, offsetTrans, facecolors,

            edgecolors, linewidths, [], [antialiased], [None], 'screen')



    def draw_gouraud_triangles(self, gc, triangles_array, colors_array,

                               transform):

        

        raise NotImplementedError



    def _iter_collection_raw_paths(self, master_transform, paths,

                                   all_transforms):

        

        Npaths = len(paths)

        Ntransforms = len(all_transforms)

        N = max(Npaths, Ntransforms)



        if Npaths == 0:

            return



        transform = transforms.IdentityTransform()

        for i in range(N):

            path = paths[i % Npaths]

            if Ntransforms:

                transform = Affine2D(all_transforms[i % Ntransforms])

            yield path, transform + master_transform



    def _iter_collection_uses_per_path(self, paths, all_transforms,

                                       offsets, facecolors, edgecolors):

        

        Npaths = len(paths)

        if Npaths == 0 or len(facecolors) == len(edgecolors) == 0:

            return 0

        Npath_ids = max(Npaths, len(all_transforms))

        N = max(Npath_ids, len(offsets))

        return (N + Npath_ids - 1) // Npath_ids



    def _iter_collection(self, gc, path_ids, offsets, offset_trans, facecolors,

                         edgecolors, linewidths, linestyles,

                         antialiaseds, urls, offset_position, *, hatchcolors):

        

        Npaths = len(path_ids)

        Noffsets = len(offsets)

        N = max(Npaths, Noffsets)

        Nfacecolors = len(facecolors)

        Nedgecolors = len(edgecolors)

        Nhatchcolors = len(hatchcolors)

        Nlinewidths = len(linewidths)

        Nlinestyles = len(linestyles)

        Nurls = len(urls)



        if (Nfacecolors == 0 and Nedgecolors == 0 and Nhatchcolors == 0) or Npaths == 0:

            return



        gc0 = self.new_gc()

        gc0.copy_properties(gc)



        def cycle_or_default(seq, default=None):

                                                                               

            return (itertools.cycle(seq) if len(seq)

                    else itertools.repeat(default))



        pathids = cycle_or_default(path_ids)

        toffsets = cycle_or_default(offset_trans.transform(offsets), (0, 0))

        fcs = cycle_or_default(facecolors)

        ecs = cycle_or_default(edgecolors)

        hcs = cycle_or_default(hatchcolors)

        lws = cycle_or_default(linewidths)

        lss = cycle_or_default(linestyles)

        aas = cycle_or_default(antialiaseds)

        urls = cycle_or_default(urls)



        if Nedgecolors == 0:

            gc0.set_linewidth(0.0)



        for pathid, (xo, yo), fc, ec, hc, lw, ls, aa, url in itertools.islice(

                zip(pathids, toffsets, fcs, ecs, hcs, lws, lss, aas, urls), N):

            if not (np.isfinite(xo) and np.isfinite(yo)):

                continue

            if Nedgecolors:

                if Nlinewidths:

                    gc0.set_linewidth(lw)

                if Nlinestyles:

                    gc0.set_dashes(*ls)

                if len(ec) == 4 and ec[3] == 0.0:

                    gc0.set_linewidth(0)

                else:

                    gc0.set_foreground(ec)

            if Nhatchcolors:

                gc0.set_hatch_color(hc)

            if fc is not None and len(fc) == 4 and fc[3] == 0:

                fc = None

            gc0.set_antialiased(aa)

            if Nurls:

                gc0.set_url(url)

            yield xo, yo, pathid, gc0, fc

        gc0.restore()



    def get_image_magnification(self):

        

        return 1.0



    def draw_image(self, gc, x, y, im, transform=None):

        

        raise NotImplementedError



    def option_image_nocomposite(self):

        

        return False



    def option_scale_image(self):

        

        return False



    def draw_tex(self, gc, x, y, s, prop, angle, *, mtext=None):

        

        self._draw_text_as_path(gc, x, y, s, prop, angle, ismath="TeX")



    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):

        

        self._draw_text_as_path(gc, x, y, s, prop, angle, ismath)



    def _draw_text_as_path(self, gc, x, y, s, prop, angle, ismath):

        

        text2path = self._text2path

        fontsize = self.points_to_pixels(prop.get_size_in_points())

        verts, codes = text2path.get_text_path(prop, s, ismath=ismath)

        path = Path(verts, codes)

        if self.flipy():

            width, height = self.get_canvas_width_height()

            transform = (Affine2D()

                         .scale(fontsize / text2path.FONT_SCALE)

                         .rotate_deg(angle)

                         .translate(x, height - y))

        else:

            transform = (Affine2D()

                         .scale(fontsize / text2path.FONT_SCALE)

                         .rotate_deg(angle)

                         .translate(x, y))

        color = gc.get_rgb()

        gc.set_linewidth(0.0)

        self.draw_path(gc, path, transform, rgbFace=color)



    def get_text_width_height_descent(self, s, prop, ismath):

        

        fontsize = prop.get_size_in_points()



        if ismath == 'TeX':

                                     

            return self.get_texmanager().get_text_width_height_descent(

                s, fontsize, renderer=self)



        dpi = self.points_to_pixels(72)

        if ismath:

            dims = self._text2path.mathtext_parser.parse(s, dpi, prop)

            return dims[0:3]                                 



        flags = self._text2path._get_hinting_flag()

        font = self._text2path._get_font(prop)

        font.set_size(fontsize, dpi)

                                                  

        font.set_text(s, 0.0, flags=flags)

        w, h = font.get_width_height()

        d = font.get_descent()

        w /= 64.0                          

        h /= 64.0

        d /= 64.0

        return w, h, d



    def flipy(self):

        

        return True



    def get_canvas_width_height(self):

        

        return 1, 1



    def get_texmanager(self):

        

        if self._texmanager is None:

            self._texmanager = TexManager()

        return self._texmanager



    def new_gc(self):

        

        return GraphicsContextBase()



    def points_to_pixels(self, points):

        

        return points



    def start_rasterizing(self):

        



    def stop_rasterizing(self):

        



    def start_filter(self):

        



    def stop_filter(self, filter_func):

        



    def _draw_disabled(self):

        

        no_ops = {

            meth_name: functools.update_wrapper(lambda *args, **kwargs: None,

                                                getattr(RendererBase, meth_name))

            for meth_name in dir(RendererBase)

            if (meth_name.startswith("draw_")

                or meth_name in ["open_group", "close_group"])

        }



        return _setattr_cm(self, **no_ops)





class GraphicsContextBase:

    



    def __init__(self):

        self._alpha = 1.0

        self._forced_alpha = False                                         

        self._antialiased = 1                                               

        self._capstyle = CapStyle('butt')

        self._cliprect = None

        self._clippath = None

        self._dashes = 0, None

        self._joinstyle = JoinStyle('round')

        self._linestyle = 'solid'

        self._linewidth = 1

        self._rgb = (0.0, 0.0, 0.0, 1.0)

        self._hatch = None

        self._hatch_color = None

        self._hatch_linewidth = rcParams['hatch.linewidth']

        self._url = None

        self._gid = None

        self._snap = None

        self._sketch = None



    def copy_properties(self, gc):

        

        self._alpha = gc._alpha

        self._forced_alpha = gc._forced_alpha

        self._antialiased = gc._antialiased

        self._capstyle = gc._capstyle

        self._cliprect = gc._cliprect

        self._clippath = gc._clippath

        self._dashes = gc._dashes

        self._joinstyle = gc._joinstyle

        self._linestyle = gc._linestyle

        self._linewidth = gc._linewidth

        self._rgb = gc._rgb

        self._hatch = gc._hatch

        self._hatch_color = gc._hatch_color

        self._hatch_linewidth = gc._hatch_linewidth

        self._url = gc._url

        self._gid = gc._gid

        self._snap = gc._snap

        self._sketch = gc._sketch



    def restore(self):

        



    def get_alpha(self):

        

        return self._alpha



    def get_antialiased(self):

        

        return self._antialiased



    def get_capstyle(self):

        

        return self._capstyle.name



    def get_clip_rectangle(self):

        

        return self._cliprect



    def get_clip_path(self):

        

        if self._clippath is not None:

            tpath, tr = self._clippath.get_transformed_path_and_affine()

            if np.all(np.isfinite(tpath.vertices)):

                return tpath, tr

            else:

                _log.warning("Ill-defined clip_path detected. Returning None.")

                return None, None

        return None, None



    def get_dashes(self):

        

        return self._dashes



    def get_forced_alpha(self):

        

        return self._forced_alpha



    def get_joinstyle(self):

        

        return self._joinstyle.name



    def get_linewidth(self):

        

        return self._linewidth



    def get_rgb(self):

        

        return self._rgb



    def get_url(self):

        

        return self._url



    def get_gid(self):

        

        return self._gid



    def get_snap(self):

        

        return self._snap



    def set_alpha(self, alpha):

        

        if alpha is not None:

            self._alpha = alpha

            self._forced_alpha = True

        else:

            self._alpha = 1.0

            self._forced_alpha = False

        self.set_foreground(self._rgb, isRGBA=True)



    def set_antialiased(self, b):

        

                                                                               

        self._antialiased = int(bool(b))



    @_docstring.interpd

    def set_capstyle(self, cs):

        

        self._capstyle = CapStyle(cs)



    def set_clip_rectangle(self, rectangle):

        

        self._cliprect = rectangle



    def set_clip_path(self, path):

        

        _api.check_isinstance((transforms.TransformedPath, None), path=path)

        self._clippath = path



    def set_dashes(self, dash_offset, dash_list):

        

        if dash_list is not None:

            dl = np.asarray(dash_list)

            if np.any(dl < 0.0):

                raise ValueError(

                    "All values in the dash list must be non-negative")

            if dl.size and not np.any(dl > 0.0):

                raise ValueError(

                    'At least one value in the dash list must be positive')

        self._dashes = dash_offset, dash_list



    def set_foreground(self, fg, isRGBA=False):

        

        if self._forced_alpha and isRGBA:

            self._rgb = fg[:3] + (self._alpha,)

        elif self._forced_alpha:

            self._rgb = colors.to_rgba(fg, self._alpha)

        elif isRGBA:

            self._rgb = fg

        else:

            self._rgb = colors.to_rgba(fg)



    @_docstring.interpd

    def set_joinstyle(self, js):

        

        self._joinstyle = JoinStyle(js)



    def set_linewidth(self, w):

        

        self._linewidth = float(w)



    def set_url(self, url):

        

        self._url = url



    def set_gid(self, id):

        

        self._gid = id



    def set_snap(self, snap):

        

        self._snap = snap



    def set_hatch(self, hatch):

        

        self._hatch = hatch



    def get_hatch(self):

        

        return self._hatch



    def get_hatch_path(self, density=6.0):

        

        hatch = self.get_hatch()

        if hatch is None:

            return None

        return Path.hatch(hatch, density)



    def get_hatch_color(self):

        

        return self._hatch_color



    def set_hatch_color(self, hatch_color):

        

        self._hatch_color = hatch_color



    def get_hatch_linewidth(self):

        

        return self._hatch_linewidth



    def set_hatch_linewidth(self, hatch_linewidth):

        

        self._hatch_linewidth = hatch_linewidth



    def get_sketch_params(self):

        

        return self._sketch



    def set_sketch_params(self, scale=None, length=None, randomness=None):

        

        self._sketch = (

            None if scale is None

            else (scale, length or 128., randomness or 16.))





class TimerBase:

    



    def __init__(self, interval=None, callbacks=None):

        

        self.callbacks = [] if callbacks is None else callbacks.copy()

                                                                             

        self.interval = 1000 if interval is None else interval

        self.single_shot = False



    def __del__(self):

        

        self._timer_stop()



    def start(self):

        

        self._timer_start()



    def stop(self):

        

        self._timer_stop()



    def _timer_start(self):

        pass



    def _timer_stop(self):

        pass



    @property

    def interval(self):

        

        return self._interval



    @interval.setter

    def interval(self, interval):

                                                                             

                                                        

                                                                         

        interval = max(int(interval), 1)

        self._interval = interval

        self._timer_set_interval()



    @property

    def single_shot(self):

        

        return self._single



    @single_shot.setter

    def single_shot(self, ss):

        self._single = ss

        self._timer_set_single_shot()



    def add_callback(self, func, *args, **kwargs):

        

        self.callbacks.append((func, args, kwargs))

        return func



    def remove_callback(self, func, *args, **kwargs):

        

        if args or kwargs:

            _api.warn_deprecated(

                "3.1", message="In a future version, Timer.remove_callback "

                "will not take *args, **kwargs anymore, but remove all "

                "callbacks where the callable matches; to keep a specific "

                "callback removable by itself, pass it to add_callback as a "

                "functools.partial object.")

            self.callbacks.remove((func, args, kwargs))

        else:

            funcs = [c[0] for c in self.callbacks]

            if func in funcs:

                self.callbacks.pop(funcs.index(func))



    def _timer_set_interval(self):

        



    def _timer_set_single_shot(self):

        



    def _on_timer(self):

        

        for func, args, kwargs in self.callbacks:

            ret = func(*args, **kwargs)

                                                                     

                                      

                                                                 

                                            

                                                                            

            if ret == 0:

                self.callbacks.remove((func, args, kwargs))



        if len(self.callbacks) == 0:

            self.stop()





class Event:

    



    def __init__(self, name, canvas, guiEvent=None):

        self.name = name

        self.canvas = canvas

        self.guiEvent = guiEvent



    def _process(self):

        

        self.canvas.callbacks.process(self.name, self)

        self.guiEvent = None





class DrawEvent(Event):

    

    def __init__(self, name, canvas, renderer):

        super().__init__(name, canvas)

        self.renderer = renderer





class ResizeEvent(Event):

    



    def __init__(self, name, canvas):

        super().__init__(name, canvas)

        self.width, self.height = canvas.get_width_height()





class CloseEvent(Event):

    





class LocationEvent(Event):

    



    _last_axes_ref = None



    def __init__(self, name, canvas, x, y, guiEvent=None, *, modifiers=None):

        super().__init__(name, canvas, guiEvent=guiEvent)

                                                 

        self.x = int(x) if x is not None else x

                                                  

        self.y = int(y) if y is not None else y

        self.inaxes = None                                       

        self.xdata = None                                    

        self.ydata = None                                    

        self.modifiers = frozenset(modifiers if modifiers is not None else [])



        if x is None or y is None:

                                                                 

            return



        self._set_inaxes(self.canvas.inaxes((x, y))

                         if self.canvas.mouse_grabber is None else

                         self.canvas.mouse_grabber,

                         (x, y))



                                                                              

                                                                              

                                                                             

                                                                       

                                                                            



    def _set_inaxes(self, inaxes, xy=None):

        self.inaxes = inaxes

        if inaxes is not None:

            try:

                self.xdata, self.ydata = inaxes.transData.inverted().transform(

                    xy if xy is not None else (self.x, self.y))

            except ValueError:

                pass





class MouseButton(IntEnum):

    LEFT = 1

    MIDDLE = 2

    RIGHT = 3

    BACK = 8

    FORWARD = 9





class MouseEvent(LocationEvent):

    



    def __init__(self, name, canvas, x, y, button=None, key=None,

                 step=0, dblclick=False, guiEvent=None, *,

                 buttons=None, modifiers=None):

        super().__init__(

            name, canvas, x, y, guiEvent=guiEvent, modifiers=modifiers)

        if button in MouseButton.__members__.values():

            button = MouseButton(button)

        if name == "scroll_event" and button is None:

            if step > 0:

                button = "up"

            elif step < 0:

                button = "down"

        self.button = button

        if name == "motion_notify_event":

            self.buttons = frozenset(buttons if buttons is not None else [])

        else:

                                                                               

                                                                           

                                        

            if buttons:

                raise ValueError(

                    "'buttons' is only supported for 'motion_notify_event'")

            self.buttons = None

        self.key = key

        self.step = step

        self.dblclick = dblclick



    @classmethod

    def _from_ax_coords(cls, name, ax, xy, *args, **kwargs):

        

        x, y = ax.transData.transform(xy)

        event = cls(name, ax.figure.canvas, x, y, *args, **kwargs)

        event.inaxes = ax

        event.xdata, event.ydata = xy                                                

        return event



    def __str__(self):

        return (f"{self.name}: "

                f"xy=({self.x}, {self.y}) xydata=({self.xdata}, {self.ydata}) "

                f"button={self.button} dblclick={self.dblclick} "

                f"inaxes={self.inaxes}")





class PickEvent(Event):

    



    def __init__(self, name, canvas, mouseevent, artist,

                 guiEvent=None, **kwargs):

        if guiEvent is None:

            guiEvent = mouseevent.guiEvent

        super().__init__(name, canvas, guiEvent)

        self.mouseevent = mouseevent

        self.artist = artist

        self.__dict__.update(kwargs)





class KeyEvent(LocationEvent):

    



    def __init__(self, name, canvas, key, x=0, y=0, guiEvent=None):

        super().__init__(name, canvas, x, y, guiEvent=guiEvent)

        self.key = key



    @classmethod

    def _from_ax_coords(cls, name, ax, xy, key, *args, **kwargs):

        

                                                                                       

                                                                               

        x, y = ax.transData.transform(xy)

        event = cls(name, ax.figure.canvas, key, x, y, *args, **kwargs)

        event.inaxes = ax

        event.xdata, event.ydata = xy                                                

        return event





                                  

def _key_handler(event):

                            

    if event.name == "key_press_event":

        event.canvas._key = event.key

    elif event.name == "key_release_event":

        event.canvas._key = None





                                    

def _mouse_handler(event):

                                       

    if event.name == "button_press_event":

        event.canvas._button = event.button

    elif event.name == "button_release_event":

        event.canvas._button = None

    elif event.name == "motion_notify_event" and event.button is None:

        event.button = event.canvas._button

    if event.key is None:

        event.key = event.canvas._key

                                 

    if event.name == "motion_notify_event":

        last_ref = LocationEvent._last_axes_ref

        last_axes = last_ref() if last_ref else None

        if last_axes != event.inaxes:

            if last_axes is not None:

                                                                            

                                                                            

                                                                               

                                                                              

                                                                  

                try:

                    canvas = last_axes.get_figure(root=True).canvas

                    leave_event = LocationEvent(

                        "axes_leave_event", canvas,

                        event.x, event.y, event.guiEvent,

                        modifiers=event.modifiers)

                    leave_event._set_inaxes(last_axes)

                    canvas.callbacks.process("axes_leave_event", leave_event)

                except Exception:

                    pass                                                    

            if event.inaxes is not None:

                event.canvas.callbacks.process("axes_enter_event", event)

        LocationEvent._last_axes_ref = (

            weakref.ref(event.inaxes) if event.inaxes else None)





def _get_renderer(figure, print_method=None):

    

                                                                               

                                            



    class Done(Exception):

        pass



    def _draw(renderer): raise Done(renderer)



    with cbook._setattr_cm(figure, draw=_draw), ExitStack() as stack:

        if print_method is None:

            fmt = figure.canvas.get_default_filetype()

                                                                            

                                                

            print_method = stack.enter_context(

                figure.canvas._switch_canvas_and_return_print_method(fmt))

        try:

            print_method(io.BytesIO())

        except Done as exc:

            renderer, = exc.args

            return renderer

        else:

            raise RuntimeError(f"{print_method} did not call Figure.draw, so "

                               f"no renderer is available")





def _no_output_draw(figure):

                                                           

                                                      

    figure.draw_without_rendering()





def _is_non_interactive_terminal_ipython(ip):

    

    return (hasattr(ip, 'parent')

            and (ip.parent is not None)

            and getattr(ip.parent, 'interact', None) is False)





@contextmanager

def _allow_interrupt(prepare_notifier, handle_sigint):

    



    old_sigint_handler = signal.getsignal(signal.SIGINT)

    if old_sigint_handler in (None, signal.SIG_IGN, signal.SIG_DFL):

        yield

        return



    handler_args = None

    wsock, rsock = socket.socketpair()

    wsock.setblocking(False)

    rsock.setblocking(False)

    old_wakeup_fd = signal.set_wakeup_fd(wsock.fileno())

    notifier = prepare_notifier(rsock)



    def save_args_and_handle_sigint(*args):

        nonlocal handler_args, notifier

        handler_args = args

        handle_sigint(notifier)

        notifier = None



    signal.signal(signal.SIGINT, save_args_and_handle_sigint)

    try:

        yield

    finally:

        wsock.close()

        rsock.close()

        signal.set_wakeup_fd(old_wakeup_fd)

        signal.signal(signal.SIGINT, old_sigint_handler)

        if handler_args is not None:

            old_sigint_handler(*handler_args)





class FigureCanvasBase:

    



                                                                      

                                                           

    required_interactive_framework = None



                                                    

                                                                      

                                                                           

                                                            

                                   

    manager_class = _api.classproperty(lambda cls: FigureManagerBase)



    events = [

        'resize_event',

        'draw_event',

        'key_press_event',

        'key_release_event',

        'button_press_event',

        'button_release_event',

        'scroll_event',

        'motion_notify_event',

        'pick_event',

        'figure_enter_event',

        'figure_leave_event',

        'axes_enter_event',

        'axes_leave_event',

        'close_event'

    ]



    fixed_dpi = None



    filetypes = _default_filetypes



    @_api.classproperty

    def supports_blit(cls):

        

        return (hasattr(cls, "copy_from_bbox")

                and hasattr(cls, "restore_region"))



    def __init__(self, figure=None):

        from matplotlib.figure import Figure

        self._fix_ipython_backend2gui()

        self._is_idle_drawing = True

        self._is_saving = False

        if figure is None:

            figure = Figure()

        figure.set_canvas(self)

        self.figure = figure

        self.manager = None

        self.widgetlock = widgets.LockDraw()

        self._button = None                      

        self._key = None                   

        self.mouse_grabber = None                                     

        self.toolbar = None                                  

        self._is_idle_drawing = False

                                                                  

        figure._original_dpi = figure.dpi

        self._device_pixel_ratio = 1

        super().__init__()                                           



    callbacks = property(lambda self: self.figure._canvas_callbacks)

    button_pick_id = property(lambda self: self.figure._button_pick_id)

    scroll_pick_id = property(lambda self: self.figure._scroll_pick_id)



    @classmethod

    @functools.cache

    def _fix_ipython_backend2gui(cls):

                                                                       

                                                                       

                                                                              

                                                     



                                                                               

                                                                        

                                                                        

        mod_ipython = sys.modules.get("IPython")

        if mod_ipython is None or mod_ipython.version_info[:2] >= (8, 24):

                                                                         

                                                         

            return



        import IPython

        ip = IPython.get_ipython()

        if not ip:

            return

        from IPython.core import pylabtools as pt

        if (not hasattr(pt, "backend2gui")

                or not hasattr(ip, "enable_matplotlib")):

                                                                              

                                      

            return

        backend2gui_rif = {

            "qt": "qt",

            "gtk3": "gtk3",

            "gtk4": "gtk4",

            "wx": "wx",

            "macosx": "osx",

        }.get(cls.required_interactive_framework)

        if backend2gui_rif:

            if _is_non_interactive_terminal_ipython(ip):

                ip.enable_gui(backend2gui_rif)



    @classmethod

    def new_manager(cls, figure, num):

        

        return cls.manager_class.create_with_canvas(cls, figure, num)



    @contextmanager

    def _idle_draw_cntx(self):

        self._is_idle_drawing = True

        try:

            yield

        finally:

            self._is_idle_drawing = False



    def is_saving(self):

        

        return self._is_saving



    def blit(self, bbox=None):

        



    def inaxes(self, xy):

        

        axes_list = [a for a in self.figure.get_axes()

                     if a.patch.contains_point(xy) and a.get_visible()]

        if axes_list:

            axes = cbook._topmost_artist(axes_list)

        else:

            axes = None



        return axes



    def grab_mouse(self, ax):

        

        if self.mouse_grabber not in (None, ax):

            raise RuntimeError("Another Axes already grabs mouse input")

        self.mouse_grabber = ax



    def release_mouse(self, ax):

        

        if self.mouse_grabber is ax:

            self.mouse_grabber = None



    def set_cursor(self, cursor):

        



    def draw(self, *args, **kwargs):

        



    def draw_idle(self, *args, **kwargs):

        

        if not self._is_idle_drawing:

            with self._idle_draw_cntx():

                self.draw(*args, **kwargs)



    @property

    def device_pixel_ratio(self):

        

        return self._device_pixel_ratio



    def _set_device_pixel_ratio(self, ratio):

        

        if self._device_pixel_ratio == ratio:

            return False

                                                                               

                                                                         

                                                                          

                                                                              

        dpi = ratio * self.figure._original_dpi

        self.figure._set_dpi(dpi, forward=False)

        self._device_pixel_ratio = ratio

        return True



    def get_width_height(self, *, physical=False):

        

        return tuple(int(size / (1 if physical else self.device_pixel_ratio))

                     for size in self.figure.bbox.max)



    @classmethod

    def get_supported_filetypes(cls):

        

        return cls.filetypes



    @classmethod

    def get_supported_filetypes_grouped(cls):

        

        groupings = {}

        for ext, name in cls.filetypes.items():

            groupings.setdefault(name, []).append(ext)

            groupings[name].sort()

        return groupings



    @contextmanager

    def _switch_canvas_and_return_print_method(self, fmt, backend=None):

        

        canvas = None

        if backend is not None:

                                                           

            from .backends.registry import backend_registry

            canvas_class = backend_registry.load_backend_module(backend).FigureCanvas

            if not hasattr(canvas_class, f"print_{fmt}"):

                raise ValueError(

                    f"The {backend!r} backend does not support {fmt} output")

            canvas = canvas_class(self.figure)

        elif hasattr(self, f"print_{fmt}"):

                                                                            

            canvas = self

        else:

                                                                             

            canvas_class = get_registered_canvas_class(fmt)

            if canvas_class is None:

                raise ValueError(

                    "Format {!r} is not supported (supported formats: {})".format(

                        fmt, ", ".join(sorted(self.get_supported_filetypes()))))

            canvas = canvas_class(self.figure)

        canvas._is_saving = self._is_saving

        meth = getattr(canvas, f"print_{fmt}")

        mod = (meth.func.__module__

               if hasattr(meth, "func")                                   

               else meth.__module__)

        if mod.startswith(("matplotlib.", "mpl_toolkits.")):

            optional_kws = {                                               

                "dpi", "facecolor", "edgecolor", "orientation",

                "bbox_inches_restore"}

            skip = optional_kws - {*inspect.signature(meth).parameters}

            print_method = functools.wraps(meth)(lambda *args, **kwargs: meth(

                *args, **{k: v for k, v in kwargs.items() if k not in skip}))

        else:                                         

            print_method = meth

        try:

            yield print_method

        finally:

            self.figure.canvas = self



    def print_figure(

            self, filename, dpi=None, facecolor=None, edgecolor=None,

            orientation='portrait', format=None, *,

            bbox_inches=None, pad_inches=None, bbox_extra_artists=None,

            backend=None, **kwargs):

        

        if format is None:

                                                                          

            if isinstance(filename, os.PathLike):

                filename = os.fspath(filename)

            if isinstance(filename, str):

                format = os.path.splitext(filename)[1][1:]

            if format is None or format == '':

                format = self.get_default_filetype()

                if isinstance(filename, str):

                    filename = filename.rstrip('.') + '.' + format

        format = format.lower()



        dpi = mpl._val_or_rc(dpi, 'savefig.dpi')

        if dpi == 'figure':

            dpi = getattr(self.figure, '_original_dpi', self.figure.dpi)



                                                                              

        with (cbook._setattr_cm(self, manager=None),

              self._switch_canvas_and_return_print_method(format, backend)

                 as print_method,

              cbook._setattr_cm(self.figure, dpi=dpi),

              cbook._setattr_cm(self.figure.canvas, _device_pixel_ratio=1),

              cbook._setattr_cm(self.figure.canvas, _is_saving=True),

              ExitStack() as stack):



            for prop, color in [("facecolor", facecolor), ("edgecolor", edgecolor)]:

                color = mpl._val_or_rc(color, f"savefig.{prop}")

                if not cbook._str_equal(color, "auto"):

                    stack.enter_context(self.figure._cm_set(**{prop: color}))



            bbox_inches = mpl._val_or_rc(bbox_inches, 'savefig.bbox')



            layout_engine = self.figure.get_layout_engine()

            if layout_engine is not None or bbox_inches == "tight":

                                                                        

                                                                       

                            

                renderer = _get_renderer(

                    self.figure,

                    functools.partial(

                        print_method, orientation=orientation)

                )

                                                                            

                                                       

                with getattr(renderer, "_draw_disabled", nullcontext)():

                    self.figure.draw(renderer)

            else:

                renderer = None



            if bbox_inches:

                if bbox_inches == "tight":

                    bbox_inches = self.figure.get_tightbbox(

                        renderer, bbox_extra_artists=bbox_extra_artists)

                    if (isinstance(layout_engine, ConstrainedLayoutEngine) and

                            pad_inches == "layout"):

                        h_pad = layout_engine.get()["h_pad"]

                        w_pad = layout_engine.get()["w_pad"]

                    else:

                        if pad_inches in [None, "layout"]:

                            pad_inches = rcParams['savefig.pad_inches']

                        h_pad = w_pad = pad_inches

                    bbox_inches = bbox_inches.padded(w_pad, h_pad)



                                                              

                restore_bbox = _tight_bbox.adjust_bbox(

                    self.figure, bbox_inches, renderer, self.figure.canvas.fixed_dpi)



                _bbox_inches_restore = (bbox_inches, restore_bbox)

            else:

                _bbox_inches_restore = None



                                                                

            stack.enter_context(self.figure._cm_set(layout_engine='none'))

            try:

                                                                            

                                                                               

                with cbook._setattr_cm(self.figure, dpi=dpi):

                    result = print_method(

                        filename,

                        facecolor=facecolor,

                        edgecolor=edgecolor,

                        orientation=orientation,

                        bbox_inches_restore=_bbox_inches_restore,

                        **kwargs)

            finally:

                if bbox_inches and restore_bbox:

                    restore_bbox()



            return result



    @classmethod

    def get_default_filetype(cls):

        

        return rcParams['savefig.format']



    def get_default_filename(self):

        

        default_basename = (

            self.manager.get_window_title()

            if self.manager is not None

            else ''

        )

        default_basename = default_basename or 'image'

                                                

                                                                                                            

                  

        removed_chars = '<>:"/\\|?*\0 '

        default_basename = default_basename.translate(

            {ord(c): "_" for c in removed_chars})

        default_filetype = self.get_default_filetype()

        return f'{default_basename}.{default_filetype}'



    def mpl_connect(self, s, func):

        



        return self.callbacks.connect(s, func)



    def mpl_disconnect(self, cid):

        

        self.callbacks.disconnect(cid)



                                                                              

                                                          

    _timer_cls = TimerBase



    def new_timer(self, interval=None, callbacks=None):

        

        return self._timer_cls(interval=interval, callbacks=callbacks)



    def flush_events(self):

        



    def start_event_loop(self, timeout=0):

        

        if timeout <= 0:

            timeout = np.inf

        timestep = 0.01

        counter = 0

        self._looping = True

        while self._looping and counter * timestep < timeout:

            self.flush_events()

            time.sleep(timestep)

            counter += 1



    def stop_event_loop(self):

        

        self._looping = False





def key_press_handler(event, canvas=None, toolbar=None):

    

    if event.key is None:

        return

    if canvas is None:

        canvas = event.canvas

    if toolbar is None:

        toolbar = canvas.toolbar



                                                          

    if event.key in rcParams['keymap.fullscreen']:

        try:

            canvas.manager.full_screen_toggle()

        except AttributeError:

            pass



                                            

    if event.key in rcParams['keymap.quit']:

        Gcf.destroy_fig(canvas.figure)

    if event.key in rcParams['keymap.quit_all']:

        Gcf.destroy_all()



    if toolbar is not None:

                                                                   

        if event.key in rcParams['keymap.home']:

            toolbar.home()

                                                                        

                                                                 

        elif event.key in rcParams['keymap.back']:

            toolbar.back()

                                                    

        elif event.key in rcParams['keymap.forward']:

            toolbar.forward()

                                        

        elif event.key in rcParams['keymap.pan']:

            toolbar.pan()

            toolbar._update_cursor(event)

                                         

        elif event.key in rcParams['keymap.zoom']:

            toolbar.zoom()

            toolbar._update_cursor(event)

                                                 

        elif event.key in rcParams['keymap.save']:

            toolbar.save_figure()



    if event.inaxes is None:

        return



                                                                    

    def _get_uniform_gridstate(ticks):

                                                                             

                                    

        return (True if all(tick.gridline.get_visible() for tick in ticks) else

                False if not any(tick.gridline.get_visible() for tick in ticks) else

                None)



    ax = event.inaxes

                                                          

                                                                          

                                                                        

                    

    if (event.key in rcParams['keymap.grid']

                                                         

            and None not in [_get_uniform_gridstate(ax.xaxis.minorTicks),

                             _get_uniform_gridstate(ax.yaxis.minorTicks)]):

        x_state = _get_uniform_gridstate(ax.xaxis.majorTicks)

        y_state = _get_uniform_gridstate(ax.yaxis.majorTicks)

        cycle = [(False, False), (True, False), (True, True), (False, True)]

        try:

            x_state, y_state = (

                cycle[(cycle.index((x_state, y_state)) + 1) % len(cycle)])

        except ValueError:

                                                         

            pass

        else:

                                                                    

            ax.grid(x_state, which="major" if x_state else "both", axis="x")

            ax.grid(y_state, which="major" if y_state else "both", axis="y")

            canvas.draw_idle()

                                                                    

    if (event.key in rcParams['keymap.grid_minor']

                                                         

            and None not in [_get_uniform_gridstate(ax.xaxis.majorTicks),

                             _get_uniform_gridstate(ax.yaxis.majorTicks)]):

        x_state = _get_uniform_gridstate(ax.xaxis.minorTicks)

        y_state = _get_uniform_gridstate(ax.yaxis.minorTicks)

        cycle = [(False, False), (True, False), (True, True), (False, True)]

        try:

            x_state, y_state = (

                cycle[(cycle.index((x_state, y_state)) + 1) % len(cycle)])

        except ValueError:

                                                         

            pass

        else:

            ax.grid(x_state, which="both", axis="x")

            ax.grid(y_state, which="both", axis="y")

            canvas.draw_idle()

                                                                          

    elif event.key in rcParams['keymap.yscale']:

        scale = ax.get_yscale()

        if scale == 'log':

            ax.set_yscale('linear')

            ax.get_figure(root=True).canvas.draw_idle()

        elif scale == 'linear':

            try:

                ax.set_yscale('log')

            except ValueError as exc:

                _log.warning(str(exc))

                ax.set_yscale('linear')

            ax.get_figure(root=True).canvas.draw_idle()

                                                                          

    elif event.key in rcParams['keymap.xscale']:

        scalex = ax.get_xscale()

        if scalex == 'log':

            ax.set_xscale('linear')

            ax.get_figure(root=True).canvas.draw_idle()

        elif scalex == 'linear':

            try:

                ax.set_xscale('log')

            except ValueError as exc:

                _log.warning(str(exc))

                ax.set_xscale('linear')

            ax.get_figure(root=True).canvas.draw_idle()





def button_press_handler(event, canvas=None, toolbar=None):

    

    if canvas is None:

        canvas = event.canvas

    if toolbar is None:

        toolbar = canvas.toolbar

    if toolbar is not None:

        button_name = str(MouseButton(event.button))

        if button_name in rcParams['keymap.back']:

            toolbar.back()

        elif button_name in rcParams['keymap.forward']:

            toolbar.forward()





class NonGuiException(Exception):

    

    pass





class FigureManagerBase:

    



    _toolbar2_class = None

    _toolmanager_toolbar_class = None



    def __init__(self, canvas, num):

        self.canvas = canvas

        canvas.manager = self                             

        self.num = num

        self.set_window_title(f"Figure {num:d}")



        self.key_press_handler_id = None

        self.button_press_handler_id = None

        if rcParams['toolbar'] != 'toolmanager':

            self.key_press_handler_id = self.canvas.mpl_connect(

                'key_press_event', key_press_handler)

            self.button_press_handler_id = self.canvas.mpl_connect(

                'button_press_event', button_press_handler)



        self.toolmanager = (ToolManager(canvas.figure)

                            if mpl.rcParams['toolbar'] == 'toolmanager'

                            else None)

        if (mpl.rcParams["toolbar"] == "toolbar2"

                and self._toolbar2_class):

            self.toolbar = self._toolbar2_class(self.canvas)

        elif (mpl.rcParams["toolbar"] == "toolmanager"

                and self._toolmanager_toolbar_class):

            self.toolbar = self._toolmanager_toolbar_class(self.toolmanager)

        else:

            self.toolbar = None



        if self.toolmanager:

            tools.add_tools_to_manager(self.toolmanager)

            if self.toolbar:

                tools.add_tools_to_container(self.toolbar)



        @self.canvas.figure.add_axobserver

        def notify_axes_change(fig):

                                                          

            if self.toolmanager is None and self.toolbar is not None:

                self.toolbar.update()



    @classmethod

    def create_with_canvas(cls, canvas_class, figure, num):

        

        return cls(canvas_class(figure), num)



    @classmethod

    def start_main_loop(cls):

        



    @classmethod

    def pyplot_show(cls, *, block=None):

        

        managers = Gcf.get_all_fig_managers()

        if not managers:

            return

        for manager in managers:

            try:

                manager.show()                                                

            except NonGuiException as exc:

                _api.warn_external(str(exc))

        if block is None:

                                                                            

                                                                            

                            

            pyplot_show = getattr(sys.modules.get("matplotlib.pyplot"), "show", None)

            ipython_pylab = hasattr(pyplot_show, "_needmain")

            block = not ipython_pylab and not is_interactive()

        if block:

            cls.start_main_loop()



    def show(self):

        

                                                    

        if sys.platform == "linux" and not os.environ.get("DISPLAY"):

                                                                     

                                                                          

                                                                               

                                      

            return

        raise NonGuiException(

            f"{type(self.canvas).__name__} is non-interactive, and thus cannot be "

            f"shown")



    def destroy(self):

        pass



    def full_screen_toggle(self):

        pass



    def resize(self, w, h):

        



    def get_window_title(self):

        

        return self._window_title



    def set_window_title(self, title):

        

                                                                            

                                                                         

                                                                             

                                                                            

                                            

        self._window_title = title





cursors = tools.cursors





class _Mode(str, Enum):

    NONE = ""

    PAN = "pan/zoom"

    ZOOM = "zoom rect"



    def __str__(self):

        return self.value





class NavigationToolbar2:

    



                                                         

       

                                                                   

                                                                   

                                                                              

                                                                          

       

    toolitems = (

        ('Home', 'Reset original view', 'home', 'home'),

        ('Back', 'Back to previous view', 'back', 'back'),

        ('Forward', 'Forward to next view', 'forward', 'forward'),

        (None, None, None, None),

        ('Pan',

         'Left button pans, Right button zooms\n'

         'x/y fixes axis, CTRL fixes aspect',

         'move', 'pan'),

        ('Zoom', 'Zoom to rectangle\nx/y fixes axis', 'zoom_to_rect', 'zoom'),

        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),

        (None, None, None, None),

        ('Save', 'Save the figure', 'filesave', 'save_figure'),

      )



    UNKNOWN_SAVED_STATUS = object()



    def __init__(self, canvas):

        self.canvas = canvas

        canvas.toolbar = self

        self._nav_stack = cbook._Stack()

                                                         

        self._last_cursor = tools.Cursors.POINTER



        self._id_press = self.canvas.mpl_connect(

            'button_press_event', self._zoom_pan_handler)

        self._id_release = self.canvas.mpl_connect(

            'button_release_event', self._zoom_pan_handler)

        self._id_drag = self.canvas.mpl_connect(

            'motion_notify_event', self.mouse_move)

        self._pan_info = None

        self._zoom_info = None



        self.mode = _Mode.NONE                                    

        self.set_history_buttons()



    def set_message(self, s):

        



    def draw_rubberband(self, event, x0, y0, x1, y1):

        



    def remove_rubberband(self):

        



    def home(self, *args):

        

        self._nav_stack.home()

        self.set_history_buttons()

        self._update_view()



    def back(self, *args):

        

        self._nav_stack.back()

        self.set_history_buttons()

        self._update_view()



    def forward(self, *args):

        

        self._nav_stack.forward()

        self.set_history_buttons()

        self._update_view()



    def _update_cursor(self, event):

        

        if self.mode and event.inaxes and event.inaxes.get_navigate():

            if (self.mode == _Mode.ZOOM

                    and self._last_cursor != tools.Cursors.SELECT_REGION):

                self.canvas.set_cursor(tools.Cursors.SELECT_REGION)

                self._last_cursor = tools.Cursors.SELECT_REGION

            elif (self.mode == _Mode.PAN

                  and self._last_cursor != tools.Cursors.MOVE):

                self.canvas.set_cursor(tools.Cursors.MOVE)

                self._last_cursor = tools.Cursors.MOVE

        elif self._last_cursor != tools.Cursors.POINTER:

            self.canvas.set_cursor(tools.Cursors.POINTER)

            self._last_cursor = tools.Cursors.POINTER



    @contextmanager

    def _wait_cursor_for_draw_cm(self):

        

        self._draw_time, last_draw_time = (

            time.time(), getattr(self, "_draw_time", -np.inf))

        if self._draw_time - last_draw_time > 1:

            try:

                self.canvas.set_cursor(tools.Cursors.WAIT)

                yield

            finally:

                self.canvas.set_cursor(self._last_cursor)

        else:

            yield



    @staticmethod

    def _mouse_event_to_message(event):

        if event.inaxes and event.inaxes.get_navigate():

            try:

                s = event.inaxes.format_coord(event.xdata, event.ydata)

            except (ValueError, OverflowError):

                pass

            else:

                s = s.rstrip()

                artists = [a for a in event.inaxes._mouseover_set

                           if a.contains(event)[0] and a.get_visible()]

                if artists:

                    a = cbook._topmost_artist(artists)

                    if a is not event.inaxes.patch:

                        data = a.get_cursor_data(event)

                        if data is not None:

                            data_str = a.format_cursor_data(data).rstrip()

                            if data_str:

                                s = s + '\n' + data_str

                return s

        return ""



    def mouse_move(self, event):

        self._update_cursor(event)

        self.set_message(self._mouse_event_to_message(event))



    def _zoom_pan_handler(self, event):

        if self.mode == _Mode.PAN:

            if event.name == "button_press_event":

                self.press_pan(event)

            elif event.name == "button_release_event":

                self.release_pan(event)

        if self.mode == _Mode.ZOOM:

            if event.name == "button_press_event":

                self.press_zoom(event)

            elif event.name == "button_release_event":

                self.release_zoom(event)



    def _start_event_axes_interaction(self, event, *, method):



        def _ax_filter(ax):

            return (ax.in_axes(event) and

                    ax.get_navigate() and

                    getattr(ax, f"can_{method}")()

                    )



        def _capture_events(ax):

            f = ax.get_forward_navigation_events()

            if f == "auto":                                

                f = not ax.patch.get_visible()

            return not f



                                             

        axes = list(filter(_ax_filter, self.canvas.figure.get_axes()))



        if len(axes) == 0:

            return []



        if self._nav_stack() is None:

            self.push_current()                                      



                                                                    

        grps = dict()

        for ax in reversed(axes):

            grps.setdefault(ax.get_zorder(), []).append(ax)



        axes_to_trigger = []

                                                                     

        for zorder in sorted(grps, reverse=True):

            for ax in grps[zorder]:

                axes_to_trigger.append(ax)

                                                                                   

                axes_to_trigger.extend(ax._twinned_axes.get_siblings(ax))



                if _capture_events(ax):

                    break                                    

            else:

                                                                       

                                                                 

                                                

                continue



                                                                      

                                               

            break



                                                            

        axes_to_trigger = list(dict.fromkeys(axes_to_trigger))



        return axes_to_trigger



    def pan(self, *args):

        

        if not self.canvas.widgetlock.available(self):

            self.set_message("pan unavailable")

            return

        if self.mode == _Mode.PAN:

            self.mode = _Mode.NONE

            self.canvas.widgetlock.release(self)

        else:

            self.mode = _Mode.PAN

            self.canvas.widgetlock(self)



    _PanInfo = namedtuple("_PanInfo", "button axes cid")



    def press_pan(self, event):

        

        if (event.button not in [MouseButton.LEFT, MouseButton.RIGHT]

                or event.x is None or event.y is None):

            return



        axes = self._start_event_axes_interaction(event, method="pan")

        if not axes:

            return



                                                                  

        for ax in axes:

            ax.start_pan(event.x, event.y, event.button)



        self.canvas.mpl_disconnect(self._id_drag)

        id_drag = self.canvas.mpl_connect("motion_notify_event", self.drag_pan)



        self._pan_info = self._PanInfo(

            button=event.button, axes=axes, cid=id_drag)



    def drag_pan(self, event):

        

        if event.buttons != {self._pan_info.button}:

                                                                        

                                               

            self.release_pan(None)                                           

            return

        for ax in self._pan_info.axes:

                                                                              

                                                                        

            ax.drag_pan(self._pan_info.button, event.key, event.x, event.y)

        self.canvas.draw_idle()



    def release_pan(self, event):

        

        if self._pan_info is None:

            return

        self.canvas.mpl_disconnect(self._pan_info.cid)

        self._id_drag = self.canvas.mpl_connect(

            'motion_notify_event', self.mouse_move)

        for ax in self._pan_info.axes:

            ax.end_pan()

        self.canvas.draw_idle()

        self._pan_info = None

        self.push_current()



    def zoom(self, *args):

        if not self.canvas.widgetlock.available(self):

            self.set_message("zoom unavailable")

            return

        """Toggle zoom to rect mode."""

        if self.mode == _Mode.ZOOM:

            self.mode = _Mode.NONE

            self.canvas.widgetlock.release(self)

        else:

            self.mode = _Mode.ZOOM

            self.canvas.widgetlock(self)



    _ZoomInfo = namedtuple("_ZoomInfo", "button start_xy axes cid cbar")



    def press_zoom(self, event):

        

        if (event.button not in [MouseButton.LEFT, MouseButton.RIGHT]

                or event.x is None or event.y is None):

            return



        axes = self._start_event_axes_interaction(event, method="zoom")

        if not axes:

            return



        id_zoom = self.canvas.mpl_connect(

            "motion_notify_event", self.drag_zoom)



                                                                            

                                                                            

                                                          

        parent_ax = axes[0]

        if hasattr(parent_ax, "_colorbar"):

            cbar = parent_ax._colorbar.orientation

        else:

            cbar = None



        self._zoom_info = self._ZoomInfo(

            button=event.button, start_xy=(event.x, event.y), axes=axes,

            cid=id_zoom, cbar=cbar)



    def drag_zoom(self, event):

        

        if event.buttons != {self._zoom_info.button}:

                                                                        

                                               

            self._cleanup_post_zoom()

            return



        start_xy = self._zoom_info.start_xy

        ax = self._zoom_info.axes[0]

        (x1, y1), (x2, y2) = np.clip(

            [start_xy, [event.x, event.y]], ax.bbox.min, ax.bbox.max)

        key = event.key

                                                                  

        if self._zoom_info.cbar == "horizontal":

            key = "x"

        elif self._zoom_info.cbar == "vertical":

            key = "y"

        if key == "x":

            y1, y2 = ax.bbox.intervaly

        elif key == "y":

            x1, x2 = ax.bbox.intervalx



        self.draw_rubberband(event, x1, y1, x2, y2)



    def release_zoom(self, event):

        

        if self._zoom_info is None:

            return



                                                                              

                                                           

        self.canvas.mpl_disconnect(self._zoom_info.cid)

        self.remove_rubberband()



        start_x, start_y = self._zoom_info.start_xy

        direction = "in" if self._zoom_info.button == 1 else "out"

        key = event.key

                                                                     

                         

        if self._zoom_info.cbar == "horizontal":

            key = "x"

        elif self._zoom_info.cbar == "vertical":

            key = "y"

                                                                               

                                                                  

        if ((abs(event.x - start_x) < 5 and key != "y") or

                (abs(event.y - start_y) < 5 and key != "x")):

            self._cleanup_post_zoom()

            return



        for i, ax in enumerate(self._zoom_info.axes):

                                                                             

                                                           

            twinx = any(ax.get_shared_x_axes().joined(ax, prev)

                        for prev in self._zoom_info.axes[:i])

            twiny = any(ax.get_shared_y_axes().joined(ax, prev)

                        for prev in self._zoom_info.axes[:i])

            ax._set_view_from_bbox(

                (start_x, start_y, event.x, event.y),

                direction, key, twinx, twiny)



        self._cleanup_post_zoom()

        self.push_current()



    def _cleanup_post_zoom(self):

                                                                              

                                                           

        self.canvas.mpl_disconnect(self._zoom_info.cid)

        self.remove_rubberband()

        self.canvas.draw_idle()

        self._zoom_info = None



    def push_current(self):

        

        self._nav_stack.push(

            WeakKeyDictionary(

                {ax: (ax._get_view(),

                                                                       

                      (ax.get_position(True).frozen(),

                       ax.get_position().frozen()))

                 for ax in self.canvas.figure.axes}))

        self.set_history_buttons()



    def _update_view(self):

        

        nav_info = self._nav_stack()

        if nav_info is None:

            return

                                                                             

                                                

        items = list(nav_info.items())

        for ax, (view, (pos_orig, pos_active)) in items:

            ax._set_view(view)

                                                              

            ax._set_position(pos_orig, 'original')

            ax._set_position(pos_active, 'active')

        self.canvas.draw_idle()



    def configure_subplots(self, *args):

        if hasattr(self, "subplot_tool"):

            self.subplot_tool.figure.canvas.manager.show()

            return self.subplot_tool

                                                                   

        from matplotlib.figure import Figure

        with mpl.rc_context({"toolbar": "none"}):                              

            manager = type(self.canvas).new_manager(Figure(figsize=(6, 3)), -1)

        manager.set_window_title("Subplot configuration tool")

        tool_fig = manager.canvas.figure

        tool_fig.subplots_adjust(top=0.9)

        self.subplot_tool = widgets.SubplotTool(self.canvas.figure, tool_fig)

        cid = self.canvas.mpl_connect(

            "close_event", lambda e: manager.destroy())



        def on_tool_fig_close(e):

            self.canvas.mpl_disconnect(cid)

            del self.subplot_tool



        tool_fig.canvas.mpl_connect("close_event", on_tool_fig_close)

        manager.show()

        return self.subplot_tool



    def save_figure(self, *args):

        

        raise NotImplementedError



    def update(self):

        

        self._nav_stack.clear()

        self.set_history_buttons()



    def set_history_buttons(self):

        





class ToolContainerBase:

    



    _icon_extension = '.png'

    """
    Toolcontainer button icon image format extension

    **String**: Image extension
    """



    def __init__(self, toolmanager):

        self.toolmanager = toolmanager

        toolmanager.toolmanager_connect(

            'tool_message_event',

            lambda event: self.set_message(event.message))

        toolmanager.toolmanager_connect(

            'tool_removed_event',

            lambda event: self.remove_toolitem(event.tool.name))



    def _tool_toggled_cbk(self, event):

        

        self.toggle_toolitem(event.tool.name, event.tool.toggled)



    def add_tool(self, tool, group, position=-1):

        

        tool = self.toolmanager.get_tool(tool)

        image = self._get_image_filename(tool)

        toggle = getattr(tool, 'toggled', None) is not None

        self.add_toolitem(tool.name, group, position,

                          image, tool.description, toggle)

        if toggle:

            self.toolmanager.toolmanager_connect('tool_trigger_%s' % tool.name,

                                                 self._tool_toggled_cbk)

                                  

            if tool.toggled:

                self.toggle_toolitem(tool.name, True)



    def _get_image_filename(self, tool):

        

        if not tool.image:

            return None

        if os.path.isabs(tool.image):

            filename = tool.image

        else:

            if "image" in getattr(tool, "__dict__", {}):

                raise ValueError("If 'tool.image' is an instance variable, "

                                 "it must be an absolute path")

            for cls in type(tool).__mro__:

                if "image" in vars(cls):

                    try:

                        src = inspect.getfile(cls)

                        break

                    except (OSError, TypeError):

                        raise ValueError("Failed to locate source file "

                                         "where 'tool.image' is defined") from None

            else:

                raise ValueError("Failed to find parent class defining 'tool.image'")

            filename = str(pathlib.Path(src).parent / tool.image)

        for filename in [filename, filename + self._icon_extension]:

            if os.path.isfile(filename):

                return os.path.abspath(filename)

        for fname in [                                       

            tool.image,

            tool.image + self._icon_extension,

            cbook._get_data_path("images", tool.image),

            cbook._get_data_path("images", tool.image + self._icon_extension),

        ]:

            if os.path.isfile(fname):

                _api.warn_deprecated(

                    "3.9", message=f"Loading icon {tool.image!r} from the current "

                    "directory or from Matplotlib's image directory.  This behavior "

                    "is deprecated since %(since)s and will be removed in %(removal)s; "

                    "Tool.image should be set to a path relative to the Tool's source "

                    "file, or to an absolute path.")

                return os.path.abspath(fname)



    def trigger_tool(self, name):

        

        self.toolmanager.trigger_tool(name, sender=self)



    def add_toolitem(self, name, group, position, image, description, toggle):

        

        raise NotImplementedError



    def toggle_toolitem(self, name, toggled):

        

        raise NotImplementedError



    def remove_toolitem(self, name):

        

        raise NotImplementedError



    def set_message(self, s):

        

        raise NotImplementedError





class _Backend:

                                                              

     

                      

                                 

                                                                 



                                                          

    backend_version = "unknown"



                                               

    FigureCanvas = None



                                                                             

    FigureManager = FigureManagerBase



                                                                         

                                                                             

                                   

    mainloop = None



                                                                           

                        



    @classmethod

    def new_figure_manager(cls, num, *args, **kwargs):

        

                                                                   

        from matplotlib.figure import Figure

        fig_cls = kwargs.pop('FigureClass', Figure)

        fig = fig_cls(*args, **kwargs)

        return cls.new_figure_manager_given_figure(num, fig)



    @classmethod

    def new_figure_manager_given_figure(cls, num, figure):

        

        return cls.FigureCanvas.new_manager(figure, num)



    @classmethod

    def draw_if_interactive(cls):

        manager_class = cls.FigureCanvas.manager_class

                                                                          

        backend_is_interactive = (

            manager_class.start_main_loop != FigureManagerBase.start_main_loop

            or manager_class.pyplot_show != FigureManagerBase.pyplot_show)

        if backend_is_interactive and is_interactive():

            manager = Gcf.get_active()

            if manager:

                manager.canvas.draw_idle()



    @classmethod

    def show(cls, *, block=None):

        

        managers = Gcf.get_all_fig_managers()

        if not managers:

            return

        for manager in managers:

            try:

                manager.show()                                                

            except NonGuiException as exc:

                _api.warn_external(str(exc))

        if cls.mainloop is None:

            return

        if block is None:

                                                                           

                                                                       

                                                               

            pyplot_show = getattr(sys.modules.get("matplotlib.pyplot"), "show", None)

            ipython_pylab = hasattr(pyplot_show, "_needmain")

            block = not ipython_pylab and not is_interactive()

        if block:

            cls.mainloop()



                                                                     



    @staticmethod

    def export(cls):

        for name in [

                "backend_version",

                "FigureCanvas",

                "FigureManager",

                "new_figure_manager",

                "new_figure_manager_given_figure",

                "draw_if_interactive",

                "show",

        ]:

            setattr(sys.modules[cls.__module__], name, getattr(cls, name))



                                                               



        class Show(ShowBase):

            def mainloop(self):

                return cls.mainloop()



        setattr(sys.modules[cls.__module__], "Show", Show)

        return cls





class ShowBase(_Backend):

    



    def __call__(self, block=None):

        return self.show(block=block)


                                                                            

                                                     



"""
`matplotlib.pyplot` is a state-based interface to matplotlib. It provides
an implicit,  MATLAB-like, way of plotting.  It also opens figures on your
screen, and acts as the figure GUI manager.

pyplot is mainly intended for interactive plots and simple cases of
programmatic plot generation::

    import numpy as np
    import matplotlib.pyplot as plt

    x = np.arange(0, 5, 0.1)
    y = np.sin(x)
    plt.plot(x, y)
    plt.show()

The explicit object-oriented API is recommended for complex plots, though
pyplot is still usually used to create the figure and often the Axes in the
figure. See `.pyplot.figure`, `.pyplot.subplots`, and
`.pyplot.subplot_mosaic` to create figures, and
:doc:`Axes API </api/axes_api>` for the plotting methods on an Axes::

    import numpy as np
    import matplotlib.pyplot as plt

    x = np.arange(0, 5, 0.1)
    y = np.sin(x)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    plt.show()


See :ref:`api_interfaces` for an explanation of the tradeoffs between the
implicit and explicit interfaces.
"""



          



from __future__ import annotations



from contextlib import AbstractContextManager, ExitStack

from enum import Enum

import functools

import importlib

import inspect

import logging

import sys

import threading

import time

from typing import IO, TYPE_CHECKING, cast, overload



from cycler import cycler              

import matplotlib

import matplotlib.colorbar

import matplotlib.image

from matplotlib import _api

                                         

from matplotlib import get_backend as get_backend, rcParams as rcParams

from matplotlib import cm as cm              

from matplotlib import style as style              

from matplotlib import _pylab_helpers

from matplotlib import interactive              

from matplotlib import cbook

from matplotlib import _docstring

from matplotlib.backend_bases import (

    FigureCanvasBase, FigureManagerBase, MouseButton)

from matplotlib.figure import Figure, FigureBase, figaspect

from matplotlib.gridspec import GridSpec, SubplotSpec

from matplotlib import rcsetup, rcParamsDefault, rcParamsOrig

from matplotlib.artist import Artist

from matplotlib.axes import Axes

from matplotlib.axes import Subplot              

from matplotlib.backends import BackendFilter, backend_registry

from matplotlib.projections import PolarAxes

from matplotlib.colorizer import _ColorizerInterface, ColorizingArtist, Colorizer

from matplotlib import mlab                                    

from matplotlib.scale import get_scale_names              



from matplotlib.cm import _colormaps

from matplotlib.colors import _color_sequences, Colormap



import numpy as np



if TYPE_CHECKING:

    from collections.abc import Callable, Hashable, Iterable, Sequence

    import pathlib

    import os

    from typing import Any, BinaryIO, Literal, TypeVar

    from typing_extensions import ParamSpec



    import PIL.Image

    from numpy.typing import ArrayLike

    import pandas as pd



    import matplotlib.axes

    import matplotlib.artist

    import matplotlib.backend_bases

    from matplotlib.axis import Tick

    from matplotlib.axes._base import _AxesBase

    from matplotlib.backend_bases import (

        CloseEvent,

        DrawEvent,

        KeyEvent,

        MouseEvent,

        PickEvent,

        ResizeEvent,

    )

    from matplotlib.cm import ScalarMappable

    from matplotlib.contour import ContourSet, QuadContourSet

    from matplotlib.collections import (

        Collection,

        FillBetweenPolyCollection,

        LineCollection,

        PolyCollection,

        PathCollection,

        EventCollection,

        QuadMesh,

    )

    from matplotlib.colorbar import Colorbar

    from matplotlib.container import (

        BarContainer,

        ErrorbarContainer,

        StemContainer,

    )

    from matplotlib.figure import SubFigure

    from matplotlib.legend import Legend

    from matplotlib.mlab import GaussianKDE

    from matplotlib.image import AxesImage, FigureImage

    from matplotlib.patches import FancyArrow, StepPatch, Wedge

    from matplotlib.quiver import Barbs, Quiver, QuiverKey

    from matplotlib.scale import ScaleBase

    from matplotlib.typing import (

        CloseEventType,

        ColorType,

        CoordsType,

        DrawEventType,

        HashableList,

        KeyEventType,

        LineStyleType,

        MarkerType,

        MouseEventType,

        PickEventType,

        ResizeEventType,

        LogLevel

    )

    from matplotlib.widgets import SubplotTool



    _P = ParamSpec('_P')

    _R = TypeVar('_R')

    _T = TypeVar('_T')





                                             

from matplotlib.colors import Normalize

from matplotlib.lines import Line2D, AxLine

from matplotlib.text import Text, Annotation

from matplotlib.patches import Arrow, Circle, Rectangle              

from matplotlib.patches import Polygon

from matplotlib.widgets import Button, Slider, Widget              



from .ticker import (              

    TickHelper, Formatter, FixedFormatter, NullFormatter, FuncFormatter,

    FormatStrFormatter, ScalarFormatter, LogFormatter, LogFormatterExponent,

    LogFormatterMathtext, Locator, IndexLocator, FixedLocator, NullLocator,

    LinearLocator, LogLocator, AutoLocator, MultipleLocator, MaxNLocator)



_log = logging.getLogger(__name__)





                                                         

colormaps = _colormaps

color_sequences = _color_sequences





@overload

def _copy_docstring_and_deprecators(

    method: Any,

    func: Literal[None] = None

) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...





@overload

def _copy_docstring_and_deprecators(

    method: Any, func: Callable[_P, _R]) -> Callable[_P, _R]: ...





def _copy_docstring_and_deprecators(

    method: Any,

    func: Callable[_P, _R] | None = None

) -> Callable[[Callable[_P, _R]], Callable[_P, _R]] | Callable[_P, _R]:

    if func is None:

        return cast('Callable[[Callable[_P, _R]], Callable[_P, _R]]',

                    functools.partial(_copy_docstring_and_deprecators, method))

    decorators: list[Callable[[Callable[_P, _R]], Callable[_P, _R]]] = [

        _docstring.copy(method)

    ]

                                                                              

                                                                         

                             

    while hasattr(method, "__wrapped__"):

        potential_decorator = _api.deprecation.DECORATORS.get(method)

        if potential_decorator:

            decorators.append(potential_decorator)

        method = method.__wrapped__

    for decorator in decorators[::-1]:

        func = decorator(func)

    _add_pyplot_note(func, method)

    return func





_NO_PYPLOT_NOTE = [

    'FigureBase._gci',                           

    '_AxesBase._sci',                           

    'Artist.findobj',                                                             

                                                                                    

                                                                  

]





def _add_pyplot_note(func, wrapped_func):

    

    if not func.__doc__:

        return                 



    qualname = wrapped_func.__qualname__

    if qualname in _NO_PYPLOT_NOTE:

        return



    wrapped_func_is_method = True

    if "." not in qualname:

                                                                              

        wrapped_func_is_method = False

        link = f"{wrapped_func.__module__}.{qualname}"

    elif qualname.startswith("Axes."):                    

        link = ".axes." + qualname

    elif qualname.startswith("_AxesBase."):                               

        link = ".axes.Axes" + qualname[9:]

    elif qualname.startswith("Figure."):                          

        link = "." + qualname

    elif qualname.startswith("FigureBase."):                         

        link = ".Figure" + qualname[10:]

    elif qualname.startswith("FigureCanvasBase."):                                  

        link = "." + qualname

    else:

        raise RuntimeError(f"Wrapped method from unexpected class: {qualname}")



    if wrapped_func_is_method:

        message = f"This is the :ref:`pyplot wrapper <pyplot_interface>` for `{link}`."

    else:

        message = f"This is equivalent to `{link}`."



                                       

                                                                         

                                                                                    

                                                                                     

                                       

                                                      

    doc = inspect.cleandoc(func.__doc__)

    if "\nNotes\n-----" in doc:

        before, after = doc.split("\nNotes\n-----", 1)

    elif (index := doc.find("\nReferences\n----------")) != -1:

        before, after = doc[:index], doc[index:]

    elif (index := doc.find("\nExamples\n--------")) != -1:

        before, after = doc[:index], doc[index:]

    else:

                                                                        

        before = doc + "\n"

        after = ""



    func.__doc__ = f"{before}\nNotes\n-----\n\n.. note::\n\n    {message}\n{after}"





            





                                                          

_ReplDisplayHook = Enum("_ReplDisplayHook", ["NONE", "PLAIN", "IPYTHON"])

_REPL_DISPLAYHOOK = _ReplDisplayHook.NONE





def _draw_all_if_interactive() -> None:

    if matplotlib.is_interactive():

        draw_all()





def install_repl_displayhook() -> None:

    

    global _REPL_DISPLAYHOOK



    if _REPL_DISPLAYHOOK is _ReplDisplayHook.IPYTHON:

        return



                                                          

                                                                          

                                                        

    mod_ipython = sys.modules.get("IPython")

    if not mod_ipython:

        _REPL_DISPLAYHOOK = _ReplDisplayHook.PLAIN

        return

    ip = mod_ipython.get_ipython()

    if not ip:

        _REPL_DISPLAYHOOK = _ReplDisplayHook.PLAIN

        return



    ip.events.register("post_execute", _draw_all_if_interactive)

    _REPL_DISPLAYHOOK = _ReplDisplayHook.IPYTHON



    if mod_ipython.version_info[:2] < (8, 24):

                                                                                    

                                       

                                                                                    

                                                           

        from IPython.core.pylabtools import backend2gui

        ipython_gui_name = backend2gui.get(get_backend())

    else:

        _, ipython_gui_name = backend_registry.resolve_backend(get_backend())

                                                           

    if ipython_gui_name:

        ip.enable_gui(ipython_gui_name)





def uninstall_repl_displayhook() -> None:

    

    global _REPL_DISPLAYHOOK

    if _REPL_DISPLAYHOOK is _ReplDisplayHook.IPYTHON:

        from IPython import get_ipython

        ip = get_ipython()

        ip.events.unregister("post_execute", _draw_all_if_interactive)

    _REPL_DISPLAYHOOK = _ReplDisplayHook.NONE





draw_all = _pylab_helpers.Gcf.draw_all





                                         

@_copy_docstring_and_deprecators(matplotlib.set_loglevel)

def set_loglevel(level: LogLevel) -> None:

    return matplotlib.set_loglevel(level)





@_copy_docstring_and_deprecators(Artist.findobj)

def findobj(

    o: Artist | None = None,

    match: Callable[[Artist], bool] | type[Artist] | None = None,

    include_self: bool = True

) -> list[Artist]:

    if o is None:

        o = gcf()

    return o.findobj(match, include_self=include_self)





_backend_mod: type[matplotlib.backend_bases._Backend] | None = None





def _get_backend_mod() -> type[matplotlib.backend_bases._Backend]:

    

    if _backend_mod is None:

                                                                          

                                                                             

                                               

        switch_backend(rcParams._get("backend"))

    return cast(type[matplotlib.backend_bases._Backend], _backend_mod)





def switch_backend(newbackend: str) -> None:

    

    global _backend_mod

                                                                  

    import matplotlib.backends



    if newbackend is rcsetup._auto_backend_sentinel:

        current_framework = cbook._get_running_interactive_framework()



        if (current_framework and

                (backend := backend_registry.backend_for_gui_framework(

                    current_framework))):

            candidates = [backend]

        else:

            candidates = []

        candidates += [

            "macosx", "qtagg", "gtk4agg", "gtk3agg", "tkagg", "wxagg"]



                                                                             

                                                                            

                               

        for candidate in candidates:

            try:

                switch_backend(candidate)

            except ImportError:

                continue

            else:

                rcParamsOrig['backend'] = candidate

                return

        else:

                                                                            

                                      

            switch_backend("agg")

            rcParamsOrig["backend"] = "agg"

            return

    old_backend = rcParams._get('backend')                                             



    module = backend_registry.load_backend_module(newbackend)

    canvas_class = module.FigureCanvas



    required_framework = canvas_class.required_interactive_framework

    if required_framework is not None:

        current_framework = cbook._get_running_interactive_framework()

        if (current_framework and required_framework

                and current_framework != required_framework):

            raise ImportError(

                "Cannot load backend {!r} which requires the {!r} interactive "

                "framework, as {!r} is currently running".format(

                    newbackend, required_framework, current_framework))



                                                                          



                                                                             

                                  

    new_figure_manager = getattr(module, "new_figure_manager", None)

    show = getattr(module, "show", None)



                                                                          

                                                                           

                                                               

                                                                              

    class backend_mod(matplotlib.backend_bases._Backend):

        locals().update(vars(module))



                                                                     

                                                                     

                                                                        

                                      

    if new_figure_manager is None:



        def new_figure_manager_given_figure(num, figure):

            return canvas_class.new_manager(figure, num)



        def new_figure_manager(num, *args, FigureClass=Figure, **kwargs):

            fig = FigureClass(*args, **kwargs)

            return new_figure_manager_given_figure(num, fig)



        def draw_if_interactive() -> None:

            if matplotlib.is_interactive():

                manager = _pylab_helpers.Gcf.get_active()

                if manager:

                    manager.canvas.draw_idle()



        backend_mod.new_figure_manager_given_figure = (                               

            new_figure_manager_given_figure)

        backend_mod.new_figure_manager = (                               

            new_figure_manager)

        backend_mod.draw_if_interactive = (                               

            draw_if_interactive)



                                                                              

                                                                        

    manager_class = getattr(canvas_class, "manager_class", None)

                                                                                     

                                                                                      

                                                                                    

                                                                             

    manager_pyplot_show = inspect.getattr_static(manager_class, "pyplot_show", None)

    base_pyplot_show = inspect.getattr_static(FigureManagerBase, "pyplot_show", None)

    if (show is None

            or (manager_pyplot_show is not None

                and manager_pyplot_show != base_pyplot_show)):

        if not manager_pyplot_show:

            raise ValueError(

                f"Backend {newbackend} defines neither FigureCanvas.manager_class nor "

                f"a toplevel show function")

        _pyplot_show = cast('Any', manager_class).pyplot_show

        backend_mod.show = _pyplot_show                               



    _log.debug("Loaded backend %s version %s.",

               newbackend, backend_mod.backend_version)



    if newbackend in ("ipympl", "widget"):

                                                                                      

                                                                                    

        import importlib.metadata as im

        from matplotlib import _parse_to_version_info                              

        try:

            module_version = im.version("ipympl")

            if _parse_to_version_info(module_version) < (0, 9, 4):

                newbackend = "module://ipympl.backend_nbagg"

        except im.PackageNotFoundError:

            pass



    rcParams['backend'] = rcParamsDefault['backend'] = newbackend

    _backend_mod = backend_mod

    for func_name in ["new_figure_manager", "draw_if_interactive", "show"]:

        globals()[func_name].__signature__ = inspect.signature(

            getattr(backend_mod, func_name))



                                                                               

                                                              

    matplotlib.backends.backend = newbackend                              



                                                                                 

    try:

        install_repl_displayhook()

    except NotImplementedError as err:

        _log.warning("Fallback to a different backend")

        raise ImportError from err





def _warn_if_gui_out_of_main_thread() -> None:

    warn = False

    canvas_class = cast(type[FigureCanvasBase], _get_backend_mod().FigureCanvas)

    if canvas_class.required_interactive_framework:

        if hasattr(threading, 'get_native_id'):

                                                                          

                                                                           

                                                                             

                            

            if threading.get_native_id() != threading.main_thread().native_id:

                warn = True

        else:

                                                                             

                              

            if threading.current_thread() is not threading.main_thread():

                warn = True

    if warn:

        _api.warn_external(

            "Starting a Matplotlib GUI outside of the main thread will likely "

            "fail.")





                                                                             

def new_figure_manager(*args, **kwargs):

    

    _warn_if_gui_out_of_main_thread()

    return _get_backend_mod().new_figure_manager(*args, **kwargs)





                                                                             

def draw_if_interactive(*args, **kwargs):

    

    return _get_backend_mod().draw_if_interactive(*args, **kwargs)





@overload

def show(*, block: bool, **kwargs) -> None: ...





@overload

def show(*args: Any, **kwargs: Any) -> None: ...





                                                                             

def show(*args, **kwargs) -> None:

    

    _warn_if_gui_out_of_main_thread()

    return _get_backend_mod().show(*args, **kwargs)





def isinteractive() -> bool:

    

    return matplotlib.is_interactive()





                                                            

                                     

                                                           

                                                                        

def ioff() -> AbstractContextManager:

    

    stack = ExitStack()

    stack.callback(ion if isinteractive() else ioff)

    matplotlib.interactive(False)

    uninstall_repl_displayhook()

    return stack





                                                           

                                     

                                                           

                                                                        

def ion() -> AbstractContextManager:

    

    stack = ExitStack()

    stack.callback(ion if isinteractive() else ioff)

    matplotlib.interactive(True)

    install_repl_displayhook()

    return stack





def pause(interval: float) -> None:

    

    manager = _pylab_helpers.Gcf.get_active()

    if manager is not None:

        canvas = manager.canvas

        if canvas.figure.stale:

            canvas.draw_idle()

        show(block=False)

        canvas.start_event_loop(interval)

    else:

        time.sleep(interval)





@_copy_docstring_and_deprecators(matplotlib.rc)

def rc(group: str, **kwargs) -> None:

    matplotlib.rc(group, **kwargs)





@_copy_docstring_and_deprecators(matplotlib.rc_context)

def rc_context(

    rc: dict[str, Any] | None = None,

    fname: str | pathlib.Path | os.PathLike | None = None,

) -> AbstractContextManager[None]:

    return matplotlib.rc_context(rc, fname)





@_copy_docstring_and_deprecators(matplotlib.rcdefaults)

def rcdefaults() -> None:

    matplotlib.rcdefaults()

    if matplotlib.is_interactive():

        draw_all()





                                                                              





@_copy_docstring_and_deprecators(matplotlib.artist.getp)

def getp(obj, *args, **kwargs):

    return matplotlib.artist.getp(obj, *args, **kwargs)





@_copy_docstring_and_deprecators(matplotlib.artist.get)

def get(obj, *args, **kwargs):

    return matplotlib.artist.get(obj, *args, **kwargs)





@_copy_docstring_and_deprecators(matplotlib.artist.setp)

def setp(obj, *args, **kwargs):

    return matplotlib.artist.setp(obj, *args, **kwargs)





def xkcd(

    scale: float = 1, length: float = 100, randomness: float = 2

) -> ExitStack:

    

                                                                             

                                                             



    if rcParams['text.usetex']:

        raise RuntimeError(

            "xkcd mode is not compatible with text.usetex = True")



    stack = ExitStack()

    stack.callback(rcParams._update_raw, rcParams.copy())                          



    from matplotlib import patheffects

    rcParams.update({

        'font.family': ['xkcd', 'xkcd Script', 'Comic Neue', 'Comic Sans MS'],

        'font.size': 14.0,

        'path.sketch': (scale, length, randomness),

        'path.effects': [

            patheffects.withStroke(linewidth=4, foreground="w")],

        'axes.linewidth': 1.5,

        'lines.linewidth': 2.0,

        'figure.facecolor': 'white',

        'grid.linewidth': 0.0,

        'axes.grid': False,

        'axes.unicode_minus': False,

        'axes.edgecolor': 'black',

        'xtick.major.size': 8,

        'xtick.major.width': 3,

        'ytick.major.size': 8,

        'ytick.major.width': 3,

    })



    return stack





             



def figure(

                                                  

    num: int | str | Figure | SubFigure | None = None,

                                   

    figsize: ArrayLike                                           

             | tuple[float, float, Literal["in", "cm", "px"]]

             | None = None,

                               

    dpi: float | None = None,

    *,

                                     

    facecolor: ColorType | None = None,

                                     

    edgecolor: ColorType | None = None,

    frameon: bool = True,

    FigureClass: type[Figure] = Figure,

    clear: bool = False,

    **kwargs

) -> Figure:

    

    allnums = get_fignums()



    if isinstance(num, FigureBase):

                                                                                      

        root_fig = num.get_figure(root=True)

        if root_fig.canvas.manager is None:

            raise ValueError("The passed figure is not managed by pyplot")

        elif (any(param is not None for param in [figsize, dpi, facecolor, edgecolor])

              or not frameon or kwargs) and root_fig.canvas.manager.num in allnums:

            _api.warn_external(

                "Ignoring specified arguments in this call because figure "

                f"with num: {root_fig.canvas.manager.num} already exists")

        _pylab_helpers.Gcf.set_active(root_fig.canvas.manager)

        return root_fig



    next_num = max(allnums) + 1 if allnums else 1

    fig_label = ''

    if num is None:

        num = next_num

    else:

        if (any(param is not None for param in [figsize, dpi, facecolor, edgecolor])

              or not frameon or kwargs) and num in allnums:

            _api.warn_external(

                "Ignoring specified arguments in this call "

                f"because figure with num: {num} already exists")

        if isinstance(num, str):

            fig_label = num

            all_labels = get_figlabels()

            if fig_label not in all_labels:

                if fig_label == 'all':

                    _api.warn_external("close('all') closes all existing figures.")

                num = next_num

            else:

                inum = all_labels.index(fig_label)

                num = allnums[inum]

        else:

            num = int(num)                                    



                                                                    

    manager = _pylab_helpers.Gcf.get_fig_manager(num)                          

    if manager is None:

        max_open_warning = rcParams['figure.max_open_warning']

        if len(allnums) == max_open_warning >= 1:

            _api.warn_external(

                f"More than {max_open_warning} figures have been opened. "

                f"Figures created through the pyplot interface "

                f"(`matplotlib.pyplot.figure`) are retained until explicitly "

                f"closed and may consume too much memory. (To control this "

                f"warning, see the rcParam `figure.max_open_warning`). "

                f"Consider using `matplotlib.pyplot.close()`.",

                RuntimeWarning)



        manager = new_figure_manager(

            num, figsize=figsize, dpi=dpi,

            facecolor=facecolor, edgecolor=edgecolor, frameon=frameon,

            FigureClass=FigureClass, **kwargs)

        fig = manager.canvas.figure

        if fig_label:

            fig.set_label(fig_label)



        for hookspecs in rcParams["figure.hooks"]:

            module_name, dotted_name = hookspecs.split(":")

            obj: Any = importlib.import_module(module_name)

            for part in dotted_name.split("."):

                obj = getattr(obj, part)

            obj(fig)



        _pylab_helpers.Gcf._set_new_active_manager(manager)



                                                                         

                                                                        

                                                                       

                                   

        draw_if_interactive()



        if _REPL_DISPLAYHOOK is _ReplDisplayHook.PLAIN:

            fig.stale_callback = _auto_draw_if_interactive



    if clear:

        manager.canvas.figure.clear()



    return manager.canvas.figure





def _auto_draw_if_interactive(fig, val):

    

    if (val and matplotlib.is_interactive()

            and not fig.canvas.is_saving()

            and not fig.canvas._is_idle_drawing):

                                                                            

                                                                             

                                                                         

                                         

        with fig.canvas._idle_draw_cntx():

            fig.canvas.draw_idle()





def gcf() -> Figure:

    

    manager = _pylab_helpers.Gcf.get_active()

    if manager is not None:

        return manager.canvas.figure

    else:

        return figure()





def fignum_exists(num: int | str) -> bool:

    

    return (

        _pylab_helpers.Gcf.has_fignum(num)

        if isinstance(num, int)

        else num in get_figlabels()

    )





def get_fignums() -> list[int]:

    

    return sorted(_pylab_helpers.Gcf.figs)





def get_figlabels() -> list[Any]:

    

    managers = _pylab_helpers.Gcf.get_all_fig_managers()

    managers.sort(key=lambda m: m.num)

    return [m.canvas.figure.get_label() for m in managers]





def get_current_fig_manager() -> FigureManagerBase | None:

    

    return gcf().canvas.manager





@overload

def connect(s: MouseEventType, func: Callable[[MouseEvent], Any]) -> int: ...





@overload

def connect(s: KeyEventType, func: Callable[[KeyEvent], Any]) -> int: ...





@overload

def connect(s: PickEventType, func: Callable[[PickEvent], Any]) -> int: ...





@overload

def connect(s: ResizeEventType, func: Callable[[ResizeEvent], Any]) -> int: ...





@overload

def connect(s: CloseEventType, func: Callable[[CloseEvent], Any]) -> int: ...





@overload

def connect(s: DrawEventType, func: Callable[[DrawEvent], Any]) -> int: ...





@_copy_docstring_and_deprecators(FigureCanvasBase.mpl_connect)

def connect(s, func) -> int:

    return gcf().canvas.mpl_connect(s, func)





@_copy_docstring_and_deprecators(FigureCanvasBase.mpl_disconnect)

def disconnect(cid: int) -> None:

    gcf().canvas.mpl_disconnect(cid)





def close(fig: None | int | str | Figure | Literal["all"] = None) -> None:

    

    if fig is None:

        manager = _pylab_helpers.Gcf.get_active()

        if manager is None:

            return

        else:

            _pylab_helpers.Gcf.destroy(manager)

    elif fig == 'all':

        _pylab_helpers.Gcf.destroy_all()

    elif isinstance(fig, int):

        _pylab_helpers.Gcf.destroy(fig)

    elif hasattr(fig, 'int'):                                            

        _pylab_helpers.Gcf.destroy(fig.int)

    elif isinstance(fig, str):

        all_labels = get_figlabels()

        if fig in all_labels:

            num = get_fignums()[all_labels.index(fig)]

            _pylab_helpers.Gcf.destroy(num)

    elif isinstance(fig, Figure):

        _pylab_helpers.Gcf.destroy_fig(fig)

    else:

        _api.check_isinstance(                             

            (Figure, int, str, None), fig=fig)





def clf() -> None:

    

    gcf().clear()





def draw() -> None:

    

    gcf().canvas.draw_idle()





@_copy_docstring_and_deprecators(Figure.savefig)

def savefig(fname: str | os.PathLike | IO, **kwargs) -> None:

    fig = gcf()

                                                                      

                                                            

    res = fig.savefig(fname, **kwargs)                                    

    fig.canvas.draw_idle()                                                     

    return res





                               





def figlegend(*args, **kwargs) -> Legend:

    return gcf().legend(*args, **kwargs)

if Figure.legend.__doc__:

    figlegend.__doc__ = Figure.legend.__doc__
        .replace(" legend(", " figlegend(")
        .replace("fig.legend(", "plt.figlegend(")
        .replace("ax.plot(", "plt.plot(")





          



@_docstring.interpd

def axes(

    arg: None | tuple[float, float, float, float] = None,

    **kwargs

) -> matplotlib.axes.Axes:

    

    fig = gcf()

    pos = kwargs.pop('position', None)

    if arg is None:

        if pos is None:

            return fig.add_subplot(**kwargs)

        else:

            return fig.add_axes(pos, **kwargs)

    else:

        return fig.add_axes(arg, **kwargs)





def delaxes(ax: matplotlib.axes.Axes | None = None) -> None:

    

    if ax is None:

        ax = gca()

    ax.remove()





def sca(ax: Axes) -> None:

    

                                              

                                                   

                                                                                       

    fig = ax.get_figure(root=False)

    figure(fig)                          

    fig.sca(ax)                            





def cla() -> None:

    

                                                                      

    return gca().cla()





                                



@overload

def subplot(nrows: int, ncols: int, index: int, /, **kwargs): ...





@overload

def subplot(pos: int | SubplotSpec, /, **kwargs): ...





@overload

def subplot(**kwargs): ...





@_docstring.interpd

def subplot(*args, **kwargs) -> Axes:

    

                                                                              

                                         

    unset = object()

    projection = kwargs.get('projection', unset)

    polar = kwargs.pop('polar', unset)

    if polar is not unset and polar:

                                                       

        if projection is not unset and projection != 'polar':

            raise ValueError(

                f"polar={polar}, yet projection={projection!r}. "

                "Only one of these arguments should be supplied."

            )

        kwargs['projection'] = projection = 'polar'



                                                                  

    if len(args) == 0:

        args = (1, 1, 1)



                                                                               

                                                                              

                                                                         

                                                                               

                                   

    if len(args) >= 3 and isinstance(args[2], bool):

        _api.warn_external("The subplot index argument to subplot() appears "

                           "to be a boolean. Did you intend to use "

                           "subplots()?")

                                                                  

    if 'nrows' in kwargs or 'ncols' in kwargs:

        raise TypeError("subplot() got an unexpected keyword argument 'ncols' "

                        "and/or 'nrows'.  Did you intend to call subplots()?")



    fig = gcf()



                                                                 

    key = SubplotSpec._from_subplot_args(fig, args)



    for ax in fig.axes:

                                                                                    

                                                               

        if (ax.get_subplotspec() == key

            and (kwargs == {}

                 or (ax._projection_init

                     == fig._process_projection_requirements(**kwargs)))):

            break

    else:

                                                                          

        ax = fig.add_subplot(*args, **kwargs)



    fig.sca(ax)



    return ax





@overload

def subplots(

    nrows: Literal[1] = ...,

    ncols: Literal[1] = ...,

    *,

    sharex: bool | Literal["none", "all", "row", "col"] = ...,

    sharey: bool | Literal["none", "all", "row", "col"] = ...,

    squeeze: Literal[True] = ...,

    width_ratios: Sequence[float] | None = ...,

    height_ratios: Sequence[float] | None = ...,

    subplot_kw: dict[str, Any] | None = ...,

    gridspec_kw: dict[str, Any] | None = ...,

    **fig_kw

) -> tuple[Figure, Axes]:

    ...





@overload

def subplots(

    nrows: int = ...,

    ncols: int = ...,

    *,

    sharex: bool | Literal["none", "all", "row", "col"] = ...,

    sharey: bool | Literal["none", "all", "row", "col"] = ...,

    squeeze: Literal[False],

    width_ratios: Sequence[float] | None = ...,

    height_ratios: Sequence[float] | None = ...,

    subplot_kw: dict[str, Any] | None = ...,

    gridspec_kw: dict[str, Any] | None = ...,

    **fig_kw

) -> tuple[Figure, np.ndarray]:                          

    ...





@overload

def subplots(

    nrows: int = ...,

    ncols: int = ...,

    *,

    sharex: bool | Literal["none", "all", "row", "col"] = ...,

    sharey: bool | Literal["none", "all", "row", "col"] = ...,

    squeeze: bool = ...,

    width_ratios: Sequence[float] | None = ...,

    height_ratios: Sequence[float] | None = ...,

    subplot_kw: dict[str, Any] | None = ...,

    gridspec_kw: dict[str, Any] | None = ...,

    **fig_kw

) -> tuple[Figure, Any]:

    ...





def subplots(

    nrows: int = 1, ncols: int = 1, *,

    sharex: bool | Literal["none", "all", "row", "col"] = False,

    sharey: bool | Literal["none", "all", "row", "col"] = False,

    squeeze: bool = True,

    width_ratios: Sequence[float] | None = None,

    height_ratios: Sequence[float] | None = None,

    subplot_kw: dict[str, Any] | None = None,

    gridspec_kw: dict[str, Any] | None = None,

    **fig_kw

) -> tuple[Figure, Any]:

    

    fig = figure(**fig_kw)

    axs = fig.subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey,

                       squeeze=squeeze, subplot_kw=subplot_kw,

                       gridspec_kw=gridspec_kw, height_ratios=height_ratios,

                       width_ratios=width_ratios)

    return fig, axs





@overload

def subplot_mosaic(

    mosaic: str,

    *,

    sharex: bool = ...,

    sharey: bool = ...,

    width_ratios: ArrayLike | None = ...,

    height_ratios: ArrayLike | None = ...,

    empty_sentinel: str = ...,

    subplot_kw: dict[str, Any] | None = ...,

    gridspec_kw: dict[str, Any] | None = ...,

    per_subplot_kw: dict[str | tuple[str, ...], dict[str, Any]] | None = ...,

    **fig_kw: Any

) -> tuple[Figure, dict[str, matplotlib.axes.Axes]]: ...





@overload

def subplot_mosaic(

    mosaic: list[HashableList[_T]],

    *,

    sharex: bool = ...,

    sharey: bool = ...,

    width_ratios: ArrayLike | None = ...,

    height_ratios: ArrayLike | None = ...,

    empty_sentinel: _T = ...,

    subplot_kw: dict[str, Any] | None = ...,

    gridspec_kw: dict[str, Any] | None = ...,

    per_subplot_kw: dict[_T | tuple[_T, ...], dict[str, Any]] | None = ...,

    **fig_kw: Any

) -> tuple[Figure, dict[_T, matplotlib.axes.Axes]]: ...





@overload

def subplot_mosaic(

    mosaic: list[HashableList[Hashable]],

    *,

    sharex: bool = ...,

    sharey: bool = ...,

    width_ratios: ArrayLike | None = ...,

    height_ratios: ArrayLike | None = ...,

    empty_sentinel: Any = ...,

    subplot_kw: dict[str, Any] | None = ...,

    gridspec_kw: dict[str, Any] | None = ...,

    per_subplot_kw: dict[Hashable | tuple[Hashable, ...], dict[str, Any]] | None = ...,

    **fig_kw: Any

) -> tuple[Figure, dict[Hashable, matplotlib.axes.Axes]]: ...





def subplot_mosaic(

    mosaic: str | list[HashableList[_T]] | list[HashableList[Hashable]],

    *,

    sharex: bool = False,

    sharey: bool = False,

    width_ratios: ArrayLike | None = None,

    height_ratios: ArrayLike | None = None,

    empty_sentinel: Any = '.',

    subplot_kw: dict[str, Any] | None = None,

    gridspec_kw: dict[str, Any] | None = None,

    per_subplot_kw: dict[str | tuple[str, ...], dict[str, Any]] |

                    dict[_T | tuple[_T, ...], dict[str, Any]] |

                    dict[Hashable | tuple[Hashable, ...], dict[str, Any]] | None = None,

    **fig_kw: Any

) -> tuple[Figure, dict[str, matplotlib.axes.Axes]] |
     tuple[Figure, dict[_T, matplotlib.axes.Axes]] |
     tuple[Figure, dict[Hashable, matplotlib.axes.Axes]]:

    

    fig = figure(**fig_kw)

    ax_dict = fig.subplot_mosaic(                      

        mosaic,                          

        sharex=sharex, sharey=sharey,

        height_ratios=height_ratios, width_ratios=width_ratios,

        subplot_kw=subplot_kw, gridspec_kw=gridspec_kw,

        empty_sentinel=empty_sentinel,

        per_subplot_kw=per_subplot_kw,                          

    )

    return fig, ax_dict





def subplot2grid(

    shape: tuple[int, int], loc: tuple[int, int],

    rowspan: int = 1, colspan: int = 1,

    fig: Figure | None = None,

    **kwargs

) -> matplotlib.axes.Axes:

    

    if fig is None:

        fig = gcf()

    rows, cols = shape

    gs = GridSpec._check_gridspec_exists(fig, rows, cols)

    subplotspec = gs.new_subplotspec(loc, rowspan=rowspan, colspan=colspan)

    return fig.add_subplot(subplotspec, **kwargs)





def twinx(ax: matplotlib.axes.Axes | None = None) -> _AxesBase:

    

    if ax is None:

        ax = gca()

    ax1 = ax.twinx()

    return ax1





def twiny(ax: matplotlib.axes.Axes | None = None) -> _AxesBase:

    

    if ax is None:

        ax = gca()

    ax1 = ax.twiny()

    return ax1





def subplot_tool(targetfig: Figure | None = None) -> SubplotTool | None:

    

    if targetfig is None:

        targetfig = gcf()

    tb = targetfig.canvas.manager.toolbar                            

    if hasattr(tb, "configure_subplots"):            

        from matplotlib.backend_bases import NavigationToolbar2

        return cast(NavigationToolbar2, tb).configure_subplots()

    elif hasattr(tb, "trigger_tool"):               

        from matplotlib.backend_bases import ToolContainerBase

        cast(ToolContainerBase, tb).trigger_tool("subplots")

        return None

    else:

        raise ValueError("subplot_tool can only be launched for figures with "

                         "an associated toolbar")





def box(on: bool | None = None) -> None:

    

    ax = gca()

    if on is None:

        on = not ax.get_frame_on()

    ax.set_frame_on(on)



          





@overload

def xlim() -> tuple[float, float]:

    ...





@overload

def xlim(

        left: float | tuple[float, float] | None = None,

        right: float | None = None,

        *,

        emit: bool = True,

        auto: bool | None = False,

        xmin: float | None = None,

        xmax: float | None = None,

) -> tuple[float, float]:

    ...





def xlim(*args, **kwargs) -> tuple[float, float]:

    

    ax = gca()

    if not args and not kwargs:

        return ax.get_xlim()

    ret = ax.set_xlim(*args, **kwargs)

    return ret





@overload

def ylim() -> tuple[float, float]:

    ...





@overload

def ylim(

        bottom: float | tuple[float, float] | None = None,

        top: float | None = None,

        *,

        emit: bool = True,

        auto: bool | None = False,

        ymin: float | None = None,

        ymax: float | None = None,

) -> tuple[float, float]:

    ...





def ylim(*args, **kwargs) -> tuple[float, float]:

    

    ax = gca()

    if not args and not kwargs:

        return ax.get_ylim()

    ret = ax.set_ylim(*args, **kwargs)

    return ret





def xticks(

    ticks: ArrayLike | None = None,

    labels: Sequence[str] | None = None,

    *,

    minor: bool = False,

    **kwargs

) -> tuple[list[Tick] | np.ndarray, list[Text]]:

    

    ax = gca()



    locs: list[Tick] | np.ndarray

    if ticks is None:

        locs = ax.get_xticks(minor=minor)

        if labels is not None:

            raise TypeError("xticks(): Parameter 'labels' can't be set "

                            "without setting 'ticks'")

    else:

        locs = ax.set_xticks(ticks, minor=minor)



    labels_out: list[Text] = []

    if labels is None:

        labels_out = ax.get_xticklabels(minor=minor)

        for l in labels_out:

            l._internal_update(kwargs)

    else:

        labels_out = ax.set_xticklabels(labels, minor=minor, **kwargs)



    return locs, labels_out





def yticks(

    ticks: ArrayLike | None = None,

    labels: Sequence[str] | None = None,

    *,

    minor: bool = False,

    **kwargs

) -> tuple[list[Tick] | np.ndarray, list[Text]]:

    

    ax = gca()



    locs: list[Tick] | np.ndarray

    if ticks is None:

        locs = ax.get_yticks(minor=minor)

        if labels is not None:

            raise TypeError("yticks(): Parameter 'labels' can't be set "

                            "without setting 'ticks'")

    else:

        locs = ax.set_yticks(ticks, minor=minor)



    labels_out: list[Text] = []

    if labels is None:

        labels_out = ax.get_yticklabels(minor=minor)

        for l in labels_out:

            l._internal_update(kwargs)

    else:

        labels_out = ax.set_yticklabels(labels, minor=minor, **kwargs)



    return locs, labels_out





def rgrids(

    radii: ArrayLike | None = None,

    labels: Sequence[str | Text] | None = None,

    angle: float | None = None,

    fmt: str | None = None,

    **kwargs

) -> tuple[list[Line2D], list[Text]]:

    

    ax = gca()

    if not isinstance(ax, PolarAxes):

        raise RuntimeError('rgrids only defined for polar Axes')

    if all(p is None for p in [radii, labels, angle, fmt]) and not kwargs:

        lines_out: list[Line2D] = ax.yaxis.get_gridlines()

        labels_out: list[Text] = ax.yaxis.get_ticklabels()

    elif radii is None:

        raise TypeError("'radii' cannot be None when other parameters are passed")

    else:

        lines_out, labels_out = ax.set_rgrids(

            radii, labels=labels, angle=angle, fmt=fmt, **kwargs)

    return lines_out, labels_out





def thetagrids(

    angles: ArrayLike | None = None,

    labels: Sequence[str | Text] | None = None,

    fmt: str | None = None,

    **kwargs

) -> tuple[list[Line2D], list[Text]]:

    

    ax = gca()

    if not isinstance(ax, PolarAxes):

        raise RuntimeError('thetagrids only defined for polar Axes')

    if all(param is None for param in [angles, labels, fmt]) and not kwargs:

        lines_out: list[Line2D] = ax.xaxis.get_ticklines()

        labels_out: list[Text] = ax.xaxis.get_ticklabels()

    elif angles is None:

        raise TypeError("'angles' cannot be None when other parameters are passed")

    else:

        lines_out, labels_out = ax.set_thetagrids(angles,

                                                  labels=labels, fmt=fmt,

                                                  **kwargs)

    return lines_out, labels_out





@_api.deprecated("3.7", pending=True)

def get_plot_commands() -> list[str]:

    

    NON_PLOT_COMMANDS = {

        'connect', 'disconnect', 'get_current_fig_manager', 'ginput',

        'new_figure_manager', 'waitforbuttonpress'}

    return [name for name in _get_pyplot_commands()

            if name not in NON_PLOT_COMMANDS]





def _get_pyplot_commands() -> list[str]:

                                                                           

                                                                         

                                                                            

    exclude = {'colormaps', 'colors', 'get_plot_commands', *colormaps}

    this_module = inspect.getmodule(get_plot_commands)

    return sorted(

        name for name, obj in globals().items()

        if not name.startswith('_') and name not in exclude

           and inspect.isfunction(obj)

           and inspect.getmodule(obj) is this_module)





                                                                





@_copy_docstring_and_deprecators(Figure.colorbar)

def colorbar(

    mappable: ScalarMappable | ColorizingArtist | None = None,

    cax: matplotlib.axes.Axes | None = None,

    ax: matplotlib.axes.Axes | Iterable[matplotlib.axes.Axes] | None = None,

    **kwargs

) -> Colorbar:

    if mappable is None:

        mappable = gci()

        if mappable is None:

            raise RuntimeError('No mappable was found to use for colorbar '

                               'creation. First define a mappable such as '

                               'an image (with imshow) or a contour set ('

                               'with contourf).')

    ret = gcf().colorbar(mappable, cax=cax, ax=ax, **kwargs)

    return ret





def clim(vmin: float | None = None, vmax: float | None = None) -> None:

    

    im = gci()

    if im is None:

        raise RuntimeError('You must first define an image, e.g., with imshow')



    im.set_clim(vmin, vmax)





def get_cmap(name: Colormap | str | None = None, lut: int | None = None) -> Colormap:

    

    if name is None:

        name = rcParams['image.cmap']

    if isinstance(name, Colormap):

        return name

    _api.check_in_list(sorted(_colormaps), name=name)

    if lut is None:

        return _colormaps[name]

    else:

        return _colormaps[name].resampled(lut)





def set_cmap(cmap: Colormap | str) -> None:

    

    cmap = get_cmap(cmap)



    rc('image', cmap=cmap.name)

    im = gci()



    if im is not None:

        im.set_cmap(cmap)





@_copy_docstring_and_deprecators(matplotlib.image.imread)

def imread(

        fname: str | pathlib.Path | BinaryIO, format: str | None = None

) -> np.ndarray:

    return matplotlib.image.imread(fname, format)





@_copy_docstring_and_deprecators(matplotlib.image.imsave)

def imsave(

    fname: str | os.PathLike | BinaryIO, arr: ArrayLike, **kwargs

) -> None:

    matplotlib.image.imsave(fname, arr, **kwargs)





def matshow(A: ArrayLike, fignum: None | int = None, **kwargs) -> AxesImage:

    

    A = np.asanyarray(A)

    if fignum == 0:

        ax = gca()

    else:

        if fignum is not None and fignum_exists(fignum):

                                              

            figsize = None

        else:

                                                                                       

            figsize = figaspect(A)

        fig = figure(fignum, figsize=figsize)

        ax = fig.add_axes((0.15, 0.09, 0.775, 0.775))

    im = ax.matshow(A, **kwargs)

    sci(im)

    return im





def polar(*args, **kwargs) -> list[Line2D]:

    

                                                                   

    if gcf().get_axes():

        ax = gca()

        if not isinstance(ax, PolarAxes):

            _api.warn_deprecated(

                "3.10",

                message="There exists a non-polar current Axes. Therefore, the "

                        "resulting plot from 'polar()' is non-polar. You likely "

                        "should call 'polar()' before any other pyplot plotting "

                        "commands. "

                        "Support for this scenario is deprecated in %(since)s and "

                        "will raise an error in %(removal)s"

            )

    else:

        ax = axes(projection="polar")

    return ax.plot(*args, **kwargs)





                                                                        

                                                                             

                                                               

if rcParams["backend_fallback"]:

    requested_backend = rcParams._get_backend_or_none()                              

    requested_backend = None if requested_backend is None else requested_backend.lower()

    available_backends = backend_registry.list_builtin(BackendFilter.INTERACTIVE)

    if (

        requested_backend in (set(available_backends) - {'webagg', 'nbagg'})

        and cbook._get_running_interactive_framework()

    ):

        rcParams._set("backend", rcsetup._auto_backend_sentinel)



         



                                                                              





                                                                        

@_copy_docstring_and_deprecators(Figure.figimage)

def figimage(

    X: ArrayLike,

    xo: int = 0,

    yo: int = 0,

    alpha: float | None = None,

    norm: str | Normalize | None = None,

    cmap: str | Colormap | None = None,

    vmin: float | None = None,

    vmax: float | None = None,

    origin: Literal["upper", "lower"] | None = None,

    resize: bool = False,

    *,

    colorizer: Colorizer | None = None,

    **kwargs,

) -> FigureImage:

    return gcf().figimage(

        X,

        xo=xo,

        yo=yo,

        alpha=alpha,

        norm=norm,

        cmap=cmap,

        vmin=vmin,

        vmax=vmax,

        origin=origin,

        resize=resize,

        colorizer=colorizer,

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Figure.text)

def figtext(

    x: float, y: float, s: str, fontdict: dict[str, Any] | None = None, **kwargs

) -> Text:

    return gcf().text(x, y, s, fontdict=fontdict, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Figure.gca)

def gca() -> Axes:

    return gcf().gca()





                                                                        

@_copy_docstring_and_deprecators(Figure._gci)

def gci() -> ColorizingArtist | None:

    return gcf()._gci()





                                                                        

@_copy_docstring_and_deprecators(Figure.ginput)

def ginput(

    n: int = 1,

    timeout: float = 30,

    show_clicks: bool = True,

    mouse_add: MouseButton = MouseButton.LEFT,

    mouse_pop: MouseButton = MouseButton.RIGHT,

    mouse_stop: MouseButton = MouseButton.MIDDLE,

) -> list[tuple[int, int]]:

    return gcf().ginput(

        n=n,

        timeout=timeout,

        show_clicks=show_clicks,

        mouse_add=mouse_add,

        mouse_pop=mouse_pop,

        mouse_stop=mouse_stop,

    )





                                                                        

@_copy_docstring_and_deprecators(Figure.subplots_adjust)

def subplots_adjust(

    left: float | None = None,

    bottom: float | None = None,

    right: float | None = None,

    top: float | None = None,

    wspace: float | None = None,

    hspace: float | None = None,

) -> None:

    gcf().subplots_adjust(

        left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace

    )





                                                                        

@_copy_docstring_and_deprecators(Figure.suptitle)

def suptitle(t: str, **kwargs) -> Text:

    return gcf().suptitle(t, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Figure.tight_layout)

def tight_layout(

    *,

    pad: float = 1.08,

    h_pad: float | None = None,

    w_pad: float | None = None,

    rect: tuple[float, float, float, float] | None = None,

) -> None:

    gcf().tight_layout(pad=pad, h_pad=h_pad, w_pad=w_pad, rect=rect)





                                                                        

@_copy_docstring_and_deprecators(Figure.waitforbuttonpress)

def waitforbuttonpress(timeout: float = -1) -> None | bool:

    return gcf().waitforbuttonpress(timeout=timeout)





                                                                        

@_copy_docstring_and_deprecators(Axes.acorr)

def acorr(

    x: ArrayLike, *, data=None, **kwargs

) -> tuple[np.ndarray, np.ndarray, LineCollection | Line2D, Line2D | None]:

    return gca().acorr(x, **({"data": data} if data is not None else {}), **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.angle_spectrum)

def angle_spectrum(

    x: ArrayLike,

    Fs: float | None = None,

    Fc: int | None = None,

    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,

    pad_to: int | None = None,

    sides: Literal["default", "onesided", "twosided"] | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray, Line2D]:

    return gca().angle_spectrum(

        x,

        Fs=Fs,

        Fc=Fc,

        window=window,

        pad_to=pad_to,

        sides=sides,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.annotate)

def annotate(

    text: str,

    xy: tuple[float, float],

    xytext: tuple[float, float] | None = None,

    xycoords: CoordsType = "data",

    textcoords: CoordsType | None = None,

    arrowprops: dict[str, Any] | None = None,

    annotation_clip: bool | None = None,

    **kwargs,

) -> Annotation:

    return gca().annotate(

        text,

        xy,

        xytext=xytext,

        xycoords=xycoords,

        textcoords=textcoords,

        arrowprops=arrowprops,

        annotation_clip=annotation_clip,

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.arrow)

def arrow(x: float, y: float, dx: float, dy: float, **kwargs) -> FancyArrow:

    return gca().arrow(x, y, dx, dy, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.autoscale)

def autoscale(

    enable: bool = True,

    axis: Literal["both", "x", "y"] = "both",

    tight: bool | None = None,

) -> None:

    gca().autoscale(enable=enable, axis=axis, tight=tight)





                                                                        

@_copy_docstring_and_deprecators(Axes.axhline)

def axhline(y: float = 0, xmin: float = 0, xmax: float = 1, **kwargs) -> Line2D:

    return gca().axhline(y=y, xmin=xmin, xmax=xmax, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.axhspan)

def axhspan(

    ymin: float, ymax: float, xmin: float = 0, xmax: float = 1, **kwargs

) -> Rectangle:

    return gca().axhspan(ymin, ymax, xmin=xmin, xmax=xmax, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.axis)

def axis(

    arg: tuple[float, float, float, float] | bool | str | None = None,

    /,

    *,

    emit: bool = True,

    **kwargs,

) -> tuple[float, float, float, float]:

    return gca().axis(arg, emit=emit, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.axline)

def axline(

    xy1: tuple[float, float],

    xy2: tuple[float, float] | None = None,

    *,

    slope: float | None = None,

    **kwargs,

) -> AxLine:

    return gca().axline(xy1, xy2=xy2, slope=slope, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.axvline)

def axvline(x: float = 0, ymin: float = 0, ymax: float = 1, **kwargs) -> Line2D:

    return gca().axvline(x=x, ymin=ymin, ymax=ymax, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.axvspan)

def axvspan(

    xmin: float, xmax: float, ymin: float = 0, ymax: float = 1, **kwargs

) -> Rectangle:

    return gca().axvspan(xmin, xmax, ymin=ymin, ymax=ymax, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.bar)

def bar(

    x: float | ArrayLike,

    height: float | ArrayLike,

    width: float | ArrayLike = 0.8,

    bottom: float | ArrayLike | None = None,

    *,

    align: Literal["center", "edge"] = "center",

    data=None,

    **kwargs,

) -> BarContainer:

    return gca().bar(

        x,

        height,

        width=width,

        bottom=bottom,

        align=align,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.barbs)

def barbs(*args, data=None, **kwargs) -> Barbs:

    return gca().barbs(*args, **({"data": data} if data is not None else {}), **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.barh)

def barh(

    y: float | ArrayLike,

    width: float | ArrayLike,

    height: float | ArrayLike = 0.8,

    left: float | ArrayLike | None = None,

    *,

    align: Literal["center", "edge"] = "center",

    data=None,

    **kwargs,

) -> BarContainer:

    return gca().barh(

        y,

        width,

        height=height,

        left=left,

        align=align,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.bar_label)

def bar_label(

    container: BarContainer,

    labels: ArrayLike | None = None,

    *,

    fmt: str | Callable[[float], str] = "%g",

    label_type: Literal["center", "edge"] = "edge",

    padding: float | ArrayLike = 0,

    **kwargs,

) -> list[Annotation]:

    return gca().bar_label(

        container,

        labels=labels,

        fmt=fmt,

        label_type=label_type,

        padding=padding,

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.boxplot)

def boxplot(

    x: ArrayLike | Sequence[ArrayLike],

    notch: bool | None = None,

    sym: str | None = None,

    vert: bool | None = None,

    orientation: Literal["vertical", "horizontal"] = "vertical",

    whis: float | tuple[float, float] | None = None,

    positions: ArrayLike | None = None,

    widths: float | ArrayLike | None = None,

    patch_artist: bool | None = None,

    bootstrap: int | None = None,

    usermedians: ArrayLike | None = None,

    conf_intervals: ArrayLike | None = None,

    meanline: bool | None = None,

    showmeans: bool | None = None,

    showcaps: bool | None = None,

    showbox: bool | None = None,

    showfliers: bool | None = None,

    boxprops: dict[str, Any] | None = None,

    tick_labels: Sequence[str] | None = None,

    flierprops: dict[str, Any] | None = None,

    medianprops: dict[str, Any] | None = None,

    meanprops: dict[str, Any] | None = None,

    capprops: dict[str, Any] | None = None,

    whiskerprops: dict[str, Any] | None = None,

    manage_ticks: bool = True,

    autorange: bool = False,

    zorder: float | None = None,

    capwidths: float | ArrayLike | None = None,

    label: Sequence[str] | None = None,

    *,

    data=None,

) -> dict[str, Any]:

    return gca().boxplot(

        x,

        notch=notch,

        sym=sym,

        vert=vert,

        orientation=orientation,

        whis=whis,

        positions=positions,

        widths=widths,

        patch_artist=patch_artist,

        bootstrap=bootstrap,

        usermedians=usermedians,

        conf_intervals=conf_intervals,

        meanline=meanline,

        showmeans=showmeans,

        showcaps=showcaps,

        showbox=showbox,

        showfliers=showfliers,

        boxprops=boxprops,

        tick_labels=tick_labels,

        flierprops=flierprops,

        medianprops=medianprops,

        meanprops=meanprops,

        capprops=capprops,

        whiskerprops=whiskerprops,

        manage_ticks=manage_ticks,

        autorange=autorange,

        zorder=zorder,

        capwidths=capwidths,

        label=label,

        **({"data": data} if data is not None else {}),

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.broken_barh)

def broken_barh(

    xranges: Sequence[tuple[float, float]],

    yrange: tuple[float, float],

    align: Literal["bottom", "center", "top"] = "bottom",

    *,

    data=None,

    **kwargs,

) -> PolyCollection:

    return gca().broken_barh(

        xranges,

        yrange,

        align=align,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.clabel)

def clabel(CS: ContourSet, levels: ArrayLike | None = None, **kwargs) -> list[Text]:

    return gca().clabel(CS, levels=levels, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.cohere)

def cohere(

    x: ArrayLike,

    y: ArrayLike,

    NFFT: int = 256,

    Fs: float = 2,

    Fc: int = 0,

    detrend: Literal["none", "mean", "linear"]

    | Callable[[ArrayLike], ArrayLike] = mlab.detrend_none,

    window: Callable[[ArrayLike], ArrayLike] | ArrayLike = mlab.window_hanning,

    noverlap: int = 0,

    pad_to: int | None = None,

    sides: Literal["default", "onesided", "twosided"] = "default",

    scale_by_freq: bool | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray]:

    return gca().cohere(

        x,

        y,

        NFFT=NFFT,

        Fs=Fs,

        Fc=Fc,

        detrend=detrend,

        window=window,

        noverlap=noverlap,

        pad_to=pad_to,

        sides=sides,

        scale_by_freq=scale_by_freq,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.contour)

def contour(*args, data=None, **kwargs) -> QuadContourSet:

    __ret = gca().contour(

        *args, **({"data": data} if data is not None else {}), **kwargs

    )

    if __ret._A is not None:                              

        sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.contourf)

def contourf(*args, data=None, **kwargs) -> QuadContourSet:

    __ret = gca().contourf(

        *args, **({"data": data} if data is not None else {}), **kwargs

    )

    if __ret._A is not None:                              

        sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.csd)

def csd(

    x: ArrayLike,

    y: ArrayLike,

    NFFT: int | None = None,

    Fs: float | None = None,

    Fc: int | None = None,

    detrend: Literal["none", "mean", "linear"]

    | Callable[[ArrayLike], ArrayLike]

    | None = None,

    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,

    noverlap: int | None = None,

    pad_to: int | None = None,

    sides: Literal["default", "onesided", "twosided"] | None = None,

    scale_by_freq: bool | None = None,

    return_line: bool | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, Line2D]:

    return gca().csd(

        x,

        y,

        NFFT=NFFT,

        Fs=Fs,

        Fc=Fc,

        detrend=detrend,

        window=window,

        noverlap=noverlap,

        pad_to=pad_to,

        sides=sides,

        scale_by_freq=scale_by_freq,

        return_line=return_line,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.ecdf)

def ecdf(

    x: ArrayLike,

    weights: ArrayLike | None = None,

    *,

    complementary: bool = False,

    orientation: Literal["vertical", "horizontal"] = "vertical",

    compress: bool = False,

    data=None,

    **kwargs,

) -> Line2D:

    return gca().ecdf(

        x,

        weights=weights,

        complementary=complementary,

        orientation=orientation,

        compress=compress,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.errorbar)

def errorbar(

    x: float | ArrayLike,

    y: float | ArrayLike,

    yerr: float | ArrayLike | None = None,

    xerr: float | ArrayLike | None = None,

    fmt: str = "",

    ecolor: ColorType | None = None,

    elinewidth: float | None = None,

    capsize: float | None = None,

    barsabove: bool = False,

    lolims: bool | ArrayLike = False,

    uplims: bool | ArrayLike = False,

    xlolims: bool | ArrayLike = False,

    xuplims: bool | ArrayLike = False,

    errorevery: int | tuple[int, int] = 1,

    capthick: float | None = None,

    elinestyle: LineStyleType | None = None,

    *,

    data=None,

    **kwargs,

) -> ErrorbarContainer:

    return gca().errorbar(

        x,

        y,

        yerr=yerr,

        xerr=xerr,

        fmt=fmt,

        ecolor=ecolor,

        elinewidth=elinewidth,

        capsize=capsize,

        barsabove=barsabove,

        lolims=lolims,

        uplims=uplims,

        xlolims=xlolims,

        xuplims=xuplims,

        errorevery=errorevery,

        capthick=capthick,

        elinestyle=elinestyle,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.eventplot)

def eventplot(

    positions: ArrayLike | Sequence[ArrayLike],

    orientation: Literal["horizontal", "vertical"] = "horizontal",

    lineoffsets: float | Sequence[float] = 1,

    linelengths: float | Sequence[float] = 1,

    linewidths: float | Sequence[float] | None = None,

    colors: ColorType | Sequence[ColorType] | None = None,

    alpha: float | Sequence[float] | None = None,

    linestyles: LineStyleType | Sequence[LineStyleType] = "solid",

    *,

    data=None,

    **kwargs,

) -> EventCollection:

    return gca().eventplot(

        positions,

        orientation=orientation,

        lineoffsets=lineoffsets,

        linelengths=linelengths,

        linewidths=linewidths,

        colors=colors,

        alpha=alpha,

        linestyles=linestyles,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.fill)

def fill(*args, data=None, **kwargs) -> list[Polygon]:

    return gca().fill(*args, **({"data": data} if data is not None else {}), **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.fill_between)

def fill_between(

    x: ArrayLike,

    y1: ArrayLike | float,

    y2: ArrayLike | float = 0,

    where: Sequence[bool] | None = None,

    interpolate: bool = False,

    step: Literal["pre", "post", "mid"] | None = None,

    *,

    data=None,

    **kwargs,

) -> FillBetweenPolyCollection:

    return gca().fill_between(

        x,

        y1,

        y2=y2,

        where=where,

        interpolate=interpolate,

        step=step,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.fill_betweenx)

def fill_betweenx(

    y: ArrayLike,

    x1: ArrayLike | float,

    x2: ArrayLike | float = 0,

    where: Sequence[bool] | None = None,

    step: Literal["pre", "post", "mid"] | None = None,

    interpolate: bool = False,

    *,

    data=None,

    **kwargs,

) -> FillBetweenPolyCollection:

    return gca().fill_betweenx(

        y,

        x1,

        x2=x2,

        where=where,

        step=step,

        interpolate=interpolate,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.grid)

def grid(

    visible: bool | None = None,

    which: Literal["major", "minor", "both"] = "major",

    axis: Literal["both", "x", "y"] = "both",

    **kwargs,

) -> None:

    gca().grid(visible=visible, which=which, axis=axis, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.grouped_bar)

def grouped_bar(

    heights: Sequence[ArrayLike] | dict[str, ArrayLike] | np.ndarray | pd.DataFrame,

    *,

    positions: ArrayLike | None = None,

    group_spacing: float | None = 1.5,

    bar_spacing: float | None = 0,

    tick_labels: Sequence[str] | None = None,

    labels: Sequence[str] | None = None,

    orientation: Literal["vertical", "horizontal"] = "vertical",

    colors: Iterable[ColorType] | None = None,

    **kwargs,

) -> list[BarContainer]:

    return gca().grouped_bar(

        heights,

        positions=positions,

        group_spacing=group_spacing,

        bar_spacing=bar_spacing,

        tick_labels=tick_labels,

        labels=labels,

        orientation=orientation,

        colors=colors,

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.hexbin)

def hexbin(

    x: ArrayLike,

    y: ArrayLike,

    C: ArrayLike | None = None,

    gridsize: int | tuple[int, int] = 100,

    bins: Literal["log"] | int | Sequence[float] | None = None,

    xscale: Literal["linear", "log"] = "linear",

    yscale: Literal["linear", "log"] = "linear",

    extent: tuple[float, float, float, float] | None = None,

    cmap: str | Colormap | None = None,

    norm: str | Normalize | None = None,

    vmin: float | None = None,

    vmax: float | None = None,

    alpha: float | None = None,

    linewidths: float | None = None,

    edgecolors: Literal["face", "none"] | ColorType = "face",

    reduce_C_function: Callable[[np.ndarray | list[float]], float] = np.mean,

    mincnt: int | None = None,

    marginals: bool = False,

    colorizer: Colorizer | None = None,

    *,

    data=None,

    **kwargs,

) -> PolyCollection:

    __ret = gca().hexbin(

        x,

        y,

        C=C,

        gridsize=gridsize,

        bins=bins,

        xscale=xscale,

        yscale=yscale,

        extent=extent,

        cmap=cmap,

        norm=norm,

        vmin=vmin,

        vmax=vmax,

        alpha=alpha,

        linewidths=linewidths,

        edgecolors=edgecolors,

        reduce_C_function=reduce_C_function,

        mincnt=mincnt,

        marginals=marginals,

        colorizer=colorizer,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )

    sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.hist)

def hist(

    x: ArrayLike | Sequence[ArrayLike],

    bins: int | Sequence[float] | str | None = None,

    range: tuple[float, float] | None = None,

    density: bool = False,

    weights: ArrayLike | None = None,

    cumulative: bool | float = False,

    bottom: ArrayLike | float | None = None,

    histtype: Literal["bar", "barstacked", "step", "stepfilled"] = "bar",

    align: Literal["left", "mid", "right"] = "mid",

    orientation: Literal["vertical", "horizontal"] = "vertical",

    rwidth: float | None = None,

    log: bool = False,

    color: ColorType | Sequence[ColorType] | None = None,

    label: str | Sequence[str] | None = None,

    stacked: bool = False,

    *,

    data=None,

    **kwargs,

) -> tuple[

    np.ndarray | list[np.ndarray],

    np.ndarray,

    BarContainer | Polygon | list[BarContainer | Polygon],

]:

    return gca().hist(

        x,

        bins=bins,

        range=range,

        density=density,

        weights=weights,

        cumulative=cumulative,

        bottom=bottom,

        histtype=histtype,

        align=align,

        orientation=orientation,

        rwidth=rwidth,

        log=log,

        color=color,

        label=label,

        stacked=stacked,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.stairs)

def stairs(

    values: ArrayLike,

    edges: ArrayLike | None = None,

    *,

    orientation: Literal["vertical", "horizontal"] = "vertical",

    baseline: float | ArrayLike | None = 0,

    fill: bool = False,

    data=None,

    **kwargs,

) -> StepPatch:

    return gca().stairs(

        values,

        edges=edges,

        orientation=orientation,

        baseline=baseline,

        fill=fill,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.hist2d)

def hist2d(

    x: ArrayLike,

    y: ArrayLike,

    bins: None | int | tuple[int, int] | ArrayLike | tuple[ArrayLike, ArrayLike] = 10,

    range: ArrayLike | None = None,

    density: bool = False,

    weights: ArrayLike | None = None,

    cmin: float | None = None,

    cmax: float | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray, np.ndarray, QuadMesh]:

    __ret = gca().hist2d(

        x,

        y,

        bins=bins,

        range=range,

        density=density,

        weights=weights,

        cmin=cmin,

        cmax=cmax,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )

    sci(__ret[-1])

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.hlines)

def hlines(

    y: float | ArrayLike,

    xmin: float | ArrayLike,

    xmax: float | ArrayLike,

    colors: ColorType | Sequence[ColorType] | None = None,

    linestyles: LineStyleType = "solid",

    label: str = "",

    *,

    data=None,

    **kwargs,

) -> LineCollection:

    return gca().hlines(

        y,

        xmin,

        xmax,

        colors=colors,

        linestyles=linestyles,

        label=label,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.imshow)

def imshow(

    X: ArrayLike | PIL.Image.Image,

    cmap: str | Colormap | None = None,

    norm: str | Normalize | None = None,

    *,

    aspect: Literal["equal", "auto"] | float | None = None,

    interpolation: str | None = None,

    alpha: float | ArrayLike | None = None,

    vmin: float | None = None,

    vmax: float | None = None,

    colorizer: Colorizer | None = None,

    origin: Literal["upper", "lower"] | None = None,

    extent: tuple[float, float, float, float] | None = None,

    interpolation_stage: Literal["data", "rgba", "auto"] | None = None,

    filternorm: bool = True,

    filterrad: float = 4.0,

    resample: bool | None = None,

    url: str | None = None,

    data=None,

    **kwargs,

) -> AxesImage:

    __ret = gca().imshow(

        X,

        cmap=cmap,

        norm=norm,

        aspect=aspect,

        interpolation=interpolation,

        alpha=alpha,

        vmin=vmin,

        vmax=vmax,

        colorizer=colorizer,

        origin=origin,

        extent=extent,

        interpolation_stage=interpolation_stage,

        filternorm=filternorm,

        filterrad=filterrad,

        resample=resample,

        url=url,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )

    sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.legend)

def legend(*args, **kwargs) -> Legend:

    return gca().legend(*args, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.locator_params)

def locator_params(

    axis: Literal["both", "x", "y"] = "both", tight: bool | None = None, **kwargs

) -> None:

    gca().locator_params(axis=axis, tight=tight, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.loglog)

def loglog(*args, **kwargs) -> list[Line2D]:

    return gca().loglog(*args, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.magnitude_spectrum)

def magnitude_spectrum(

    x: ArrayLike,

    Fs: float | None = None,

    Fc: int | None = None,

    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,

    pad_to: int | None = None,

    sides: Literal["default", "onesided", "twosided"] | None = None,

    scale: Literal["default", "linear", "dB"] | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray, Line2D]:

    return gca().magnitude_spectrum(

        x,

        Fs=Fs,

        Fc=Fc,

        window=window,

        pad_to=pad_to,

        sides=sides,

        scale=scale,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.margins)

def margins(

    *margins: float,

    x: float | None = None,

    y: float | None = None,

    tight: bool | None = True,

) -> tuple[float, float] | None:

    return gca().margins(*margins, x=x, y=y, tight=tight)





                                                                        

@_copy_docstring_and_deprecators(Axes.minorticks_off)

def minorticks_off() -> None:

    gca().minorticks_off()





                                                                        

@_copy_docstring_and_deprecators(Axes.minorticks_on)

def minorticks_on() -> None:

    gca().minorticks_on()





                                                                        

@_copy_docstring_and_deprecators(Axes.pcolor)

def pcolor(

    *args: ArrayLike,

    shading: Literal["flat", "nearest", "auto"] | None = None,

    alpha: float | None = None,

    norm: str | Normalize | None = None,

    cmap: str | Colormap | None = None,

    vmin: float | None = None,

    vmax: float | None = None,

    colorizer: Colorizer | None = None,

    data=None,

    **kwargs,

) -> Collection:

    __ret = gca().pcolor(

        *args,

        shading=shading,

        alpha=alpha,

        norm=norm,

        cmap=cmap,

        vmin=vmin,

        vmax=vmax,

        colorizer=colorizer,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )

    sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.pcolormesh)

def pcolormesh(

    *args: ArrayLike,

    alpha: float | None = None,

    norm: str | Normalize | None = None,

    cmap: str | Colormap | None = None,

    vmin: float | None = None,

    vmax: float | None = None,

    colorizer: Colorizer | None = None,

    shading: Literal["flat", "nearest", "gouraud", "auto"] | None = None,

    antialiased: bool = False,

    data=None,

    **kwargs,

) -> QuadMesh:

    __ret = gca().pcolormesh(

        *args,

        alpha=alpha,

        norm=norm,

        cmap=cmap,

        vmin=vmin,

        vmax=vmax,

        colorizer=colorizer,

        shading=shading,

        antialiased=antialiased,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )

    sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.phase_spectrum)

def phase_spectrum(

    x: ArrayLike,

    Fs: float | None = None,

    Fc: int | None = None,

    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,

    pad_to: int | None = None,

    sides: Literal["default", "onesided", "twosided"] | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray, Line2D]:

    return gca().phase_spectrum(

        x,

        Fs=Fs,

        Fc=Fc,

        window=window,

        pad_to=pad_to,

        sides=sides,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.pie)

def pie(

    x: ArrayLike,

    explode: ArrayLike | None = None,

    labels: Sequence[str] | None = None,

    colors: ColorType | Sequence[ColorType] | None = None,

    autopct: str | Callable[[float], str] | None = None,

    pctdistance: float = 0.6,

    shadow: bool = False,

    labeldistance: float | None = 1.1,

    startangle: float = 0,

    radius: float = 1,

    counterclock: bool = True,

    wedgeprops: dict[str, Any] | None = None,

    textprops: dict[str, Any] | None = None,

    center: tuple[float, float] = (0, 0),

    frame: bool = False,

    rotatelabels: bool = False,

    *,

    normalize: bool = True,

    hatch: str | Sequence[str] | None = None,

    data=None,

) -> tuple[list[Wedge], list[Text]] | tuple[list[Wedge], list[Text], list[Text]]:

    return gca().pie(

        x,

        explode=explode,

        labels=labels,

        colors=colors,

        autopct=autopct,

        pctdistance=pctdistance,

        shadow=shadow,

        labeldistance=labeldistance,

        startangle=startangle,

        radius=radius,

        counterclock=counterclock,

        wedgeprops=wedgeprops,

        textprops=textprops,

        center=center,

        frame=frame,

        rotatelabels=rotatelabels,

        normalize=normalize,

        hatch=hatch,

        **({"data": data} if data is not None else {}),

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.plot)

def plot(

    *args: float | ArrayLike | str,

    scalex: bool = True,

    scaley: bool = True,

    data=None,

    **kwargs,

) -> list[Line2D]:

    return gca().plot(

        *args,

        scalex=scalex,

        scaley=scaley,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.psd)

def psd(

    x: ArrayLike,

    NFFT: int | None = None,

    Fs: float | None = None,

    Fc: int | None = None,

    detrend: Literal["none", "mean", "linear"]

    | Callable[[ArrayLike], ArrayLike]

    | None = None,

    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,

    noverlap: int | None = None,

    pad_to: int | None = None,

    sides: Literal["default", "onesided", "twosided"] | None = None,

    scale_by_freq: bool | None = None,

    return_line: bool | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, Line2D]:

    return gca().psd(

        x,

        NFFT=NFFT,

        Fs=Fs,

        Fc=Fc,

        detrend=detrend,

        window=window,

        noverlap=noverlap,

        pad_to=pad_to,

        sides=sides,

        scale_by_freq=scale_by_freq,

        return_line=return_line,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.quiver)

def quiver(*args, data=None, **kwargs) -> Quiver:

    __ret = gca().quiver(

        *args, **({"data": data} if data is not None else {}), **kwargs

    )

    sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.quiverkey)

def quiverkey(

    Q: Quiver, X: float, Y: float, U: float, label: str, **kwargs

) -> QuiverKey:

    return gca().quiverkey(Q, X, Y, U, label, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.scatter)

def scatter(

    x: float | ArrayLike,

    y: float | ArrayLike,

    s: float | ArrayLike | None = None,

    c: ArrayLike | Sequence[ColorType] | ColorType | None = None,

    marker: MarkerType | None = None,

    cmap: str | Colormap | None = None,

    norm: str | Normalize | None = None,

    vmin: float | None = None,

    vmax: float | None = None,

    alpha: float | None = None,

    linewidths: float | Sequence[float] | None = None,

    *,

    edgecolors: Literal["face", "none"] | ColorType | Sequence[ColorType] | None = None,

    colorizer: Colorizer | None = None,

    plotnonfinite: bool = False,

    data=None,

    **kwargs,

) -> PathCollection:

    __ret = gca().scatter(

        x,

        y,

        s=s,

        c=c,

        marker=marker,

        cmap=cmap,

        norm=norm,

        vmin=vmin,

        vmax=vmax,

        alpha=alpha,

        linewidths=linewidths,

        edgecolors=edgecolors,

        colorizer=colorizer,

        plotnonfinite=plotnonfinite,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )

    sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.semilogx)

def semilogx(*args, **kwargs) -> list[Line2D]:

    return gca().semilogx(*args, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.semilogy)

def semilogy(*args, **kwargs) -> list[Line2D]:

    return gca().semilogy(*args, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.specgram)

def specgram(

    x: ArrayLike,

    NFFT: int | None = None,

    Fs: float | None = None,

    Fc: int | None = None,

    detrend: Literal["none", "mean", "linear"]

    | Callable[[ArrayLike], ArrayLike]

    | None = None,

    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,

    noverlap: int | None = None,

    cmap: str | Colormap | None = None,

    xextent: tuple[float, float] | None = None,

    pad_to: int | None = None,

    sides: Literal["default", "onesided", "twosided"] | None = None,

    scale_by_freq: bool | None = None,

    mode: Literal["default", "psd", "magnitude", "angle", "phase"] | None = None,

    scale: Literal["default", "linear", "dB"] | None = None,

    vmin: float | None = None,

    vmax: float | None = None,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray, np.ndarray, AxesImage]:

    __ret = gca().specgram(

        x,

        NFFT=NFFT,

        Fs=Fs,

        Fc=Fc,

        detrend=detrend,

        window=window,

        noverlap=noverlap,

        cmap=cmap,

        xextent=xextent,

        pad_to=pad_to,

        sides=sides,

        scale_by_freq=scale_by_freq,

        mode=mode,

        scale=scale,

        vmin=vmin,

        vmax=vmax,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )

    sci(__ret[-1])

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.spy)

def spy(

    Z: ArrayLike,

    precision: float | Literal["present"] = 0,

    marker: str | None = None,

    markersize: float | None = None,

    aspect: Literal["equal", "auto"] | float | None = "equal",

    origin: Literal["upper", "lower"] = "upper",

    **kwargs,

) -> AxesImage:

    __ret = gca().spy(

        Z,

        precision=precision,

        marker=marker,

        markersize=markersize,

        aspect=aspect,

        origin=origin,

        **kwargs,

    )

    if isinstance(__ret, _ColorizerInterface):

        sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.stackplot)

def stackplot(

    x, *args, labels=(), colors=None, hatch=None, baseline="zero", data=None, **kwargs

):

    return gca().stackplot(

        x,

        *args,

        labels=labels,

        colors=colors,

        hatch=hatch,

        baseline=baseline,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.stem)

def stem(

    *args: ArrayLike | str,

    linefmt: str | None = None,

    markerfmt: str | None = None,

    basefmt: str | None = None,

    bottom: float = 0,

    label: str | None = None,

    orientation: Literal["vertical", "horizontal"] = "vertical",

    data=None,

) -> StemContainer:

    return gca().stem(

        *args,

        linefmt=linefmt,

        markerfmt=markerfmt,

        basefmt=basefmt,

        bottom=bottom,

        label=label,

        orientation=orientation,

        **({"data": data} if data is not None else {}),

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.step)

def step(

    x: ArrayLike,

    y: ArrayLike,

    *args,

    where: Literal["pre", "post", "mid"] = "pre",

    data=None,

    **kwargs,

) -> list[Line2D]:

    return gca().step(

        x,

        y,

        *args,

        where=where,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.streamplot)

def streamplot(

    x,

    y,

    u,

    v,

    density=1,

    linewidth=None,

    color=None,

    cmap=None,

    norm=None,

    arrowsize=1,

    arrowstyle="-|>",

    minlength=0.1,

    transform=None,

    zorder=None,

    start_points=None,

    maxlength=4.0,

    integration_direction="both",

    broken_streamlines=True,

    *,

    integration_max_step_scale=1.0,

    integration_max_error_scale=1.0,

    num_arrows=1,

    data=None,

):

    __ret = gca().streamplot(

        x,

        y,

        u,

        v,

        density=density,

        linewidth=linewidth,

        color=color,

        cmap=cmap,

        norm=norm,

        arrowsize=arrowsize,

        arrowstyle=arrowstyle,

        minlength=minlength,

        transform=transform,

        zorder=zorder,

        start_points=start_points,

        maxlength=maxlength,

        integration_direction=integration_direction,

        broken_streamlines=broken_streamlines,

        integration_max_step_scale=integration_max_step_scale,

        integration_max_error_scale=integration_max_error_scale,

        num_arrows=num_arrows,

        **({"data": data} if data is not None else {}),

    )

    sci(__ret.lines)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.table)

def table(

    cellText=None,

    cellColours=None,

    cellLoc="right",

    colWidths=None,

    rowLabels=None,

    rowColours=None,

    rowLoc="left",

    colLabels=None,

    colColours=None,

    colLoc="center",

    loc="bottom",

    bbox=None,

    edges="closed",

    **kwargs,

):

    return gca().table(

        cellText=cellText,

        cellColours=cellColours,

        cellLoc=cellLoc,

        colWidths=colWidths,

        rowLabels=rowLabels,

        rowColours=rowColours,

        rowLoc=rowLoc,

        colLabels=colLabels,

        colColours=colColours,

        colLoc=colLoc,

        loc=loc,

        bbox=bbox,

        edges=edges,

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.text)

def text(

    x: float, y: float, s: str, fontdict: dict[str, Any] | None = None, **kwargs

) -> Text:

    return gca().text(x, y, s, fontdict=fontdict, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.tick_params)

def tick_params(axis: Literal["both", "x", "y"] = "both", **kwargs) -> None:

    gca().tick_params(axis=axis, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.ticklabel_format)

def ticklabel_format(

    *,

    axis: Literal["both", "x", "y"] = "both",

    style: Literal["", "sci", "scientific", "plain"] | None = None,

    scilimits: tuple[int, int] | None = None,

    useOffset: bool | float | None = None,

    useLocale: bool | None = None,

    useMathText: bool | None = None,

) -> None:

    gca().ticklabel_format(

        axis=axis,

        style=style,

        scilimits=scilimits,

        useOffset=useOffset,

        useLocale=useLocale,

        useMathText=useMathText,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.tricontour)

def tricontour(*args, **kwargs):

    __ret = gca().tricontour(*args, **kwargs)

    if __ret._A is not None:                              

        sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.tricontourf)

def tricontourf(*args, **kwargs):

    __ret = gca().tricontourf(*args, **kwargs)

    if __ret._A is not None:                              

        sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.tripcolor)

def tripcolor(

    *args,

    alpha=1.0,

    norm=None,

    cmap=None,

    vmin=None,

    vmax=None,

    shading="flat",

    facecolors=None,

    **kwargs,

):

    __ret = gca().tripcolor(

        *args,

        alpha=alpha,

        norm=norm,

        cmap=cmap,

        vmin=vmin,

        vmax=vmax,

        shading=shading,

        facecolors=facecolors,

        **kwargs,

    )

    sci(__ret)

    return __ret





                                                                        

@_copy_docstring_and_deprecators(Axes.triplot)

def triplot(*args, **kwargs):

    return gca().triplot(*args, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.violinplot)

def violinplot(

    dataset: ArrayLike | Sequence[ArrayLike],

    positions: ArrayLike | None = None,

    vert: bool | None = None,

    orientation: Literal["vertical", "horizontal"] = "vertical",

    widths: float | ArrayLike = 0.5,

    showmeans: bool = False,

    showextrema: bool = True,

    showmedians: bool = False,

    quantiles: Sequence[float | Sequence[float]] | None = None,

    points: int = 100,

    bw_method: Literal["scott", "silverman"]

    | float

    | Callable[[GaussianKDE], float]

    | None = None,

    side: Literal["both", "low", "high"] = "both",

    facecolor: Sequence[ColorType] | ColorType | None = None,

    linecolor: Sequence[ColorType] | ColorType | None = None,

    *,

    data=None,

) -> dict[str, Collection]:

    return gca().violinplot(

        dataset,

        positions=positions,

        vert=vert,

        orientation=orientation,

        widths=widths,

        showmeans=showmeans,

        showextrema=showextrema,

        showmedians=showmedians,

        quantiles=quantiles,

        points=points,

        bw_method=bw_method,

        side=side,

        facecolor=facecolor,

        linecolor=linecolor,

        **({"data": data} if data is not None else {}),

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.vlines)

def vlines(

    x: float | ArrayLike,

    ymin: float | ArrayLike,

    ymax: float | ArrayLike,

    colors: ColorType | Sequence[ColorType] | None = None,

    linestyles: LineStyleType = "solid",

    label: str = "",

    *,

    data=None,

    **kwargs,

) -> LineCollection:

    return gca().vlines(

        x,

        ymin,

        ymax,

        colors=colors,

        linestyles=linestyles,

        label=label,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.xcorr)

def xcorr(

    x: ArrayLike,

    y: ArrayLike,

    normed: bool = True,

    detrend: Callable[[ArrayLike], ArrayLike] = mlab.detrend_none,

    usevlines: bool = True,

    maxlags: int = 10,

    *,

    data=None,

    **kwargs,

) -> tuple[np.ndarray, np.ndarray, LineCollection | Line2D, Line2D | None]:

    return gca().xcorr(

        x,

        y,

        normed=normed,

        detrend=detrend,

        usevlines=usevlines,

        maxlags=maxlags,

        **({"data": data} if data is not None else {}),

        **kwargs,

    )





                                                                        

@_copy_docstring_and_deprecators(Axes._sci)

def sci(im: ColorizingArtist) -> None:

    gca()._sci(im)





                                                                        

@_copy_docstring_and_deprecators(Axes.set_title)

def title(

    label: str,

    fontdict: dict[str, Any] | None = None,

    loc: Literal["left", "center", "right"] | None = None,

    pad: float | None = None,

    *,

    y: float | None = None,

    **kwargs,

) -> Text:

    return gca().set_title(label, fontdict=fontdict, loc=loc, pad=pad, y=y, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.set_xlabel)

def xlabel(

    xlabel: str,

    fontdict: dict[str, Any] | None = None,

    labelpad: float | None = None,

    *,

    loc: Literal["left", "center", "right"] | None = None,

    **kwargs,

) -> Text:

    return gca().set_xlabel(

        xlabel, fontdict=fontdict, labelpad=labelpad, loc=loc, **kwargs

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.set_ylabel)

def ylabel(

    ylabel: str,

    fontdict: dict[str, Any] | None = None,

    labelpad: float | None = None,

    *,

    loc: Literal["bottom", "center", "top"] | None = None,

    **kwargs,

) -> Text:

    return gca().set_ylabel(

        ylabel, fontdict=fontdict, labelpad=labelpad, loc=loc, **kwargs

    )





                                                                        

@_copy_docstring_and_deprecators(Axes.set_xscale)

def xscale(value: str | ScaleBase, **kwargs) -> None:

    gca().set_xscale(value, **kwargs)





                                                                        

@_copy_docstring_and_deprecators(Axes.set_yscale)

def yscale(value: str | ScaleBase, **kwargs) -> None:

    gca().set_yscale(value, **kwargs)





                                                                        

def autumn() -> None:

    

    set_cmap("autumn")





                                                                        

def bone() -> None:

    

    set_cmap("bone")





                                                                        

def cool() -> None:

    

    set_cmap("cool")





                                                                        

def copper() -> None:

    

    set_cmap("copper")





                                                                        

def flag() -> None:

    

    set_cmap("flag")





                                                                        

def gray() -> None:

    

    set_cmap("gray")





                                                                        

def hot() -> None:

    

    set_cmap("hot")





                                                                        

def hsv() -> None:

    

    set_cmap("hsv")





                                                                        

def jet() -> None:

    

    set_cmap("jet")





                                                                        

def pink() -> None:

    

    set_cmap("pink")





                                                                        

def prism() -> None:

    

    set_cmap("prism")





                                                                        

def spring() -> None:

    

    set_cmap("spring")





                                                                        

def summer() -> None:

    

    set_cmap("summer")





                                                                        

def winter() -> None:

    

    set_cmap("winter")





                                                                        

def magma() -> None:

    

    set_cmap("magma")





                                                                        

def inferno() -> None:

    

    set_cmap("inferno")





                                                                        

def plasma() -> None:

    

    set_cmap("plasma")





                                                                        

def viridis() -> None:

    

    set_cmap("viridis")





                                                                        

def nipy_spectral() -> None:

    

    set_cmap("nipy_spectral")


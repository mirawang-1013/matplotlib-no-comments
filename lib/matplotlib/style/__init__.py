



import contextlib

import importlib.resources

import logging

import os

from pathlib import Path

import warnings



import matplotlib as mpl

from matplotlib import _api, _docstring, rc_params_from_file, rcParamsDefault



_log = logging.getLogger(__name__)



__all__ = ['use', 'context', 'available', 'library', 'reload_library']





_BASE_LIBRARY_PATH = os.path.join(mpl.get_data_path(), 'stylelib')

                                                                  

USER_LIBRARY_PATHS = [os.path.join(mpl.get_configdir(), 'stylelib')]

_STYLE_EXTENSION = 'mplstyle'

                                                           

_STYLE_BLACKLIST = {

    'interactive', 'backend', 'webagg.port', 'webagg.address',

    'webagg.port_retries', 'webagg.open_in_browser', 'backend_fallback',

    'toolbar', 'timezone', 'figure.max_open_warning',

    'figure.raise_window', 'savefig.directory', 'tk.window_focus',

    'docstring.hardcopy', 'date.epoch'}





@_docstring.Substitution(

    "\n".join(map("- {}".format, sorted(_STYLE_BLACKLIST, key=str.lower)))

)

def use(style):

    

    if isinstance(style, (str, Path)) or hasattr(style, 'keys'):

                                                                               

        styles = [style]

    else:

        styles = style



    style_alias = {'mpl20': 'default', 'mpl15': 'classic'}



    for style in styles:

        if isinstance(style, str):

            style = style_alias.get(style, style)

            if style == "default":

                                                                         

                                                               

                with _api.suppress_matplotlib_deprecation_warning():

                                                                   

                    style = {k: rcParamsDefault[k] for k in rcParamsDefault

                             if k not in _STYLE_BLACKLIST}

            elif style in library:

                style = library[style]

            elif "." in style:

                pkg, _, name = style.rpartition(".")

                try:

                    path = importlib.resources.files(pkg) / f"{name}.{_STYLE_EXTENSION}"

                    style = rc_params_from_file(path, use_default_template=False)

                except (ModuleNotFoundError, OSError, TypeError) as exc:

                                                                             

                                                                              

                                                                             

                                                                          

                                                                               

                                                         

                    pass

        if isinstance(style, (str, Path)):

            try:

                style = rc_params_from_file(style, use_default_template=False)

            except OSError as err:

                raise OSError(

                    f"{style!r} is not a valid package style, path of style "

                    f"file, URL of style file, or library style name (library "

                    f"styles are listed in `style.available`)") from err

        filtered = {}

        for k in style:                                                 

            if k in _STYLE_BLACKLIST:

                _api.warn_external(

                    f"Style includes a parameter, {k!r}, that is not "

                    f"related to style.  Ignoring this parameter.")

            else:

                filtered[k] = style[k]

        mpl.rcParams.update(filtered)





@contextlib.contextmanager

def context(style, after_reset=False):

    

    with mpl.rc_context():

        if after_reset:

            mpl.rcdefaults()

        use(style)

        yield





def _update_user_library(library):

    

    for stylelib_path in map(os.path.expanduser, USER_LIBRARY_PATHS):

        styles = _read_style_directory(stylelib_path)

        _update_nested_dict(library, styles)

    return library





@_api.deprecated("3.11")

def update_user_library(library):

    return _update_user_library(library)





def _read_style_directory(style_dir):

    

    styles = dict()

    for path in Path(style_dir).glob(f"*.{_STYLE_EXTENSION}"):

        with warnings.catch_warnings(record=True) as warns:

            styles[path.stem] = rc_params_from_file(path, use_default_template=False)

        for w in warns:

            _log.warning('In %s: %s', path, w.message)

    return styles





@_api.deprecated("3.11")

def read_style_directory(style_dir):

    return _read_style_directory(style_dir)





def _update_nested_dict(main_dict, new_dict):

    

                                           

    for name, rc_dict in new_dict.items():

        main_dict.setdefault(name, {}).update(rc_dict)

    return main_dict





@_api.deprecated("3.11")

def update_nested_dict(main_dict, new_dict):

    return _update_nested_dict(main_dict, new_dict)





                    

                    

_base_library = _read_style_directory(_BASE_LIBRARY_PATH)

library = {}

available = []





def reload_library():

    

    library.clear()

    library.update(_update_user_library(_base_library.copy()))

    available[:] = sorted(name for name in library if not name.startswith('_'))





reload_library()


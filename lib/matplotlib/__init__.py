



__all__ = [

    "__bibtex__",

    "__version__",

    "__version_info__",

    "set_loglevel",

    "ExecutableNotFoundError",

    "get_configdir",

    "get_cachedir",

    "get_data_path",

    "matplotlib_fname",

    "MatplotlibDeprecationWarning",

    "RcParams",

    "rc_params",

    "rc_params_from_file",

    "rcParamsDefault",

    "rcParams",

    "rcParamsOrig",

    "defaultParams",

    "rc",

    "rcdefaults",

    "rc_file_defaults",

    "rc_file",

    "rc_context",

    "use",

    "get_backend",

    "interactive",

    "is_interactive",

    "colormaps",

    "multivar_colormaps",

    "bivar_colormaps",

    "color_sequences",

]





import atexit

from collections import namedtuple

from collections.abc import MutableMapping

import contextlib

import functools

import importlib

import inspect

from inspect import Parameter

import locale

import logging

import os

from pathlib import Path

import pprint

import re

import shutil

import subprocess

import sys

import tempfile



from packaging.version import parse as parse_version



                                                   

                                                    

from . import _api, _version, cbook, _docstring, rcsetup

from matplotlib._api import MatplotlibDeprecationWarning

from matplotlib.colors import _color_sequences as color_sequences

from matplotlib.rcsetup import cycler              





_log = logging.getLogger(__name__)



__bibtex__ = r"""@Article{Hunter:2007,
  Author    = {Hunter, J. D.},
  Title     = {Matplotlib: A 2D graphics environment},
  Journal   = {Computing in Science \& Engineering},
  Volume    = {9},
  Number    = {3},
  Pages     = {90--95},
  abstract  = {Matplotlib is a 2D graphics package used for Python
  for application development, interactive scripting, and
  publication-quality image generation across user
  interfaces and operating systems.},
  publisher = {IEEE COMPUTER SOC},
  year      = 2007
}"""



                                 

_VersionInfo = namedtuple('_VersionInfo',

                          'major, minor, micro, releaselevel, serial')





def _parse_to_version_info(version_str):

    

    v = parse_version(version_str)

    if v.pre is None and v.post is None and v.dev is None:

        return _VersionInfo(v.major, v.minor, v.micro, 'final', 0)

    elif v.dev is not None:

        return _VersionInfo(v.major, v.minor, v.micro, 'alpha', v.dev)

    elif v.pre is not None:

        releaselevel = {

            'a': 'alpha',

            'b': 'beta',

            'rc': 'candidate'}.get(v.pre[0], 'alpha')

        return _VersionInfo(v.major, v.minor, v.micro, releaselevel, v.pre[1])

    else:

                                                                        

        return _VersionInfo(v.major, v.minor, v.micro + 1, 'alpha', v.post)





def _get_version():

    

                                                                              

                                                                             

                                                                    

    root = Path(__file__).resolve().parents[2]

    if ((root / ".matplotlib-repo").exists()

            and (root / ".git").exists()

            and not (root / ".git/shallow").exists()):

        try:

            import setuptools_scm

        except ImportError:

            pass

        else:

            return setuptools_scm.get_version(

                root=root,

                dist_name="matplotlib",

                version_scheme="release-branch-semver",

                local_scheme="node-and-date",

                fallback_version=_version.version,

            )

                                                                                   

                  

    return _version.version





@_api.caching_module_getattr

class __getattr__:

    __version__ = property(lambda self: _get_version())

    __version_info__ = property(

        lambda self: _parse_to_version_info(self.__version__))





def _check_versions():



                                                             

                                                 

    from . import ft2font              



    for modname, minver in [

            ("cycler", "0.10"),

            ("dateutil", "2.7"),

            ("kiwisolver", "1.3.1"),

            ("numpy", "1.25"),

            ("pyparsing", "2.3.1"),

    ]:

        module = importlib.import_module(modname)

        if parse_version(module.__version__) < parse_version(minver):

            raise ImportError(f"Matplotlib requires {modname}>={minver}; "

                              f"you have {module.__version__}")





_check_versions()





                                                                            

                 

@functools.cache

def _ensure_handler():

    

    handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))

    _log.addHandler(handler)

    return handler





def set_loglevel(level):

    

    _log.setLevel(level.upper())

    _ensure_handler().setLevel(level.upper())





def _logged_cached(fmt, func=None):

    

    if func is None:                                

        return functools.partial(_logged_cached, fmt)



    called = False

    ret = None



    @functools.wraps(func)

    def wrapper(**kwargs):

        nonlocal called, ret

        if not called:

            ret = func(**kwargs)

            called = True

            _log.debug(fmt, ret)

        return ret



    return wrapper





_ExecInfo = namedtuple("_ExecInfo", "executable raw_version version")





class ExecutableNotFoundError(FileNotFoundError):

    

    pass





@functools.cache

def _get_executable_info(name):

    



    def impl(args, regex, min_ver=None, ignore_exit_code=False):

                                                                              

                                                                            

                                                  

                                                                            

                                                                         

        try:

            output = subprocess.check_output(

                args, stderr=subprocess.STDOUT,

                text=True, errors="replace", timeout=30)

        except subprocess.CalledProcessError as _cpe:

            if ignore_exit_code:

                output = _cpe.output

            else:

                raise ExecutableNotFoundError(str(_cpe)) from _cpe

        except subprocess.TimeoutExpired as _te:

            msg = f"Timed out running {cbook._pformat_subprocess(args)}"

            raise ExecutableNotFoundError(msg) from _te

        except OSError as _ose:

            raise ExecutableNotFoundError(str(_ose)) from _ose

        match = re.search(regex, output)

        if match:

            raw_version = match.group(1)

            version = parse_version(raw_version)

            if min_ver is not None and version < parse_version(min_ver):

                raise ExecutableNotFoundError(

                    f"You have {args[0]} version {version} but the minimum "

                    f"version supported by Matplotlib is {min_ver}")

            return _ExecInfo(args[0], raw_version, version)

        else:

            raise ExecutableNotFoundError(

                f"Failed to determine the version of {args[0]} from "

                f"{' '.join(args)}, which output {output}")



    if name in os.environ.get("_MPLHIDEEXECUTABLES", "").split(","):

        raise ExecutableNotFoundError(f"{name} was hidden")



    if name == "dvipng":

        return impl(["dvipng", "-version"], "(?m)^dvipng(?: .*)? (.+)", "1.6")

    elif name == "gs":

        execs = (["gswin32c", "gswin64c", "mgs", "gs"]                     

                 if sys.platform == "win32" else

                 ["gs"])

        for e in execs:

            try:

                return impl([e, "--version"], "(.*)", "9")

            except ExecutableNotFoundError:

                pass

        message = "Failed to find a Ghostscript installation"

        raise ExecutableNotFoundError(message)

    elif name == "inkscape":

        try:

                                                                            

            return impl(["inkscape", "--without-gui", "-V"],

                        "Inkscape ([^ ]*)")

        except ExecutableNotFoundError:

            pass                                

                                                                              

                         

        return impl(["inkscape", "-V"], "Inkscape ([^ ]*)")

    elif name == "magick":

        if sys.platform == "win32":

                                                                              

                                            

            import winreg

            binpath = ""

            for flag in [0, winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY]:

                try:

                    with winreg.OpenKeyEx(

                            winreg.HKEY_LOCAL_MACHINE,

                            r"Software\Imagemagick\Current",

                            0, winreg.KEY_QUERY_VALUE | flag) as hkey:

                        binpath = winreg.QueryValueEx(hkey, "BinPath")[0]

                except OSError:

                    pass

            path = None

            if binpath:

                for name in ["convert.exe", "magick.exe"]:

                    candidate = Path(binpath, name)

                    if candidate.exists():

                        path = str(candidate)

                        break

            if path is None:

                raise ExecutableNotFoundError(

                    "Failed to find an ImageMagick installation")

        else:

            path = "convert"

                                                                   

        info = impl([path, "--version"], r"(?sm:.*^)Version: ImageMagick (\S*)")

        if info.raw_version == "7.0.10-34":

                                                                    

            raise ExecutableNotFoundError(

                f"You have ImageMagick {info.version}, which is unsupported")

        return info

    elif name == "pdftocairo":

        return impl(["pdftocairo", "-v"], "pdftocairo version (.*)")

    elif name == "pdftops":

        info = impl(["pdftops", "-v"], "^pdftops version (.*)",

                    ignore_exit_code=True)

        if info and not (

                3 <= info.version.major or

                                          

                parse_version("0.9") <= info.version < parse_version("1.0")):

            raise ExecutableNotFoundError(

                f"You have pdftops version {info.version} but the minimum "

                f"version supported by Matplotlib is 3.0")

        return info

    else:

        raise ValueError(f"Unknown executable: {name!r}")





def _get_xdg_config_dir():

    

    return os.environ.get('XDG_CONFIG_HOME') or str(Path.home() / ".config")





def _get_xdg_cache_dir():

    

    return os.environ.get('XDG_CACHE_HOME') or str(Path.home() / ".cache")





def _get_config_or_cache_dir(xdg_base_getter):

    configdir = os.environ.get('MPLCONFIGDIR')

    if configdir:

        configdir = Path(configdir)

    elif sys.platform.startswith(('linux', 'freebsd')):

                                                                              

                                        

        try:

            configdir = Path(xdg_base_getter(), "matplotlib")

        except RuntimeError:                                          

            pass

    else:

        try:

            configdir = Path.home() / ".matplotlib"

        except RuntimeError:                                          

            pass



    if configdir:

                                                                                 

        configdir = configdir.resolve()

        try:

            configdir.mkdir(parents=True, exist_ok=True)

        except OSError as exc:

            _log.warning("mkdir -p failed for path %s: %s", configdir, exc)

        else:

            if os.access(str(configdir), os.W_OK) and configdir.is_dir():

                return str(configdir)

            _log.warning("%s is not a writable directory", configdir)

        issue_msg = "the default path ({configdir})"

    else:

        issue_msg = "resolving the home directory"

                                                                             

                                        

    try:

        tmpdir = tempfile.mkdtemp(prefix="matplotlib-")

    except OSError as exc:

        raise OSError(

            f"Matplotlib requires access to a writable cache directory, but there "

            f"was an issue with {issue_msg}, and a temporary "

            f"directory could not be created; set the MPLCONFIGDIR environment "

            f"variable to a writable directory") from exc

    os.environ["MPLCONFIGDIR"] = tmpdir

    atexit.register(shutil.rmtree, tmpdir)

    _log.warning(

        "Matplotlib created a temporary cache directory at %s because there was "

        "an issue with %s; it is highly recommended to set the "

        "MPLCONFIGDIR environment variable to a writable directory, in particular to "

        "speed up the import of Matplotlib and to better support multiprocessing.",

        tmpdir, issue_msg)

    return tmpdir





@_logged_cached('CONFIGDIR=%s')

def get_configdir():

    

    return _get_config_or_cache_dir(_get_xdg_config_dir)





@_logged_cached('CACHEDIR=%s')

def get_cachedir():

    

    return _get_config_or_cache_dir(_get_xdg_cache_dir)





@_logged_cached('matplotlib data path: %s')

def get_data_path():

    

    return str(Path(__file__).with_name("mpl-data"))





def matplotlib_fname():

    



    def gen_candidates():

                                                                      

                                                                   

                                                                    

                       

        yield 'matplotlibrc'

        try:

            matplotlibrc = os.environ['MATPLOTLIBRC']

        except KeyError:

            pass

        else:

            yield matplotlibrc

            yield os.path.join(matplotlibrc, 'matplotlibrc')

        yield os.path.join(get_configdir(), 'matplotlibrc')

        yield os.path.join(get_data_path(), 'matplotlibrc')



    for fname in gen_candidates():

        if os.path.exists(fname) and not os.path.isdir(fname):

            return fname



    raise RuntimeError("Could not find matplotlibrc file; your Matplotlib "

                       "install is broken")





@_docstring.Substitution(

    "\n".join(map("- {}".format, sorted(rcsetup._validators, key=str.lower)))

)

class RcParams(MutableMapping, dict):

    



    validate = rcsetup._validators



                                   

    def __init__(self, *args, **kwargs):

        self.update(*args, **kwargs)



    def _set(self, key, val):

        

        dict.__setitem__(self, key, val)



    def _get(self, key):

        

        return dict.__getitem__(self, key)



    def _update_raw(self, other_params):

        

        if isinstance(other_params, RcParams):

            other_params = dict.items(other_params)

        dict.update(self, other_params)



    def _ensure_has_backend(self):

        

        dict.setdefault(self, "backend", rcsetup._auto_backend_sentinel)



    def __setitem__(self, key, val):

        if (key == "backend"

                and val is rcsetup._auto_backend_sentinel

                and "backend" in self):

            return

        valid_key = _api.check_getitem(

            self.validate, rcParam=key, _error_cls=KeyError

        )

        try:

            cval = valid_key(val)

        except ValueError as ve:

            raise ValueError(f"Key {key}: {ve}") from None

        self._set(key, cval)



    def __getitem__(self, key):

                                                                            

                                                                              

        if key == "backend" and self is globals().get("rcParams"):

            val = self._get(key)

            if val is rcsetup._auto_backend_sentinel:

                from matplotlib import pyplot as plt

                plt.switch_backend(rcsetup._auto_backend_sentinel)

        return self._get(key)



    def _get_backend_or_none(self):

        

        backend = self._get("backend")

        return None if backend is rcsetup._auto_backend_sentinel else backend



    def __repr__(self):

        class_name = self.__class__.__name__

        indent = len(class_name) + 1

        with _api.suppress_matplotlib_deprecation_warning():

            repr_split = pprint.pformat(dict(self), indent=1,

                                        width=80 - indent).split('\n')

        repr_indented = ('\n' + ' ' * indent).join(repr_split)

        return f'{class_name}({repr_indented})'



    def __str__(self):

        return '\n'.join(map('{0[0]}: {0[1]}'.format, sorted(self.items())))



    def __iter__(self):

        

                                                                        

                                                

        with _api.suppress_matplotlib_deprecation_warning():

            yield from sorted(dict.__iter__(self))



    def __len__(self):

        return dict.__len__(self)



    def find_all(self, pattern):

        

        pattern_re = re.compile(pattern)

        return self.__class__(

            (key, value) for key, value in self.items() if pattern_re.search(key)

        )



    def copy(self):

        

        rccopy = self.__class__()

        for k in self:                                       

            rccopy._set(k, self._get(k))

        return rccopy





def rc_params(fail_on_error=False):

    

    return rc_params_from_file(matplotlib_fname(), fail_on_error)





@functools.cache

def _get_ssl_context():

    try:

        import certifi

    except ImportError:

        _log.debug("Could not import certifi.")

        return None

    import ssl

    return ssl.create_default_context(cafile=certifi.where())





@contextlib.contextmanager

def _open_file_or_url(fname):

    if (isinstance(fname, str)

            and fname.startswith(('http://', 'https://', 'ftp://', 'file:'))):

        import urllib.request

        ssl_ctx = _get_ssl_context()

        if ssl_ctx is None:

            _log.debug(

                "Could not get certifi ssl context, https may not work."

            )

        with urllib.request.urlopen(fname, context=ssl_ctx) as f:

            yield (line.decode('utf-8') for line in f)

    else:

        fname = os.path.expanduser(fname)

        with open(fname, encoding='utf-8') as f:

            yield f





def _rc_params_in_file(fname, transform=lambda x: x, fail_on_error=False):

    

    import matplotlib as mpl

    rc_temp = {}

    with _open_file_or_url(fname) as fd:

        try:

            for line_no, line in enumerate(fd, 1):

                line = transform(line)

                strippedline = cbook._strip_comment(line)

                if not strippedline:

                    continue

                tup = strippedline.split(':', 1)

                if len(tup) != 2:

                    _log.warning('Missing colon in file %r, line %d (%r)',

                                 fname, line_no, line.rstrip('\n'))

                    continue

                key, val = tup

                key = key.strip()

                val = val.strip()

                if val.startswith('"') and val.endswith('"'):

                    val = val[1:-1]                       

                if key in rc_temp:

                    _log.warning('Duplicate key in file %r, line %d (%r)',

                                 fname, line_no, line.rstrip('\n'))

                rc_temp[key] = (val, line, line_no)

        except UnicodeDecodeError:

            _log.warning('Cannot decode configuration file %r as utf-8.',

                         fname)

            raise



    config = RcParams()



    for key, (val, line, line_no) in rc_temp.items():

        if key in rcsetup._validators:

            if fail_on_error:

                config[key] = val                                          

            else:

                try:

                    config[key] = val                                         

                except Exception as msg:

                    _log.warning('Bad value in file %r, line %d (%r): %s',

                                 fname, line_no, line.rstrip('\n'), msg)

        else:

                                                                          

                                       

            version = ('main' if '.post' in mpl.__version__

                       else f'v{mpl.__version__}')

            _log.warning("""
Bad key %(key)s in file %(fname)s, line %(line_no)s (%(line)r)
You probably need to get an updated matplotlibrc file from
https://github.com/matplotlib/matplotlib/blob/%(version)s/lib/matplotlib/mpl-data/matplotlibrc
or from the matplotlib source distribution""",

                         dict(key=key, fname=fname, line_no=line_no,

                              line=line.rstrip('\n'), version=version))

    return config





def rc_params_from_file(fname, fail_on_error=False, use_default_template=True):

    

    config_from_file = _rc_params_in_file(fname, fail_on_error=fail_on_error)



    if not use_default_template:

        return config_from_file



    with _api.suppress_matplotlib_deprecation_warning():

        config = RcParams({**rcParamsDefault, **config_from_file})



    if "".join(config['text.latex.preamble']):

        _log.info("""
*****************************************************************
You have the following UNSUPPORTED LaTeX preamble customizations:
%s
Please do not ask for support with these customizations active.
*****************************************************************
""", '\n'.join(config['text.latex.preamble']))

    _log.debug('loaded rc file %s', fname)



    return config





rcParamsDefault = _rc_params_in_file(

    cbook._get_data_path("matplotlibrc"),

                            

    transform=lambda line: line[1:] if line.startswith("#") else line,

    fail_on_error=True)

rcParamsDefault._update_raw(rcsetup._hardcoded_defaults)

rcParamsDefault._ensure_has_backend()



rcParams = RcParams()                        

rcParams._update_raw(rcParamsDefault)

rcParams._update_raw(_rc_params_in_file(matplotlib_fname()))

rcParamsOrig = rcParams.copy()

with _api.suppress_matplotlib_deprecation_warning():

                                                                           

                                                                     

    defaultParams = rcsetup.defaultParams = {

                                                                    

        key: [(rcsetup._auto_backend_sentinel if key == "backend" else

               rcParamsDefault[key]),

              validator]

        for key, validator in rcsetup._validators.items()}

if rcParams['axes.formatter.use_locale']:

    locale.setlocale(locale.LC_ALL, '')





def rc(group, **kwargs):

    



    aliases = {

        'lw':  'linewidth',

        'ls':  'linestyle',

        'c':   'color',

        'fc':  'facecolor',

        'ec':  'edgecolor',

        'mew': 'markeredgewidth',

        'aa':  'antialiased',

        'sans': 'sans-serif',

        }



    if isinstance(group, str):

        group = (group,)

    for g in group:

        for k, v in kwargs.items():

            name = aliases.get(k) or k

            key = f'{g}.{name}'

            try:

                rcParams[key] = v

            except KeyError as err:

                raise KeyError(('Unrecognized key "%s" for group "%s" and '

                                'name "%s"') % (key, g, name)) from err





def rcdefaults():

    

                                                                              

                                  

    with _api.suppress_matplotlib_deprecation_warning():

        from .style.core import STYLE_BLACKLIST

        rcParams.clear()

        rcParams.update({k: v for k, v in rcParamsDefault.items()

                         if k not in STYLE_BLACKLIST})





def rc_file_defaults():

    

                                                                              

                               

    with _api.suppress_matplotlib_deprecation_warning():

        from .style.core import STYLE_BLACKLIST

        rcParams.update({k: rcParamsOrig[k] for k in rcParamsOrig

                         if k not in STYLE_BLACKLIST})





def rc_file(fname, *, use_default_template=True):

    

                                                                               

                          

    with _api.suppress_matplotlib_deprecation_warning():

        from .style.core import STYLE_BLACKLIST

        rc_from_file = rc_params_from_file(

            fname, use_default_template=use_default_template)

        rcParams.update({k: rc_from_file[k] for k in rc_from_file

                         if k not in STYLE_BLACKLIST})





@contextlib.contextmanager

def rc_context(rc=None, fname=None):

    

    orig = dict(rcParams.copy())

    del orig['backend']

    try:

        if fname:

            rc_file(fname)

        if rc:

            rcParams.update(rc)

        yield

    finally:

        rcParams._update_raw(orig)                               





def use(backend, *, force=True):

    

    name = rcsetup.validate_backend(backend)

                                                            

    if rcParams._get_backend_or_none() == name:

                                                               

        pass

    else:

                                                                     

                                                                        

                                                                             

        plt = sys.modules.get('matplotlib.pyplot')

                                                            

        if plt is not None:

            try:

                                                                   

                                                                   

                                           

                plt.switch_backend(name)

            except ImportError:

                if force:

                    raise

                                                                     

                                                                     

                

        else:

            rcParams['backend'] = backend

                                                                 

              

    rcParams['backend_fallback'] = False





if os.environ.get('MPLBACKEND'):

    rcParams['backend'] = os.environ.get('MPLBACKEND')





def get_backend(*, auto_select=True):

    

    if auto_select:

        return rcParams['backend']

    else:

        backend = rcParams._get('backend')

        if backend is rcsetup._auto_backend_sentinel:

            return None

        else:

            return backend





def interactive(b):

    

    rcParams['interactive'] = b





def is_interactive():

    

    return rcParams['interactive']





def _val_or_rc(val, *rc_names):

    

    if val is not None:

        return val



    for rc_name in rc_names[:-1]:

        if rcParams[rc_name] is not None:

            return rcParams[rc_name]

    return rcParams[rc_names[-1]]





def _init_tests():

                                                                                       

                                 

    LOCAL_FREETYPE_VERSION = '2.6.1'



    from matplotlib import ft2font

    if (ft2font.__freetype_version__ != LOCAL_FREETYPE_VERSION or

            ft2font.__freetype_build_type__ != 'local'):

        _log.warning(

            "Matplotlib is not built with the correct FreeType version to run tests.  "

            "Rebuild without setting system-freetype=true in Meson setup options.  "

            "Expect many image comparison failures below.  "

            "Expected freetype version %s.  "

            "Found freetype version %s.  "

            "Freetype build type is %slocal.",

            LOCAL_FREETYPE_VERSION,

            ft2font.__freetype_version__,

            "" if ft2font.__freetype_build_type__ == 'local' else "not ")





def _replacer(data, value):

    

    try:

                                            

        if isinstance(value, str):

                                    

            value = data[value]

    except Exception:

                                                       

        pass

    return cbook.sanitize_sequence(value)





def _label_from_arg(y, default_name):

    try:

        return y.name

    except AttributeError:

        if isinstance(default_name, str):

            return default_name

    return None





def _add_data_doc(docstring, replace_names):

    

    if (docstring is None

            or replace_names is not None and len(replace_names) == 0):

        return docstring

    docstring = inspect.cleandoc(docstring)



    data_doc = ("""\
    If given, all parameters also accept a string ``s``, which is
    interpreted as ``data[s]`` if ``s`` is a key in ``data``."""

                if replace_names is None else f"""\
    If given, the following parameters also accept a string ``s``, which is
    interpreted as ``data[s]`` if ``s`` is a key in ``data``:

    {', '.join(map('*{}*'.format, replace_names))}""")

                                                                       

                                

                                                                              

    if _log.level <= logging.DEBUG:

                                                                            

                                                    

        if "data : indexable object, optional" not in docstring:

            _log.debug("data parameter docstring error: no data parameter")

        if 'DATA_PARAMETER_PLACEHOLDER' not in docstring:

            _log.debug("data parameter docstring error: missing placeholder")

    return docstring.replace('    DATA_PARAMETER_PLACEHOLDER', data_doc)





def _preprocess_data(func=None, *, replace_names=None, label_namer=None):

    



    if func is None:                                

        return functools.partial(

            _preprocess_data,

            replace_names=replace_names, label_namer=label_namer)



    sig = inspect.signature(func)

    varargs_name = None

    varkwargs_name = None

    arg_names = []

    params = list(sig.parameters.values())

    for p in params:

        if p.kind is Parameter.VAR_POSITIONAL:

            varargs_name = p.name

        elif p.kind is Parameter.VAR_KEYWORD:

            varkwargs_name = p.name

        else:

            arg_names.append(p.name)

    data_param = Parameter("data", Parameter.KEYWORD_ONLY, default=None)

    if varkwargs_name:

        params.insert(-1, data_param)

    else:

        params.append(data_param)

    new_sig = sig.replace(parameters=params)

    arg_names = arg_names[1:]                                    



    assert {*arg_names}.issuperset(replace_names or []) or varkwargs_name, (

        "Matplotlib internal error: invalid replace_names "

        f"({replace_names!r}) for {func.__name__!r}")

    assert label_namer is None or label_namer in arg_names, (

        "Matplotlib internal error: invalid label_namer "

        f"({label_namer!r}) for {func.__name__!r}")



    @functools.wraps(func)

    def inner(ax, *args, data=None, **kwargs):

        if data is None:

            return func(

                ax,

                *map(cbook.sanitize_sequence, args),

                **{k: cbook.sanitize_sequence(v) for k, v in kwargs.items()})



        bound = new_sig.bind(ax, *args, **kwargs)

        auto_label = (bound.arguments.get(label_namer)

                      or bound.kwargs.get(label_namer))



        for k, v in bound.arguments.items():

            if k == varkwargs_name:

                for k1, v1 in v.items():

                    if replace_names is None or k1 in replace_names:

                        v[k1] = _replacer(data, v1)

            elif k == varargs_name:

                if replace_names is None:

                    bound.arguments[k] = tuple(_replacer(data, v1) for v1 in v)

            else:

                if replace_names is None or k in replace_names:

                    bound.arguments[k] = _replacer(data, v)



        new_args = bound.args

        new_kwargs = bound.kwargs



        args_and_kwargs = {**bound.arguments, **bound.kwargs}

        if label_namer and "label" not in args_and_kwargs:

            new_kwargs["label"] = _label_from_arg(

                args_and_kwargs.get(label_namer), auto_label)



        return func(*new_args, **new_kwargs)



    inner.__doc__ = _add_data_doc(inner.__doc__, replace_names)

    inner.__signature__ = new_sig

    return inner





_log.debug('interactive is %s', is_interactive())

_log.debug('platform is %s', sys.platform)





@_api.deprecated("3.10", alternative="matplotlib.cbook.sanitize_sequence")

def sanitize_sequence(data):

    return cbook.sanitize_sequence(data)





@_api.deprecated("3.10", alternative="matplotlib.rcsetup.validate_backend")

def validate_backend(s):

    return rcsetup.validate_backend(s)





                                                                               

                                       

from matplotlib.cm import _colormaps as colormaps              

from matplotlib.cm import _multivar_colormaps as multivar_colormaps              

from matplotlib.cm import _bivar_colormaps as bivar_colormaps              


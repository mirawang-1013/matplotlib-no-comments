



import collections

import collections.abc

import contextlib

import functools

import gzip

import itertools

import math

import operator

import os

from pathlib import Path

import shlex

import subprocess

import sys

import time

import traceback

import types

import weakref



import numpy as np



try:

    from numpy.exceptions import VisibleDeprecationWarning                 

except ImportError:

    from numpy import VisibleDeprecationWarning



import matplotlib

from matplotlib import _api, _c_internal_utils





class _ExceptionInfo:

    



    def __init__(self, cls, *args):

        self._cls = cls

        self._args = args



    @classmethod

    def from_exception(cls, exc):

        return cls(type(exc), *exc.args)



    def to_exception(self):

        return self._cls(*self._args)





def _get_running_interactive_framework():

    

                                                                          

                                                        

    QtWidgets = (

        sys.modules.get("PyQt6.QtWidgets")

        or sys.modules.get("PySide6.QtWidgets")

        or sys.modules.get("PyQt5.QtWidgets")

        or sys.modules.get("PySide2.QtWidgets")

    )

    if QtWidgets and QtWidgets.QApplication.instance():

        return "qt"

    Gtk = sys.modules.get("gi.repository.Gtk")

    if Gtk:

        if Gtk.MAJOR_VERSION == 4:

            from gi.repository import GLib

            if GLib.main_depth():

                return "gtk4"

        if Gtk.MAJOR_VERSION == 3 and Gtk.main_level():

            return "gtk3"

    wx = sys.modules.get("wx")

    if wx and wx.GetApp():

        return "wx"

    tkinter = sys.modules.get("tkinter")

    if tkinter:

        codes = {tkinter.mainloop.__code__, tkinter.Misc.mainloop.__code__}

        for frame in sys._current_frames().values():

            while frame:

                if frame.f_code in codes:

                    return "tk"

                frame = frame.f_back

                                                                          

        del frame

    macosx = sys.modules.get("matplotlib.backends._macosx")

    if macosx and macosx.event_loop_is_running():

        return "macosx"

    if not _c_internal_utils.display_is_valid():

        return "headless"

    return None





def _exception_printer(exc):

    if _get_running_interactive_framework() in ["headless", None]:

        raise exc

    else:

        traceback.print_exc()





class _StrongRef:

    



    def __init__(self, obj):

        self._obj = obj



    def __call__(self):

        return self._obj



    def __eq__(self, other):

        return isinstance(other, _StrongRef) and self._obj == other._obj



    def __hash__(self):

        return hash(self._obj)





def _weak_or_strong_ref(func, callback):

    

    try:

        return weakref.WeakMethod(func, callback)

    except TypeError:

        return _StrongRef(func)





class _UnhashDict:

    



    def __init__(self, pairs):

        self._dict = {}

        self._pairs = []

        for k, v in pairs:

            self[k] = v



    def __setitem__(self, key, value):

        try:

            self._dict[key] = value

        except TypeError:

            for i, (k, v) in enumerate(self._pairs):

                if k == key:

                    self._pairs[i] = (key, value)

                    break

            else:

                self._pairs.append((key, value))



    def __getitem__(self, key):

        try:

            return self._dict[key]

        except TypeError:

            pass

        for k, v in self._pairs:

            if k == key:

                return v

        raise KeyError(key)



    def pop(self, key, *args):

        try:

            if key in self._dict:

                return self._dict.pop(key)

        except TypeError:

            for i, (k, v) in enumerate(self._pairs):

                if k == key:

                    del self._pairs[i]

                    return v

        if args:

            return args[0]

        raise KeyError(key)



    def __iter__(self):

        yield from self._dict

        for k, v in self._pairs:

            yield k





class CallbackRegistry:

    



                               

                                                         

                                                             



    def __init__(self, exception_handler=_exception_printer, *, signals=None):

        self._signals = None if signals is None else list(signals)            

        self.exception_handler = exception_handler

        self.callbacks = {}

        self._cid_gen = itertools.count()

        self._func_cid_map = _UnhashDict([])

                                                                    

        self._pickled_cids = set()



    def __getstate__(self):

        return {

            **vars(self),

                                                                             

                                                              

            "callbacks": {s: {cid: proxy() for cid, proxy in d.items()

                              if cid in self._pickled_cids}

                          for s, d in self.callbacks.items()},

                                                                               

            "_func_cid_map": None,

            "_cid_gen": next(self._cid_gen)

        }



    def __setstate__(self, state):

        cid_count = state.pop('_cid_gen')

        vars(self).update(state)

        self.callbacks = {

            s: {cid: _weak_or_strong_ref(func, functools.partial(self._remove_proxy, s))

                for cid, func in d.items()}

            for s, d in self.callbacks.items()}

        self._func_cid_map = _UnhashDict(

            ((s, proxy), cid)

            for s, d in self.callbacks.items() for cid, proxy in d.items())

        self._cid_gen = itertools.count(cid_count)



    def connect(self, signal, func):

        

        if self._signals is not None:

            _api.check_in_list(self._signals, signal=signal)

        proxy = _weak_or_strong_ref(func, functools.partial(self._remove_proxy, signal))

        try:

            return self._func_cid_map[signal, proxy]

        except KeyError:

            cid = self._func_cid_map[signal, proxy] = next(self._cid_gen)

            self.callbacks.setdefault(signal, {})[cid] = proxy

            return cid



    def _connect_picklable(self, signal, func):

        

        cid = self.connect(signal, func)

        self._pickled_cids.add(cid)

        return cid



                                                                             

                    

    def _remove_proxy(self, signal, proxy, *, _is_finalizing=sys.is_finalizing):

        if _is_finalizing():

                                                                         

            return

        cid = self._func_cid_map.pop((signal, proxy), None)

        if cid is not None:

            del self.callbacks[signal][cid]

            self._pickled_cids.discard(cid)

        else:             

            return

        if len(self.callbacks[signal]) == 0:                        

            del self.callbacks[signal]



    def disconnect(self, cid):

        

        self._pickled_cids.discard(cid)

        for signal, proxy in self._func_cid_map:

            if self._func_cid_map[signal, proxy] == cid:

                break

        else:             

            return

        assert self.callbacks[signal][cid] == proxy

        del self.callbacks[signal][cid]

        self._func_cid_map.pop((signal, proxy))

        if len(self.callbacks[signal]) == 0:                        

            del self.callbacks[signal]



    def process(self, s, *args, **kwargs):

        

        if self._signals is not None:

            _api.check_in_list(self._signals, signal=s)

        for ref in list(self.callbacks.get(s, {}).values()):

            func = ref()

            if func is not None:

                try:

                    func(*args, **kwargs)

                                                                      

                                   

                except Exception as exc:

                    if self.exception_handler is not None:

                        self.exception_handler(exc)

                    else:

                        raise



    @contextlib.contextmanager

    def blocked(self, *, signal=None):

        

        orig = self.callbacks

        try:

            if signal is None:

                                         

                self.callbacks = {}

            else:

                                                 

                self.callbacks = {k: orig[k] for k in orig if k != signal}

            yield

        finally:

            self.callbacks = orig





class silent_list(list):

    



    def __init__(self, type, seq=None):

        self.type = type

        if seq is not None:

            self.extend(seq)



    def __repr__(self):

        if self.type is not None or len(self) != 0:

            tp = self.type if self.type is not None else type(self[0]).__name__

            return f"<a list of {len(self)} {tp} objects>"

        else:

            return "<an empty list>"





def _local_over_kwdict(

        local_var, kwargs, *keys,

        warning_cls=_api.MatplotlibDeprecationWarning):

    out = local_var

    for key in keys:

        kwarg_val = kwargs.pop(key, None)

        if kwarg_val is not None:

            if out is None:

                out = kwarg_val

            else:

                _api.warn_external(f'"{key}" keyword argument will be ignored',

                                   warning_cls)

    return out





def strip_math(s):

    

    if len(s) >= 2 and s[0] == s[-1] == "$":

        s = s[1:-1]

        for tex, plain in [

                (r"\times", "x"),                                       

                (r"\mathdefault", ""),

                (r"\rm", ""),

                (r"\cal", ""),

                (r"\tt", ""),

                (r"\it", ""),

                ("\\", ""),

                ("{", ""),

                ("}", ""),

        ]:

            s = s.replace(tex, plain)

    return s





def _strip_comment(s):

    

    pos = 0

    while True:

        quote_pos = s.find('"', pos)

        hash_pos = s.find('#', pos)

        if quote_pos < 0:

            without_comment = s if hash_pos < 0 else s[:hash_pos]

            return without_comment.strip()

        elif 0 <= hash_pos < quote_pos:

            return s[:hash_pos].strip()

        else:

            closing_quote_pos = s.find('"', quote_pos + 1)

            if closing_quote_pos < 0:

                raise ValueError(

                    f"Missing closing quote in: {s!r}. If you need a double-"

                    'quote inside a string, use escaping: e.g. "the \" char"')

            pos = closing_quote_pos + 1                        





def is_writable_file_like(obj):

    

    return callable(getattr(obj, 'write', None))





def file_requires_unicode(x):

    

    try:

        x.write(b'')

    except TypeError:

        return True

    else:

        return False





def to_filehandle(fname, flag='r', return_opened=False, encoding=None):

    

    if isinstance(fname, os.PathLike):

        fname = os.fspath(fname)

    if isinstance(fname, str):

        if fname.endswith('.gz'):

            fh = gzip.open(fname, flag)

        elif fname.endswith('.bz2'):

                                                          

                                          

            import bz2

            fh = bz2.BZ2File(fname, flag)

        else:

            fh = open(fname, flag, encoding=encoding)

        opened = True

    elif hasattr(fname, 'seek'):

        fh = fname

        opened = False

    else:

        raise ValueError('fname must be a PathLike or file handle')

    if return_opened:

        return fh, opened

    return fh





def open_file_cm(path_or_file, mode="r", encoding=None):

    

    fh, opened = to_filehandle(path_or_file, mode, True, encoding)

    return fh if opened else contextlib.nullcontext(fh)





def is_scalar_or_string(val):

    

    return isinstance(val, str) or not np.iterable(val)





def get_sample_data(fname, asfileobj=True):

    

    path = _get_data_path('sample_data', fname)

    if asfileobj:

        suffix = path.suffix.lower()

        if suffix == '.gz':

            return gzip.open(path)

        elif suffix in ['.npy', '.npz']:

            return np.load(path)

        elif suffix in ['.csv', '.xrc', '.txt']:

            return path.open('r')

        else:

            return path.open('rb')

    else:

        return str(path)





def _get_data_path(*args):

    

    return Path(matplotlib.get_data_path(), *args)





def flatten(seq, scalarp=is_scalar_or_string):

                  

    for item in seq:

        if scalarp(item) or item is None:

            yield item

        else:

            yield from flatten(item, scalarp)





class _Stack:

    



    def __init__(self):

        self._pos = -1

        self._elements = []



    def clear(self):

        

        self._pos = -1

        self._elements = []



    def __call__(self):

        

        return self._elements[self._pos] if self._elements else None



    def __len__(self):

        return len(self._elements)



    def __getitem__(self, ind):

        return self._elements[ind]



    def forward(self):

        

        self._pos = min(self._pos + 1, len(self._elements) - 1)

        return self()



    def back(self):

        

        self._pos = max(self._pos - 1, 0)

        return self()



    def push(self, o):

        

        self._elements[self._pos + 1:] = [o]

        self._pos = len(self._elements) - 1

        return o



    def home(self):

        

        return self.push(self._elements[0]) if self._elements else None





def safe_masked_invalid(x, copy=False):

    x = np.array(x, subok=True, copy=copy)

    if not x.dtype.isnative:

                                                                               

                                           

                               

        x = x.byteswap(inplace=copy).view(x.dtype.newbyteorder('N'))

    try:

        xm = np.ma.masked_where(~(np.isfinite(x)), x, copy=False)

    except TypeError:

        return x

    return xm





def print_cycles(objects, outstream=sys.stdout, show_progress=False):

    

    import gc



    def print_path(path):

        for i, step in enumerate(path):

                                 

            next = path[(i + 1) % len(path)]



            outstream.write("   %s -- " % type(step))

            if isinstance(step, dict):

                for key, val in step.items():

                    if val is next:

                        outstream.write(f"[{key!r}]")

                        break

                    if key is next:

                        outstream.write(f"[key] = {val!r}")

                        break

            elif isinstance(step, list):

                outstream.write("[%d]" % step.index(next))

            elif isinstance(step, tuple):

                outstream.write("( tuple )")

            else:

                outstream.write(repr(step))

            outstream.write(" ->\n")

        outstream.write("\n")



    def recurse(obj, start, all, current_path):

        if show_progress:

            outstream.write("%d\r" % len(all))



        all[id(obj)] = None



        referents = gc.get_referents(obj)

        for referent in referents:

                                                               

                                      

            if referent is start:

                print_path(current_path)



                                                                    

                                                                     

                                                                

            elif referent is objects or isinstance(referent, types.FrameType):

                continue



                                                            

            elif id(referent) not in all:

                recurse(referent, start, all, current_path + [obj])



    for obj in objects:

        outstream.write(f"Examining: {obj!r}\n")

        recurse(obj, obj, {}, [])





class Grouper:

    



    def __init__(self, init=()):

        self._mapping = weakref.WeakKeyDictionary(

            {x: weakref.WeakSet([x]) for x in init})

        self._ordering = weakref.WeakKeyDictionary()

        for x in init:

            if x not in self._ordering:

                self._ordering[x] = len(self._ordering)

        self._next_order = len(self._ordering)                                   



    def __getstate__(self):

        return {

            **vars(self),

                                               

            "_mapping": {k: set(v) for k, v in self._mapping.items()},

            "_ordering": {**self._ordering},

        }



    def __setstate__(self, state):

        vars(self).update(state)

                                           

        self._mapping = weakref.WeakKeyDictionary(

            {k: weakref.WeakSet(v) for k, v in self._mapping.items()})

        self._ordering = weakref.WeakKeyDictionary(self._ordering)



    def __contains__(self, item):

        return item in self._mapping



    def join(self, a, *args):

        

        mapping = self._mapping

        try:

            set_a = mapping[a]

        except KeyError:

            set_a = mapping[a] = weakref.WeakSet([a])

            self._ordering[a] = self._next_order

            self._next_order += 1

        for arg in args:

            try:

                set_b = mapping[arg]

            except KeyError:

                set_b = mapping[arg] = weakref.WeakSet([arg])

                self._ordering[arg] = self._next_order

                self._next_order += 1

            if set_b is not set_a:

                if len(set_b) > len(set_a):

                    set_a, set_b = set_b, set_a

                set_a.update(set_b)

                for elem in set_b:

                    mapping[elem] = set_a



    def joined(self, a, b):

        

        return (self._mapping.get(a, object()) is self._mapping.get(b))



    def remove(self, a):

        

        self._mapping.pop(a, {a}).remove(a)

        self._ordering.pop(a, None)



    def __iter__(self):

        

        unique_groups = {id(group): group for group in self._mapping.values()}

        for group in unique_groups.values():

            yield sorted(group, key=self._ordering.__getitem__)



    def get_siblings(self, a):

        

        siblings = self._mapping.get(a, [a])

        return sorted(siblings, key=self._ordering.get)





class GrouperView:

    



    def __init__(self, grouper): self._grouper = grouper

    def __contains__(self, item): return item in self._grouper

    def __iter__(self): return iter(self._grouper)



    def joined(self, a, b):

        

        return self._grouper.joined(a, b)



    def get_siblings(self, a):

        

        return self._grouper.get_siblings(a)





def simple_linear_interpolation(a, steps):

    

    fps = a.reshape((len(a), -1))

    xp = np.arange(len(a)) * steps

    x = np.arange((len(a) - 1) * steps + 1)

    return (np.column_stack([np.interp(x, xp, fp) for fp in fps.T])

            .reshape((len(x),) + a.shape[1:]))





def delete_masked_points(*args):

    

    if not len(args):

        return ()

    if is_scalar_or_string(args[0]):

        raise ValueError("First argument must be a sequence")

    nrecs = len(args[0])

    margs = []

    seqlist = [False] * len(args)

    for i, x in enumerate(args):

        if not isinstance(x, str) and np.iterable(x) and len(x) == nrecs:

            seqlist[i] = True

            if isinstance(x, np.ma.MaskedArray):

                if x.ndim > 1:

                    raise ValueError("Masked arrays must be 1-D")

            else:

                x = np.asarray(x)

        margs.append(x)

    masks = []                                           

    for i, x in enumerate(margs):

        if seqlist[i]:

            if x.ndim > 1:

                continue                                              

            if isinstance(x, np.ma.MaskedArray):

                masks.append(~np.ma.getmaskarray(x))                   

                xd = x.data

            else:

                xd = x

            try:

                mask = np.isfinite(xd)

                if isinstance(mask, np.ndarray):

                    masks.append(mask)

            except Exception:                                               

                pass

    if len(masks):

        mask = np.logical_and.reduce(masks)

        igood = mask.nonzero()[0]

        if len(igood) < nrecs:

            for i, x in enumerate(margs):

                if seqlist[i]:

                    margs[i] = x[igood]

    for i, x in enumerate(margs):

        if seqlist[i] and isinstance(x, np.ma.MaskedArray):

            margs[i] = x.filled()

    return margs





def _combine_masks(*args):

    

    if not len(args):

        return ()

    if is_scalar_or_string(args[0]):

        raise ValueError("First argument must be a sequence")

    nrecs = len(args[0])

    margs = []                                      

    seqlist = [False] * len(args)                                         

    masks = []                    

    for i, x in enumerate(args):

        if is_scalar_or_string(x) or len(x) != nrecs:

            margs.append(x)                        

        else:

            if isinstance(x, np.ma.MaskedArray) and x.ndim > 1:

                raise ValueError("Masked arrays must be 1-D")

            try:

                x = np.asanyarray(x)

            except (VisibleDeprecationWarning, ValueError):

                                                                              

                                                    

                x = np.asanyarray(x, dtype=object)

            if x.ndim == 1:

                x = safe_masked_invalid(x)

                seqlist[i] = True

                if np.ma.is_masked(x):

                    masks.append(np.ma.getmaskarray(x))

            margs.append(x)                      

    if len(masks):

        mask = np.logical_or.reduce(masks)

        for i, x in enumerate(margs):

            if seqlist[i]:

                margs[i] = np.ma.array(x, mask=mask)

    return margs





def _broadcast_with_masks(*args, compress=False):

    

                               

    masks = [k.mask for k in args if isinstance(k, np.ma.MaskedArray)]

                                  

    bcast = np.broadcast_arrays(*args, *masks)

    inputs = bcast[:len(args)]

    masks = bcast[len(args):]

    if masks:

                                    

        mask = np.logical_or.reduce(masks)

                                  

        if compress:

            inputs = [np.ma.array(k, mask=mask).compressed()

                      for k in inputs]

        else:

            inputs = [np.ma.array(k, mask=mask, dtype=float).filled(np.nan).ravel()

                      for k in inputs]

    else:

        inputs = [np.ravel(k) for k in inputs]

    return inputs





def boxplot_stats(X, whis=1.5, bootstrap=None, labels=None, autorange=False):

    



    def _bootstrap_median(data, N=5000):

                                                          

        M = len(data)

        percentiles = [2.5, 97.5]



        bs_index = np.random.randint(M, size=(N, M))

        bsData = data[bs_index]

        estimate = np.median(bsData, axis=1, overwrite_input=True)



        CI = np.percentile(estimate, percentiles)

        return CI



    def _compute_conf_interval(data, med, iqr, bootstrap):

        if bootstrap is not None:

                                                         

                                               

            CI = _bootstrap_median(data, N=bootstrap)

            notch_min = CI[0]

            notch_max = CI[1]

        else:



            N = len(data)

            notch_min = med - 1.57 * iqr / np.sqrt(N)

            notch_max = med + 1.57 * iqr / np.sqrt(N)



        return notch_min, notch_max



                               

    bxpstats = []



                                  

    X = _reshape_2D(X, "X")



    ncols = len(X)

    if labels is None:

        labels = itertools.repeat(None)

    elif len(labels) != ncols:

        raise ValueError("Dimensions of labels and X must be compatible")



    input_whis = whis

    for ii, (x, label) in enumerate(zip(X, labels)):



                    

        stats = {}

        if label is not None:

            stats['label'] = label



                                                                             

        whis = input_whis



                                                                

        bxpstats.append(stats)



                        

        if len(x) == 0:

            stats['fliers'] = np.array([])

            stats['mean'] = np.nan

            stats['med'] = np.nan

            stats['q1'] = np.nan

            stats['q3'] = np.nan

            stats['iqr'] = np.nan

            stats['cilo'] = np.nan

            stats['cihi'] = np.nan

            stats['whislo'] = np.nan

            stats['whishi'] = np.nan

            continue



                                                 

        x = np.ma.asarray(x)

        x = x.data[~x.mask].ravel()



                         

        stats['mean'] = np.mean(x)



                               

        q1, med, q3 = np.percentile(x, [25, 50, 75])



                             

        stats['iqr'] = q3 - q1

        if stats['iqr'] == 0 and autorange:

            whis = (0, 100)



                                      

        stats['cilo'], stats['cihi'] = _compute_conf_interval(

            x, med, stats['iqr'], bootstrap

        )



                                     

        if np.iterable(whis) and not isinstance(whis, str):

            loval, hival = np.percentile(x, whis)

        elif np.isreal(whis):

            loval = q1 - whis * stats['iqr']

            hival = q3 + whis * stats['iqr']

        else:

            raise ValueError('whis must be a float or list of percentiles')



                          

        wiskhi = x[x <= hival]

        if len(wiskhi) == 0 or np.max(wiskhi) < q3:

            stats['whishi'] = q3

        else:

            stats['whishi'] = np.max(wiskhi)



                         

        wisklo = x[x >= loval]

        if len(wisklo) == 0 or np.min(wisklo) > q1:

            stats['whislo'] = q1

        else:

            stats['whislo'] = np.min(wisklo)



                                            

        stats['fliers'] = np.concatenate([

            x[x < stats['whislo']],

            x[x > stats['whishi']],

        ])



                                    

        stats['q1'], stats['med'], stats['q3'] = q1, med, q3



    return bxpstats





                                                                       

ls_mapper = {'-': 'solid', '--': 'dashed', '-.': 'dashdot', ':': 'dotted'}

                                                                         

ls_mapper_r = {v: k for k, v in ls_mapper.items()}





def contiguous_regions(mask):

    

    mask = np.asarray(mask, dtype=bool)



    if not mask.size:

        return []



                                                            

    idx, = np.nonzero(mask[:-1] != mask[1:])

    idx += 1



                                                            

    idx = idx.tolist()



                                           

    if mask[0]:

        idx = [0] + idx

    if mask[-1]:

        idx.append(len(mask))



    return list(zip(idx[::2], idx[1::2]))





def is_math_text(s):

    

    s = str(s)

    dollar_count = s.count(r'$') - s.count(r'\$')

    even_dollars = (dollar_count > 0 and dollar_count % 2 == 0)

    return even_dollars





def _to_unmasked_float_array(x):

    

    if hasattr(x, 'mask'):

        return np.ma.asanyarray(x, float).filled(np.nan)

    else:

        return np.asanyarray(x, float)





def _check_1d(x):

    

                                                    

    x = _unpack_to_numpy(x)

                                                     

                                                                  

                                            

    if (not hasattr(x, 'shape') or

            not hasattr(x, 'ndim') or

            len(x.shape) < 1):

        return np.atleast_1d(x)

    else:

        return x





def _reshape_2D(X, name):

    



                                                    

    X = _unpack_to_numpy(X)



                                        

    if isinstance(X, np.ndarray):

        X = X.transpose()



        if len(X) == 0:

            return [[]]

        elif X.ndim == 1 and np.ndim(X[0]) == 0:

                                                      

            return [X]

        elif X.ndim in [1, 2]:

                                                                     

            return [np.reshape(x, -1) for x in X]

        else:

            raise ValueError(f'{name} must have 2 or fewer dimensions')



                                     

    if len(X) == 0:

        return [[]]



    result = []

    is_1d = True

    for xi in X:

                                                                

                              

        if not isinstance(xi, str):

            try:

                iter(xi)

            except TypeError:

                pass

            else:

                is_1d = False

        xi = np.asanyarray(xi)

        nd = np.ndim(xi)

        if nd > 1:

            raise ValueError(f'{name} must have 2 or fewer dimensions')

        result.append(xi.reshape(-1))



    if is_1d:

                                                  

        return [np.reshape(result, -1)]

    else:

                                                                    

        return result





def violin_stats(X, method, points=100, quantiles=None):

    



                                                          

    vpstats = []



                                           

    X = _reshape_2D(X, "X")



                                                              

    if quantiles is not None and len(quantiles) != 0:

        quantiles = _reshape_2D(quantiles, "quantiles")

                                                

    else:

        quantiles = [[]] * len(X)



                                                    

    if len(X) != len(quantiles):

        raise ValueError("List of violinplot statistics and quantiles values"

                         " must have the same length")



                         

    for (x, q) in zip(X, quantiles):

                                                     

        stats = {}



                                                    

        min_val = np.min(x)

        max_val = np.max(x)

        quantile_val = np.percentile(x, 100 * q)



                                              

        coords = np.linspace(min_val, max_val, points)

        stats['vals'] = method(x, coords)

        stats['coords'] = coords



                                                           

        stats['mean'] = np.mean(x)

        stats['median'] = np.median(x)

        stats['min'] = min_val

        stats['max'] = max_val

        stats['quantiles'] = np.atleast_1d(quantile_val)



                          

        vpstats.append(stats)



    return vpstats





def pts_to_prestep(x, *args):

    

    steps = np.zeros((1 + len(args), max(2 * len(x) - 1, 0)))

                                                                             

                                                 

    steps[0, 0::2] = x

    steps[0, 1::2] = steps[0, 0:-2:2]

    steps[1:, 0::2] = args

    steps[1:, 1::2] = steps[1:, 2::2]

    return steps





def pts_to_poststep(x, *args):

    

    steps = np.zeros((1 + len(args), max(2 * len(x) - 1, 0)))

    steps[0, 0::2] = x

    steps[0, 1::2] = steps[0, 2::2]

    steps[1:, 0::2] = args

    steps[1:, 1::2] = steps[1:, 0:-2:2]

    return steps





def pts_to_midstep(x, *args):

    

    steps = np.zeros((1 + len(args), 2 * len(x)))

    x = np.asanyarray(x)

    steps[0, 1:-1:2] = steps[0, 2::2] = (x[:-1] + x[1:]) / 2

    steps[0, :1] = x[:1]                                    

    steps[0, -1:] = x[-1:]

    steps[1:, 0::2] = args

    steps[1:, 1::2] = steps[1:, 0::2]

    return steps





STEP_LOOKUP_MAP = {'default': lambda x, y: (x, y),

                   'steps': pts_to_prestep,

                   'steps-pre': pts_to_prestep,

                   'steps-post': pts_to_poststep,

                   'steps-mid': pts_to_midstep}





def index_of(y):

    

    try:

        return y.index.to_numpy(), y.to_numpy()

    except AttributeError:

        pass

    try:

        y = _check_1d(y)

    except (VisibleDeprecationWarning, ValueError):

                                                                             

        pass

    else:

        return np.arange(y.shape[0], dtype=float), y

    raise ValueError('Input could not be cast to an at-least-1D NumPy array')





def safe_first_element(obj):

    

    if isinstance(obj, collections.abc.Iterator):

                                                 

                                                                                     

                                                                                  

                             

        try:

            return obj[0]

        except TypeError:

            pass

        raise RuntimeError("matplotlib does not support generators as input")

    return next(iter(obj))





def _safe_first_finite(obj):

    

    def safe_isfinite(val):

        if val is None:

            return False

        try:

            return math.isfinite(val)

        except (TypeError, ValueError):

                                                                    

                                                              

                                                               

            pass

        try:

            return np.isfinite(val) if np.isscalar(val) else True

        except TypeError:

                                                                         

                             

            return True



    if isinstance(obj, np.flatiter):

                                              

        return obj[0]

    elif isinstance(obj, collections.abc.Iterator):

        raise RuntimeError("matplotlib does not support generators as input")

    else:

        for val in obj:

            if safe_isfinite(val):

                return val

        return safe_first_element(obj)





def sanitize_sequence(data):

    

    return (list(data) if isinstance(data, collections.abc.MappingView)

            else data)





def _resize_sequence(seq, N):

    

    num_elements = len(seq)

    if N == num_elements:

        return seq

    elif N < num_elements:

        return seq[:N]

    else:

        return list(itertools.islice(itertools.cycle(seq), N))





def normalize_kwargs(kw, alias_mapping=None):

    

    from matplotlib.artist import Artist



    if kw is None:

        return {}



                                              

    if alias_mapping is None:

        alias_mapping = {}

    elif (isinstance(alias_mapping, type) and issubclass(alias_mapping, Artist)

          or isinstance(alias_mapping, Artist)):

        alias_mapping = getattr(alias_mapping, "_alias_map", {})



    to_canonical = {alias: canonical

                    for canonical, alias_list in alias_mapping.items()

                    for alias in alias_list}

    canonical_to_seen = {}

    ret = {}                     



    for k, v in kw.items():

        canonical = to_canonical.get(k, k)

        if canonical in canonical_to_seen:

            raise TypeError(f"Got both {canonical_to_seen[canonical]!r} and "

                            f"{k!r}, which are aliases of one another")

        canonical_to_seen[canonical] = k

        ret[canonical] = v



    return ret





@contextlib.contextmanager

def _lock_path(path):

    

    path = Path(path)

    lock_path = path.with_name(path.name + ".matplotlib-lock")

    retries = 50

    sleeptime = 0.1

    for _ in range(retries):

        try:

            with lock_path.open("xb"):

                break

        except FileExistsError:

            time.sleep(sleeptime)

    else:

        raise TimeoutError("""\
Lock error: Matplotlib failed to acquire the following lock file:
    {}
This maybe due to another process holding this lock file.  If you are sure no
other Matplotlib process is running, remove this file and try again.""".format(

            lock_path))

    try:

        yield

    finally:

        lock_path.unlink()





def _topmost_artist(

        artists,

        _cached_max=functools.partial(max, key=operator.attrgetter("zorder"))):

    

    return _cached_max(reversed(artists))





def _str_equal(obj, s):

    

    return isinstance(obj, str) and obj == s





def _str_lower_equal(obj, s):

    

    return isinstance(obj, str) and obj.lower() == s





def _array_perimeter(arr):

    

                                                              

                 

    forward = np.s_[0:-1]                  

    backward = np.s_[-1:0:-1]              

    return np.concatenate((

        arr[0, forward],

        arr[forward, -1],

        arr[-1, backward],

        arr[backward, 0],

    ))





def _unfold(arr, axis, size, step):

    

    new_shape = [*arr.shape, size]

    new_strides = [*arr.strides, arr.strides[axis]]

    new_shape[axis] = (new_shape[axis] - size) // step + 1

    new_strides[axis] = new_strides[axis] * step

    return np.lib.stride_tricks.as_strided(arr,

                                           shape=new_shape,

                                           strides=new_strides,

                                           writeable=False)





def _array_patch_perimeters(x, rstride, cstride):

    

    assert rstride > 0 and cstride > 0

    assert (x.shape[0] - 1) % rstride == 0

    assert (x.shape[1] - 1) % cstride == 0

                                                                          

                                                         

     

                   

                   

                   

                   

     

                                                                            

                                                                           

     

                                                                

                                                                  

                                                                    

     

                                                                           

                                           

    top = _unfold(x[:-1:rstride, :-1], 1, cstride, cstride)

    bottom = _unfold(x[rstride::rstride, 1:], 1, cstride, cstride)[..., ::-1]

    right = _unfold(x[:-1, cstride::cstride], 0, rstride, rstride)

    left = _unfold(x[1:, :-1:cstride], 0, rstride, rstride)[..., ::-1]

    return (np.concatenate((top, right, bottom, left), axis=2)

              .reshape(-1, 2 * (rstride + cstride)))





@contextlib.contextmanager

def _setattr_cm(obj, **kwargs):

    

    sentinel = object()

    origs = {}

    for attr in kwargs:

        orig = getattr(obj, attr, sentinel)

        if attr in obj.__dict__ or orig is sentinel:

                                                                    

                                                                 

            origs[attr] = orig

        else:

                                                                     

                                  

            cls_orig = getattr(type(obj), attr)

                                                                              

                                                     

            if isinstance(cls_orig, property):

                origs[attr] = orig

                                                                     

                                                                    

                                                                    

                                                                     

                                                                      

                                                                    

                                                                      

                                                    

            else:

                origs[attr] = sentinel



    try:

        for attr, val in kwargs.items():

            setattr(obj, attr, val)

        yield

    finally:

        for attr, orig in origs.items():

            if orig is sentinel:

                delattr(obj, attr)

            else:

                setattr(obj, attr, orig)





class _OrderedSet(collections.abc.MutableSet):

    def __init__(self):

        self._od = collections.OrderedDict()



    def __contains__(self, key):

        return key in self._od



    def __iter__(self):

        return iter(self._od)



    def __len__(self):

        return len(self._od)



    def add(self, key):

        self._od.pop(key, None)

        self._od[key] = None



    def discard(self, key):

        self._od.pop(key, None)





                                                                            

                                                         





def _premultiplied_argb32_to_unmultiplied_rgba8888(buf):

    

    rgba = np.take(                                               

        buf,

        [2, 1, 0, 3] if sys.byteorder == "little" else [1, 2, 3, 0], axis=2)

    rgb = rgba[..., :-1]

    alpha = rgba[..., -1]

                                                                       

    mask = alpha != 0

    for channel in np.rollaxis(rgb, -1):

        channel[mask] = (

            (channel[mask].astype(int) * 255 + alpha[mask] // 2)

            // alpha[mask])

    return rgba





def _unmultiplied_rgba8888_to_premultiplied_argb32(rgba8888):

    

    if sys.byteorder == "little":

        argb32 = np.take(rgba8888, [2, 1, 0, 3], axis=2)

        rgb24 = argb32[..., :-1]

        alpha8 = argb32[..., -1:]

    else:

        argb32 = np.take(rgba8888, [3, 0, 1, 2], axis=2)

        alpha8 = argb32[..., :1]

        rgb24 = argb32[..., 1:]

                                                                            

                                                                         

                                                   

    if alpha8.min() != 0xff:

        np.multiply(rgb24, alpha8 / 0xff, out=rgb24, casting="unsafe")

    return argb32





def _get_nonzero_slices(buf):

    

    x_nz, = buf.any(axis=0).nonzero()

    y_nz, = buf.any(axis=1).nonzero()

    if len(x_nz) and len(y_nz):

        l, r = x_nz[[0, -1]]

        b, t = y_nz[[0, -1]]

        return slice(b, t + 1), slice(l, r + 1)

    else:

        return slice(0, 0), slice(0, 0)





def _pformat_subprocess(command):

    

    return (command if isinstance(command, str)

            else " ".join(shlex.quote(os.fspath(arg)) for arg in command))





def _check_and_log_subprocess(command, logger, **kwargs):

    

    logger.debug('%s', _pformat_subprocess(command))

    proc = subprocess.run(command, capture_output=True, **kwargs)

    if proc.returncode:

        stdout = proc.stdout

        if isinstance(stdout, bytes):

            stdout = stdout.decode()

        stderr = proc.stderr

        if isinstance(stderr, bytes):

            stderr = stderr.decode()

        raise RuntimeError(

            f"The command\n"

            f"    {_pformat_subprocess(command)}\n"

            f"failed and generated the following output:\n"

            f"{stdout}\n"

            f"and the following error:\n"

            f"{stderr}")

    if proc.stdout:

        logger.debug("stdout:\n%s", proc.stdout)

    if proc.stderr:

        logger.debug("stderr:\n%s", proc.stderr)

    return proc.stdout





def _setup_new_guiapp():

    

                                                                               

                                                                               

              

    try:

        _c_internal_utils.Win32_GetCurrentProcessExplicitAppUserModelID()

    except OSError:

        _c_internal_utils.Win32_SetCurrentProcessExplicitAppUserModelID(

            "matplotlib")





def _format_approx(number, precision):

    

    return f'{number:.{precision}f}'.rstrip('0').rstrip('.') or '0'





def _g_sig_digits(value, delta):

    

                                                   

    if not math.isfinite(value):

        return 0

    if delta == 0:

        if value == 0:

                                                                            

                                                   

            return 3

                                                                             

                                                                        

        delta = abs(np.spacing(value))

                                                                               

                                                                            

                                                                              

                                                                             

                    

    return max(

        0,

        (math.floor(math.log10(abs(value))) + 1 if value else 1)

        - math.floor(math.log10(delta)))





def _unikey_or_keysym_to_mplkey(unikey, keysym):

    

                                                                             

    if unikey and unikey.isprintable():

        return unikey

    key = keysym.lower()

    if key.startswith("kp_"):                                  

        key = key[3:]

    if key.startswith("page_"):                  

        key = key.replace("page_", "page")

    if key.endswith(("_l", "_r")):                           

        key = key[:-2]

    if sys.platform == "darwin" and key == "meta":

                                                   

        key = "cmd"

    key = {

        "return": "enter",

        "prior": "pageup",               

        "next": "pagedown",               

    }.get(key, key)

    return key





@functools.cache

def _make_class_factory(mixin_class, fmt, attr_name=None):

    



    @functools.cache

    def class_factory(axes_class):

                                                                 

        if issubclass(axes_class, mixin_class):

            return axes_class



                                                                               

                                                   

        base_class = axes_class



        class subcls(mixin_class, base_class):

                                                                        

            __module__ = mixin_class.__module__



            def __reduce__(self):

                return (_picklable_class_constructor,

                        (mixin_class, fmt, attr_name, base_class),

                        self.__getstate__())



        subcls.__name__ = subcls.__qualname__ = fmt.format(base_class.__name__)

        if attr_name is not None:

            setattr(subcls, attr_name, base_class)

        return subcls



    class_factory.__module__ = mixin_class.__module__

    return class_factory





def _picklable_class_constructor(mixin_class, fmt, attr_name, base_class):

    

    factory = _make_class_factory(mixin_class, fmt, attr_name)

    cls = factory(base_class)

    return cls.__new__(cls)





def _is_torch_array(x):

    

    try:

                                                                         

                                                                            

        tp = sys.modules.get("torch").Tensor

    except AttributeError:

        return False                                                                    

    return (isinstance(tp, type)                                                

            and isinstance(x, tp))





def _is_jax_array(x):

    

    try:

                                                                       

                                                                        

        tp = sys.modules.get("jax").Array

    except AttributeError:

        return False                                                                   

    return (isinstance(tp, type)                                                

            and isinstance(x, tp))





def _is_pandas_dataframe(x):

    

    try:

                                                                          

                                                                                  

        tp = sys.modules.get("pandas").DataFrame

    except AttributeError:

        return False                                                                   

    return (isinstance(tp, type)                                                

            and isinstance(x, tp))





def _is_tensorflow_array(x):

    

    try:

                                                                              

                                                                         

                                                                             

                                                                      

                                                       

        is_tensor = sys.modules.get("tensorflow").is_tensor

    except AttributeError:

        return False

    try:

        return is_tensor(x)

    except Exception:

        return False                                                





def _unpack_to_numpy(x):

    

    if isinstance(x, np.ndarray):

                                   

        return x

    if hasattr(x, 'to_numpy'):

                                                                          

        return x.to_numpy()

    if hasattr(x, 'values'):

        xtmp = x.values

                                                                               

                                                             

        if isinstance(xtmp, np.ndarray):

            return xtmp

    if _is_torch_array(x) or _is_jax_array(x) or _is_tensorflow_array(x):

                                                                                

                                                                        

                                                                                                      

                                                     

        xtmp = np.asarray(x)



                                                                           

        if isinstance(xtmp, np.ndarray):

            return xtmp

    return x





def _auto_format_str(fmt, value):

    

    try:

        return fmt % (value,)

    except (TypeError, ValueError):

        return fmt.format(value)


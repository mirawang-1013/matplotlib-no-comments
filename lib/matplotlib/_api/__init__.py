



import difflib

import functools

import itertools

import pathlib

import re

import sys

import warnings



from .deprecation import (              

    deprecated, warn_deprecated,

    rename_parameter, delete_parameter, make_keyword_only,

    deprecate_method_override, deprecate_privatize_attribute,

    suppress_matplotlib_deprecation_warning,

    MatplotlibDeprecationWarning)





                                                                      

                                                                       

                                                          

class _Unset:

    def __repr__(self):

        return "<UNSET>"

UNSET = _Unset()





class classproperty:

    



    def __init__(self, fget, fset=None, fdel=None, doc=None):

        self._fget = fget

        if fset is not None or fdel is not None:

            raise ValueError('classproperty only implements fget.')

        self.fset = fset

        self.fdel = fdel

                                  

        self._doc = doc



    def __get__(self, instance, owner):

        return self._fget(owner)



    @property

    def fget(self):

        return self._fget





                                                                                        

                                                      



def check_isinstance(types, /, **kwargs):

    

    none_type = type(None)

    types = ((types,) if isinstance(types, type) else

             (none_type,) if types is None else

             tuple(none_type if tp is None else tp for tp in types))



    def type_name(tp):

        return ("None" if tp is none_type

                else tp.__qualname__ if tp.__module__ == "builtins"

                else f"{tp.__module__}.{tp.__qualname__}")



    for k, v in kwargs.items():

        if not isinstance(v, types):

            names = [*map(type_name, types)]

            if "None" in names:                                          

                names.remove("None")

                names.append("None")

            raise TypeError(

                "{!r} must be an instance of {}, not a {}".format(

                    k,

                    ", ".join(names[:-1]) + " or " + names[-1]

                    if len(names) > 1 else names[0],

                    type_name(type(v))))





def check_in_list(values, /, *, _print_supported_values=True, **kwargs):

    

    if not kwargs:

        raise TypeError("No argument to check!")

    for key, val in kwargs.items():

        if val not in values:

            msg = f"{val!r} is not a valid value for {key}"

            if _print_supported_values:

                msg += f"; supported values are {', '.join(map(repr, values))}"

            raise ValueError(msg)





def check_shape(shape, /, **kwargs):

    

    for k, v in kwargs.items():

        data_shape = v.shape



        if (len(data_shape) != len(shape)

                or any(s != t and t is not None for s, t in zip(data_shape, shape))):

            dim_labels = iter(itertools.chain(

                'NMLKJIH',

                (f"D{i}" for i in itertools.count())))

            text_shape = ", ".join([str(n) if n is not None else next(dim_labels)

                                    for n in shape[::-1]][::-1])

            if len(shape) == 1:

                text_shape += ","



            raise ValueError(

                f"{k!r} must be {len(shape)}D with shape ({text_shape}), "

                f"but your input has shape {v.shape}"

            )





def check_getitem(mapping, /, _error_cls=ValueError, **kwargs):

    

    if len(kwargs) != 1:

        raise ValueError("check_getitem takes a single keyword argument")

    (k, v), = kwargs.items()

    try:

        return mapping[v]

    except KeyError:

        if len(mapping) > 5:

            if len(best := difflib.get_close_matches(v, mapping.keys(), cutoff=0.5)):

                suggestion = f"Did you mean one of {best}?"

            else:

                suggestion = ""

        else:

            suggestion = f"Supported values are {', '.join(map(repr, mapping))}"

        raise _error_cls(f"{v!r} is not a valid value for {k}. {suggestion}") from None





def caching_module_getattr(cls):

    



    assert cls.__name__ == "__getattr__"

                                            

    props = {name: prop for name, prop in vars(cls).items()

             if isinstance(prop, property)}

    instance = cls()



    @functools.cache

    def __getattr__(name):

        if name in props:

            return props[name].__get__(instance)

        raise AttributeError(

            f"module {cls.__module__!r} has no attribute {name!r}")



    return __getattr__





def define_aliases(alias_d, cls=None):

    

    if cls is None:                                      

        return functools.partial(define_aliases, alias_d)



    def make_alias(name):                                  

        @functools.wraps(getattr(cls, name))

        def method(self, *args, **kwargs):

            return getattr(self, name)(*args, **kwargs)

        return method



    for prop, aliases in alias_d.items():

        exists = False

        for prefix in ["get_", "set_"]:

            if prefix + prop in vars(cls):

                exists = True

                for alias in aliases:

                    method = make_alias(prefix + prop)

                    method.__name__ = prefix + alias

                    method.__doc__ = f"Alias for `{prefix + prop}`."

                    setattr(cls, prefix + alias, method)

        if not exists:

            raise ValueError(

                f"Neither getter nor setter exists for {prop!r}")



    def get_aliased_and_aliases(d):

        return {*d, *(alias for aliases in d.values() for alias in aliases)}



    preexisting_aliases = getattr(cls, "_alias_map", {})

    conflicting = (get_aliased_and_aliases(preexisting_aliases)

                   & get_aliased_and_aliases(alias_d))

    if conflicting:

                                                       

        raise NotImplementedError(

            f"Parent class already defines conflicting aliases: {conflicting}")

    cls._alias_map = {**preexisting_aliases, **alias_d}

    return cls





def select_matching_signature(funcs, *args, **kwargs):

    

                                                                               

                                                                         

                                                                               

    for i, func in enumerate(funcs):

        try:

            return func(*args, **kwargs)

        except TypeError:

            if i == len(funcs) - 1:

                raise





def nargs_error(name, takes, given):

    

    return TypeError(f"{name}() takes {takes} positional arguments but "

                     f"{given} were given")





def kwarg_error(name, kw):

    

    if not isinstance(kw, str):

        kw = next(iter(kw))

    return TypeError(f"{name}() got an unexpected keyword argument '{kw}'")





def recursive_subclasses(cls):

    

    yield cls

    for subcls in cls.__subclasses__():

        yield from recursive_subclasses(subcls)





def warn_external(message, category=None):

    

    kwargs = {}

    if sys.version_info[:2] >= (3, 12):

                                                                           

        basedir = pathlib.Path(__file__).parents[2]

        kwargs['skip_file_prefixes'] = (str(basedir / 'matplotlib'),

                                        str(basedir / 'mpl_toolkits'))

    else:

        frame = sys._getframe()

        for stacklevel in itertools.count(1):

            if frame is None:

                                                                       

                kwargs['stacklevel'] = stacklevel

                break

            if not re.match(r"\A(matplotlib|mpl_toolkits)(\Z|\.(?!tests\.))",

                                                                              

                            frame.f_globals.get("__name__", "")):

                kwargs['stacklevel'] = stacklevel

                break

            frame = frame.f_back

                                                                         

        del frame

    warnings.warn(message, category, **kwargs)


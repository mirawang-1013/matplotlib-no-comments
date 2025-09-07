



import contextlib

import functools

import inspect

import math

import warnings





class MatplotlibDeprecationWarning(DeprecationWarning):

    





def _generate_deprecation_warning(

        since, message='', name='', alternative='', pending=False, obj_type='',

        addendum='', *, removal=''):

    if pending:

        if removal:

            raise ValueError("A pending deprecation cannot have a scheduled removal")

    elif removal == '':

        macro, meso, *_ = since.split('.')

        removal = f'{macro}.{int(meso) + 2}'

    if not message:

        message = (

            ("The %(name)s %(obj_type)s" if obj_type else "%(name)s") +

            (" will be deprecated in a future version" if pending else

             (" was deprecated in Matplotlib %(since)s" +

              (" and will be removed in %(removal)s" if removal else ""))) +

            "." +

            (" Use %(alternative)s instead." if alternative else "") +

            (" %(addendum)s" if addendum else ""))

    warning_cls = PendingDeprecationWarning if pending else MatplotlibDeprecationWarning

    return warning_cls(message % dict(

        func=name, name=name, obj_type=obj_type, since=since, removal=removal,

        alternative=alternative, addendum=addendum))





def warn_deprecated(

        since, *, message='', name='', alternative='', pending=False,

        obj_type='', addendum='', removal=''):

    

    warning = _generate_deprecation_warning(

        since, message, name, alternative, pending, obj_type, addendum,

        removal=removal)

    from . import warn_external

    warn_external(warning, category=MatplotlibDeprecationWarning)





def deprecated(since, *, message='', name='', alternative='', pending=False,

               obj_type=None, addendum='', removal=''):

    



    def deprecate(obj, message=message, name=name, alternative=alternative,

                  pending=pending, obj_type=obj_type, addendum=addendum):

        from matplotlib._api import classproperty



        if isinstance(obj, type):

            if obj_type is None:

                obj_type = "class"

            func = obj.__init__

            name = name or obj.__name__

            old_doc = obj.__doc__



            def finalize(wrapper, new_doc):

                try:

                    obj.__doc__ = new_doc

                except AttributeError:                                        

                    pass

                obj.__init__ = functools.wraps(obj.__init__)(wrapper)

                return obj



        elif isinstance(obj, (property, classproperty)):

            if obj_type is None:

                obj_type = "attribute"

            func = None

            name = name or obj.fget.__name__

            old_doc = obj.__doc__



            class _deprecated_property(type(obj)):

                def __get__(self, instance, owner=None):

                    if instance is not None or owner is not None
                            and isinstance(self, classproperty):

                        emit_warning()

                    return super().__get__(instance, owner)



                def __set__(self, instance, value):

                    if instance is not None:

                        emit_warning()

                    return super().__set__(instance, value)



                def __delete__(self, instance):

                    if instance is not None:

                        emit_warning()

                    return super().__delete__(instance)



                def __set_name__(self, owner, set_name):

                    nonlocal name

                    if name == "<lambda>":

                        name = set_name



            def finalize(_, new_doc):

                return _deprecated_property(

                    fget=obj.fget, fset=obj.fset, fdel=obj.fdel, doc=new_doc)



        else:

            if obj_type is None:

                obj_type = "function"

            func = obj

            name = name or obj.__name__

            old_doc = func.__doc__



            def finalize(wrapper, new_doc):

                wrapper = functools.wraps(func)(wrapper)

                wrapper.__doc__ = new_doc

                return wrapper



        def emit_warning():

            warn_deprecated(

                since, message=message, name=name, alternative=alternative,

                pending=pending, obj_type=obj_type, addendum=addendum,

                removal=removal)



        def wrapper(*args, **kwargs):

            emit_warning()

            return func(*args, **kwargs)



        old_doc = inspect.cleandoc(old_doc or '').strip('\n')



        notes_header = '\nNotes\n-----'

        second_arg = ' '.join([t.strip() for t in

                               (message, f"Use {alternative} instead."

                                if alternative else "", addendum) if t])

        new_doc = (f"[*Deprecated*] {old_doc}\n"

                   f"{notes_header if notes_header not in old_doc else ''}\n"

                   f".. deprecated:: {since}\n"

                   f"   {second_arg}")



        if not old_doc:

                                                                              

                                                             

            new_doc += r'\ '



        return finalize(wrapper, new_doc)



    return deprecate





class deprecate_privatize_attribute:

    



    def __init__(self, *args, **kwargs):

        self.deprecator = deprecated(*args, **kwargs)



    def __set_name__(self, owner, name):

        setattr(owner, name, self.deprecator(

            property(lambda self: getattr(self, f"_{name}"),

                     lambda self, value: setattr(self, f"_{name}", value)),

            name=name))





                                                                           

                                                                               

                                                                          

                                                                             

                                          

DECORATORS = {}





def rename_parameter(since, old, new, func=None):

    



    decorator = functools.partial(rename_parameter, since, old, new)



    if func is None:

        return decorator



    signature = inspect.signature(func)

    assert old not in signature.parameters, (

        f"Matplotlib internal error: {old!r} cannot be a parameter for "

        f"{func.__name__}()")

    assert new in signature.parameters, (

        f"Matplotlib internal error: {new!r} must be a parameter for "

        f"{func.__name__}()")



    @functools.wraps(func)

    def wrapper(*args, **kwargs):

        if old in kwargs:

            warn_deprecated(

                since, message=f"The {old!r} parameter of {func.__name__}() "

                f"has been renamed {new!r} since Matplotlib {since}; support "

                f"for the old name will be dropped in %(removal)s.")

            kwargs[new] = kwargs.pop(old)

        return func(*args, **kwargs)



                                                                        

                                                                             

                                                                              

                                                                     



    DECORATORS[wrapper] = decorator

    return wrapper





class _deprecated_parameter_class:

    def __repr__(self):

        return "<deprecated parameter>"





_deprecated_parameter = _deprecated_parameter_class()





def delete_parameter(since, name, func=None, **kwargs):

    



    decorator = functools.partial(delete_parameter, since, name, **kwargs)



    if func is None:

        return decorator



    signature = inspect.signature(func)

                                                                       

                                                                            

                                

    kwargs_name = next((param.name for param in signature.parameters.values()

                        if param.kind == inspect.Parameter.VAR_KEYWORD), None)

    if name in signature.parameters:

        kind = signature.parameters[name].kind

        is_varargs = kind is inspect.Parameter.VAR_POSITIONAL

        is_varkwargs = kind is inspect.Parameter.VAR_KEYWORD

        if not is_varargs and not is_varkwargs:

            name_idx = (

                                                                    

                math.inf if kind is inspect.Parameter.KEYWORD_ONLY

                                                                              

                                                                           

                else [*signature.parameters].index(name))

            func.__signature__ = signature = signature.replace(parameters=[

                param.replace(default=_deprecated_parameter)

                if param.name == name else param

                for param in signature.parameters.values()])

        else:

            name_idx = -1                                                     

    else:

        is_varargs = is_varkwargs = False

                                                            

        name_idx = math.inf

        assert kwargs_name, (

            f"Matplotlib internal error: {name!r} must be a parameter for "

            f"{func.__name__}()")



    addendum = kwargs.pop('addendum', None)



    @functools.wraps(func)

    def wrapper(*inner_args, **inner_kwargs):

        if len(inner_args) <= name_idx and name not in inner_kwargs:

                                                                               

                              

            return func(*inner_args, **inner_kwargs)

        arguments = signature.bind(*inner_args, **inner_kwargs).arguments

        if is_varargs and arguments.get(name):

            warn_deprecated(

                since, message=f"Additional positional arguments to "

                f"{func.__name__}() are deprecated since %(since)s and "

                f"support for them will be removed in %(removal)s.")

        elif is_varkwargs and arguments.get(name):

            warn_deprecated(

                since, message=f"Additional keyword arguments to "

                f"{func.__name__}() are deprecated since %(since)s and "

                f"support for them will be removed in %(removal)s.")

                                                                         

                                                        

        elif any(name in d and d[name] != _deprecated_parameter

                 for d in [arguments, arguments.get(kwargs_name, {})]):

            deprecation_addendum = (

                f"If any parameter follows {name!r}, they should be passed as "

                f"keyword, not positionally.")

            warn_deprecated(

                since,

                name=repr(name),

                obj_type=f"parameter of {func.__name__}()",

                addendum=(addendum + " " + deprecation_addendum) if addendum

                         else deprecation_addendum,

                **kwargs)

        return func(*inner_args, **inner_kwargs)



    DECORATORS[wrapper] = decorator

    return wrapper





def make_keyword_only(since, name, func=None):

    



    decorator = functools.partial(make_keyword_only, since, name)



    if func is None:

        return decorator



    signature = inspect.signature(func)

    POK = inspect.Parameter.POSITIONAL_OR_KEYWORD

    KWO = inspect.Parameter.KEYWORD_ONLY

    assert (name in signature.parameters

            and signature.parameters[name].kind == POK), (

        f"Matplotlib internal error: {name!r} must be a positional-or-keyword "

        f"parameter for {func.__name__}(). If this error happens on a function with a "

        f"pyplot wrapper, make sure make_keyword_only() is the outermost decorator.")

    names = [*signature.parameters]

    name_idx = names.index(name)

    kwonly = [name for name in names[name_idx:]

              if signature.parameters[name].kind == POK]



    @functools.wraps(func)

    def wrapper(*args, **kwargs):

                                                                           

                                                                  

                                                                         

        if len(args) > name_idx:

            warn_deprecated(

                since, message="Passing the %(name)s %(obj_type)s "

                "positionally is deprecated since Matplotlib %(since)s; the "

                "parameter will become keyword-only in %(removal)s.",

                name=name, obj_type=f"parameter of {func.__name__}()")

        return func(*args, **kwargs)



                                                                  

    wrapper.__signature__ = signature.replace(parameters=[

        param.replace(kind=KWO) if param.name in kwonly else param

        for param in signature.parameters.values()])

    DECORATORS[wrapper] = decorator

    return wrapper





def deprecate_method_override(method, obj, *, allow_empty=False, **kwargs):

    



    def empty(): pass

    def empty_with_docstring(): """doc"""



    name = method.__name__

    bound_child = getattr(obj, name)

    bound_base = (

        method                                                           

        if isinstance(bound_child, type(empty)) and isinstance(obj, type)

        else method.__get__(obj))

    if (bound_child != bound_base

            and (not allow_empty

                 or (getattr(getattr(bound_child, "__code__", None),

                             "co_code", None)

                     not in [empty.__code__.co_code,

                             empty_with_docstring.__code__.co_code]))):

        warn_deprecated(**{"name": name, "obj_type": "method", **kwargs})

        return bound_child

    return None





@contextlib.contextmanager

def suppress_matplotlib_deprecation_warning():

    with warnings.catch_warnings():

        warnings.simplefilter("ignore", MatplotlibDeprecationWarning)

        yield


import inspect



from . import _api





def kwarg_doc(text):

    

    def decorator(func):

        func._kwarg_doc = text

        return func

    return decorator





class Substitution:

    

    def __init__(self, *args, **kwargs):

        if args and kwargs:

            raise TypeError("Only positional or keyword args are allowed")

        self.params = args or kwargs



    def __call__(self, func):

        if func.__doc__:

            func.__doc__ = inspect.cleandoc(func.__doc__) % self.params

        return func





class _ArtistKwdocLoader(dict):

    def __missing__(self, key):

        if not key.endswith(":kwdoc"):

            raise KeyError(key)

        name = key[:-len(":kwdoc")]

        from matplotlib.artist import Artist, kwdoc

        try:

            cls, = (cls for cls in _api.recursive_subclasses(Artist)

                    if cls.__name__ == name)

        except ValueError as e:

            raise KeyError(key) from e

        return self.setdefault(key, kwdoc(cls))





class _ArtistPropertiesSubstitution:

    



    def __init__(self):

        self.params = _ArtistKwdocLoader()



    def register(self, **kwargs):

        

        self.params.update(**kwargs)



    def __call__(self, obj):

        if obj.__doc__:

            obj.__doc__ = inspect.cleandoc(obj.__doc__) % self.params

        if isinstance(obj, type) and obj.__init__ != object.__init__:

            self(obj.__init__)

        return obj





def copy(source):

    

    def do_copy(target):

        if source.__doc__:

            target.__doc__ = source.__doc__

        return target

    return do_copy





                                                                          

                        

interpd = _ArtistPropertiesSubstitution()


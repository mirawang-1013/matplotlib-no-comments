



from collections.abc import Mapping



import matplotlib as mpl

from matplotlib import _api, colors

                               

from matplotlib.colorizer import _ScalarMappable as ScalarMappable        

from matplotlib._cm import datad

from matplotlib._cm_listed import cmaps as cmaps_listed

from matplotlib._cm_multivar import cmap_families as multivar_cmaps

from matplotlib._cm_bivar import cmaps as bivar_cmaps





_LUTSIZE = mpl.rcParams['image.lut']





def _gen_cmap_registry():

    

    cmap_d = {**cmaps_listed}

    for name, spec in datad.items():

        cmap_d[name] = (                                           

            colors.LinearSegmentedColormap(name, spec, _LUTSIZE)

            if 'red' in spec else

            colors.ListedColormap(spec['listed'], name)

            if 'listed' in spec else

            colors.LinearSegmentedColormap.from_list(name, spec, _LUTSIZE))



                                                  

    aliases = {

                                

        'grey': 'gray',

        'gist_grey': 'gist_gray',

        'gist_yerg': 'gist_yarg',

        'Grays': 'Greys',

    }

    for alias, original_name in aliases.items():

        cmap = cmap_d[original_name].copy()

        cmap.name = alias

        cmap_d[alias] = cmap



                              

    for cmap in list(cmap_d.values()):

        rmap = cmap.reversed()

        cmap_d[rmap.name] = rmap

    return cmap_d





class ColormapRegistry(Mapping):

    

    def __init__(self, cmaps):

        self._cmaps = cmaps

        self._builtin_cmaps = tuple(cmaps)



    def __getitem__(self, item):

        cmap = _api.check_getitem(self._cmaps, colormap=item, _error_cls=KeyError)

        return cmap.copy()



    def __iter__(self):

        return iter(self._cmaps)



    def __len__(self):

        return len(self._cmaps)



    def __str__(self):

        return ('ColormapRegistry; available colormaps:\n' +

                ', '.join(f"'{name}'" for name in self))



    def __call__(self):

        

        return list(self)



    def register(self, cmap, *, name=None, force=False):

        

        _api.check_isinstance(colors.Colormap, cmap=cmap)



        name = name or cmap.name

        if name in self:

            if not force:

                                                                  

                                            

                raise ValueError(

                    f'A colormap named "{name}" is already registered.')

            elif name in self._builtin_cmaps:

                                                      

                raise ValueError("Re-registering the builtin cmap "

                                 f"{name!r} is not allowed.")



                                                                    

            _api.warn_external(f"Overwriting the cmap {name!r} "

                               "that was already in the registry.")



        self._cmaps[name] = cmap.copy()

                                                                                    

                                                                                   

                                                                     

        if self._cmaps[name].name != name:

            self._cmaps[name].name = name



    def unregister(self, name):

        

        if name in self._builtin_cmaps:

            raise ValueError(f"cannot unregister {name!r} which is a builtin "

                             "colormap.")

        self._cmaps.pop(name, None)



    def get_cmap(self, cmap):

        

                                   

        if cmap is None:

            return self[mpl.rcParams["image.cmap"]]



                                                            

        if isinstance(cmap, colors.Colormap):

            return cmap

        if isinstance(cmap, str):

            _api.check_in_list(sorted(_colormaps), cmap=cmap)

                                                          

            return self[cmap]

        raise TypeError(

            'get_cmap expects None or an instance of a str or Colormap . ' +

            f'you passed {cmap!r} of type {type(cmap)}'

        )





                                                                               

                                                                           

         

_colormaps = ColormapRegistry(_gen_cmap_registry())

globals().update(_colormaps)



_multivar_colormaps = ColormapRegistry(multivar_cmaps)



_bivar_colormaps = ColormapRegistry(bivar_cmaps)





def _ensure_cmap(cmap):

    

    if isinstance(cmap, colors.Colormap):

        return cmap

    cmap_name = mpl._val_or_rc(cmap, "image.cmap")

                                                                           

                                                         

    if cmap_name not in _colormaps:

        _api.check_in_list(sorted(_colormaps), cmap=cmap_name)

    return mpl.colormaps[cmap_name]


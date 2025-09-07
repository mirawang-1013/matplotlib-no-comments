



import itertools

import functools

import math

from numbers import Number, Real

import warnings



import numpy as np



import matplotlib as mpl

from . import (_api, _path, artist, cbook, colorizer as mcolorizer, colors as mcolors,

               _docstring, hatch as mhatch, lines as mlines, path as mpath, transforms)

from ._enums import JoinStyle, CapStyle





                                                                         

                    

@_api.define_aliases({

    "antialiased": ["antialiaseds", "aa"],

    "edgecolor": ["edgecolors", "ec"],

    "facecolor": ["facecolors", "fc"],

    "linestyle": ["linestyles", "dashes", "ls"],

    "linewidth": ["linewidths", "lw"],

    "offset_transform": ["transOffset"],

})

class Collection(mcolorizer.ColorizingArtist):

    

                                                                    

                                                                 

                                                                     

                                              

                                                

                                                                   

    _transforms = np.empty((0, 3, 3))



                                                   

                                 

    _edge_default = False



    @_docstring.interpd

    def __init__(self, *,

                 edgecolors=None,

                 facecolors=None,

                 hatchcolors=None,

                 linewidths=None,

                 linestyles='solid',

                 capstyle=None,

                 joinstyle=None,

                 antialiaseds=None,

                 offsets=None,

                 offset_transform=None,

                 norm=None,                               

                 cmap=None,         

                 colorizer=None,

                 pickradius=5.0,

                 hatch=None,

                 urls=None,

                 zorder=1,

                 **kwargs

                 ):

        



        super().__init__(self._get_colorizer(cmap, norm, colorizer))

                                         

                                                              

        self._us_linestyles = [(0, None)]

                               

        self._linestyles = [(0, None)]

                                               

        self._us_lw = [0]

        self._linewidths = [0]



        self._gapcolor = None                                          



                                                                             

        self._face_is_mapped = None

        self._edge_is_mapped = None

        self._mapped_colors = None                                       

        self._hatch_linewidth = mpl.rcParams['hatch.linewidth']

        self.set_facecolor(facecolors)

        self.set_edgecolor(edgecolors)

        self.set_linewidth(linewidths)

        self.set_linestyle(linestyles)

        self.set_antialiased(antialiaseds)

        self.set_pickradius(pickradius)

        self.set_urls(urls)

        self.set_hatch(hatch)

        self.set_hatchcolor(hatchcolors)

        self.set_zorder(zorder)



        if capstyle:

            self.set_capstyle(capstyle)

        else:

            self._capstyle = None



        if joinstyle:

            self.set_joinstyle(joinstyle)

        else:

            self._joinstyle = None



        if offsets is not None:

            offsets = np.asanyarray(offsets, float)

                                                        

            if offsets.shape == (2,):

                offsets = offsets[None, :]



        self._offsets = offsets

        self._offset_transform = offset_transform



        self._path_effects = None

        self._internal_update(kwargs)

        self._paths = None



    def get_paths(self):

        return self._paths



    def set_paths(self, paths):

        self._paths = paths

        self.stale = True



    def get_transforms(self):

        return self._transforms



    def get_offset_transform(self):

        

        if self._offset_transform is None:

            self._offset_transform = transforms.IdentityTransform()

        elif (not isinstance(self._offset_transform, transforms.Transform)

              and hasattr(self._offset_transform, '_as_mpl_transform')):

            self._offset_transform =
                self._offset_transform._as_mpl_transform(self.axes)

        return self._offset_transform



    def set_offset_transform(self, offset_transform):

        

        self._offset_transform = offset_transform



    def get_datalim(self, transData):

                                                                 

         

                                                                      

                                                            

         

                                                                            

                                                                       

                                                                     

         

                                                                          

                                     

                                                                           

                                                 

         

                                          



        transform = self.get_transform()

        offset_trf = self.get_offset_transform()

        if not (isinstance(offset_trf, transforms.IdentityTransform)

                or offset_trf.contains_branch(transData)):

                                                                

                                                  

            return transforms.Bbox.null()



        paths = self.get_paths()

        if not len(paths):

                                   

            return transforms.Bbox.null()



        if not transform.is_affine:

            paths = [transform.transform_path_non_affine(p) for p in paths]

                                                                            

                                                                      

                                                                             

                                                                    



        offsets = self.get_offsets()



        if any(transform.contains_branch_seperately(transData)):

                                                                   

                                                                    

                                                               

                                                        

            if isinstance(offsets, np.ma.MaskedArray):

                offsets = offsets.filled(np.nan)

                                                                               

            return mpath.get_path_collection_extents(

                transform.get_affine() - transData, paths,

                self.get_transforms(),

                offset_trf.transform_non_affine(offsets),

                offset_trf.get_affine().frozen())



                                                                        

        if self._offsets is not None:

                                                                    

                                                                  

                                                                        

                                                                    

                       

            offsets = (offset_trf - transData).transform(offsets)

                                     

            offsets = np.ma.masked_invalid(offsets)

            if not offsets.mask.all():

                bbox = transforms.Bbox.null()

                bbox.update_from_data_xy(offsets)

                return bbox

        return transforms.Bbox.null()



    def get_window_extent(self, renderer=None):

                                                           

                                              

        return self.get_datalim(transforms.IdentityTransform())



    def _prepare_points(self):

                                             



        transform = self.get_transform()

        offset_trf = self.get_offset_transform()

        offsets = self.get_offsets()

        paths = self.get_paths()



        if self.have_units():

            paths = []

            for path in self.get_paths():

                vertices = path.vertices

                xs, ys = vertices[:, 0], vertices[:, 1]

                xs = self.convert_xunits(xs)

                ys = self.convert_yunits(ys)

                paths.append(mpath.Path(np.column_stack([xs, ys]), path.codes))

            xs = self.convert_xunits(offsets[:, 0])

            ys = self.convert_yunits(offsets[:, 1])

            offsets = np.ma.column_stack([xs, ys])



        if not transform.is_affine:

            paths = [transform.transform_path_non_affine(path)

                     for path in paths]

            transform = transform.get_affine()

        if not offset_trf.is_affine:

            offsets = offset_trf.transform_non_affine(offsets)

                                                                     

            offset_trf = offset_trf.get_affine()



        if isinstance(offsets, np.ma.MaskedArray):

            offsets = offsets.filled(np.nan)

                                                                

                                                       



        return transform, offset_trf, offsets, paths



    @artist.allow_rasterization

    def draw(self, renderer):

        if not self.get_visible():

            return

        renderer.open_group(self.__class__.__name__, self.get_gid())



        self.update_scalarmappable()



        transform, offset_trf, offsets, paths = self._prepare_points()



        gc = renderer.new_gc()

        self._set_gc_clip(gc)

        gc.set_snap(self.get_snap())



        if self._hatch:

            gc.set_hatch(self._hatch)

            gc.set_hatch_linewidth(self._hatch_linewidth)



        if self.get_sketch_params() is not None:

            gc.set_sketch_params(*self.get_sketch_params())



        if self.get_path_effects():

            from matplotlib.patheffects import PathEffectRenderer

            renderer = PathEffectRenderer(self.get_path_effects(), renderer)



                                                                      

                                                                   

                                                                     

                                                                     

                     



        trans = self.get_transforms()

        facecolors = self.get_facecolor()

        edgecolors = self.get_edgecolor()

        do_single_path_optimization = False

        if (len(paths) == 1 and len(trans) <= 1 and

                len(facecolors) == 1 and len(edgecolors) == 1 and

                len(self._linewidths) == 1 and

                all(ls[1] is None for ls in self._linestyles) and

                len(self._antialiaseds) == 1 and len(self._urls) == 1 and

                self.get_hatch() is None):

            if len(trans):

                combined_transform = transforms.Affine2D(trans[0]) + transform

            else:

                combined_transform = transform

            extents = paths[0].get_extents(combined_transform)

            if (extents.width < self.get_figure(root=True).bbox.width

                    and extents.height < self.get_figure(root=True).bbox.height):

                do_single_path_optimization = True



        if self._joinstyle:

            gc.set_joinstyle(self._joinstyle)



        if self._capstyle:

            gc.set_capstyle(self._capstyle)



        if do_single_path_optimization:

            gc.set_foreground(tuple(edgecolors[0]))

            gc.set_linewidth(self._linewidths[0])

            gc.set_dashes(*self._linestyles[0])

            gc.set_antialiased(self._antialiaseds[0])

            gc.set_url(self._urls[0])

            renderer.draw_markers(

                gc, paths[0], combined_transform.frozen(),

                mpath.Path(offsets), offset_trf, tuple(facecolors[0]))

        else:

                                                                          

                                                 



                                                                                      

                                                                                    

                                                                                     

                                                       

            hatchcolors_arg_supported = True

            try:

                renderer.draw_path_collection(

                    gc, transform.frozen(), [],

                    self.get_transforms(), offsets, offset_trf,

                    self.get_facecolor(), self.get_edgecolor(),

                    self._linewidths, self._linestyles,

                    self._antialiaseds, self._urls,

                    "screen", hatchcolors=self.get_hatchcolor()

                )

            except TypeError:

                                                                            

                                                                  

                                                                  

                hatchcolors_arg_supported = False



                                                                     

                                                                   

                                                        

            hatchcolors_not_needed = (self.get_hatch() is None or

                                      self._original_hatchcolor is None)



            if self._gapcolor is not None:

                                                   

                ipaths, ilinestyles = self._get_inverse_paths_linestyles()

                args = [offsets, offset_trf, [mcolors.to_rgba("none")], self._gapcolor,

                        self._linewidths, ilinestyles, self._antialiaseds, self._urls,

                        "screen"]



                if hatchcolors_arg_supported:

                    renderer.draw_path_collection(gc, transform.frozen(), ipaths,

                                                  self.get_transforms(), *args,

                                                  hatchcolors=self.get_hatchcolor())

                else:

                    if hatchcolors_not_needed:

                        renderer.draw_path_collection(gc, transform.frozen(), ipaths,

                                                      self.get_transforms(), *args)

                    else:

                        path_ids = renderer._iter_collection_raw_paths(

                            transform.frozen(), ipaths, self.get_transforms())

                        for xo, yo, path_id, gc0, rgbFace in renderer._iter_collection(

                            gc, list(path_ids), *args,

                            hatchcolors=self.get_hatchcolor(),

                        ):

                            path, transform = path_id

                            if xo != 0 or yo != 0:

                                transform = transform.frozen()

                                transform.translate(xo, yo)

                            renderer.draw_path(gc0, path, transform, rgbFace)



            args = [offsets, offset_trf, self.get_facecolor(), self.get_edgecolor(),

                    self._linewidths, self._linestyles, self._antialiaseds, self._urls,

                    "screen"]



            if hatchcolors_arg_supported:

                renderer.draw_path_collection(gc, transform.frozen(), paths,

                                              self.get_transforms(), *args,

                                              hatchcolors=self.get_hatchcolor())

            else:

                if hatchcolors_not_needed:

                    renderer.draw_path_collection(gc, transform.frozen(), paths,

                                                  self.get_transforms(), *args)

                else:

                    path_ids = renderer._iter_collection_raw_paths(

                        transform.frozen(), paths, self.get_transforms())

                    for xo, yo, path_id, gc0, rgbFace in renderer._iter_collection(

                        gc, list(path_ids), *args, hatchcolors=self.get_hatchcolor(),

                    ):

                        path, transform = path_id

                        if xo != 0 or yo != 0:

                            transform = transform.frozen()

                            transform.translate(xo, yo)

                        renderer.draw_path(gc0, path, transform, rgbFace)



        gc.restore()

        renderer.close_group(self.__class__.__name__)

        self.stale = False



    def set_pickradius(self, pickradius):

        

        if not isinstance(pickradius, Real):

            raise ValueError(

                f"pickradius must be a real-valued number, not {pickradius!r}")

        self._pickradius = pickradius



    def get_pickradius(self):

        return self._pickradius



    def contains(self, mouseevent):

        

        if self._different_canvas(mouseevent) or not self.get_visible():

            return False, {}

        pickradius = (

            float(self._picker)

            if isinstance(self._picker, Number) and

               self._picker is not True                                   

            else self._pickradius)

        if self.axes:

            self.axes._unstale_viewLim()

        transform, offset_trf, offsets, paths = self._prepare_points()

                                                                       

                                                                           

                                                                           

                                                                              

                                                       

        ind = _path.point_in_path_collection(

            mouseevent.x, mouseevent.y, pickradius,

            transform.frozen(), paths, self.get_transforms(),

            offsets, offset_trf, pickradius <= 0)

        return len(ind) > 0, dict(ind=ind)



    def set_urls(self, urls):

        

        self._urls = urls if urls is not None else [None]

        self.stale = True



    def get_urls(self):

        

        return self._urls



    def set_hatch(self, hatch):

        

                                                     

        mhatch._validate_hatch_pattern(hatch)

        self._hatch = hatch

        self.stale = True



    def get_hatch(self):

        

        return self._hatch



    def set_hatch_linewidth(self, lw):

        

        self._hatch_linewidth = lw



    def get_hatch_linewidth(self):

        

        return self._hatch_linewidth



    def set_offsets(self, offsets):

        

        offsets = np.asanyarray(offsets)

        if offsets.shape == (2,):                                              

            offsets = offsets[None, :]

        cstack = (np.ma.column_stack if isinstance(offsets, np.ma.MaskedArray)

                  else np.column_stack)

        self._offsets = cstack(

            (np.asanyarray(self.convert_xunits(offsets[:, 0]), float),

             np.asanyarray(self.convert_yunits(offsets[:, 1]), float)))

        self.stale = True



    def get_offsets(self):

        

                                                       

        return np.zeros((1, 2)) if self._offsets is None else self._offsets



    def _get_default_linewidth(self):

                                               

        return mpl.rcParams['patch.linewidth']                      



    def set_linewidth(self, lw):

        

        if lw is None:

            lw = self._get_default_linewidth()

                                        

        self._us_lw = np.atleast_1d(lw)



                                         

        self._linewidths, self._linestyles = self._bcast_lwls(

            self._us_lw, self._us_linestyles)

        self.stale = True



    def set_linestyle(self, ls):

        

                                                      

        self._us_linestyles = mlines._get_dash_patterns(ls)



                                                      

        self._linewidths, self._linestyles = self._bcast_lwls(

            self._us_lw, self._us_linestyles)



    @_docstring.interpd

    def set_capstyle(self, cs):

        

        self._capstyle = CapStyle(cs)



    @_docstring.interpd

    def get_capstyle(self):

        

        return self._capstyle.name if self._capstyle else None



    @_docstring.interpd

    def set_joinstyle(self, js):

        

        self._joinstyle = JoinStyle(js)



    @_docstring.interpd

    def get_joinstyle(self):

        

        return self._joinstyle.name if self._joinstyle else None



    @staticmethod

    def _bcast_lwls(linewidths, dashes):

        

        if mpl.rcParams['_internal.classic_mode']:

            return linewidths, dashes

                                                               

        if len(dashes) != len(linewidths):

            l_dashes = len(dashes)

            l_lw = len(linewidths)

            gcd = math.gcd(l_dashes, l_lw)

            dashes = list(dashes) * (l_lw // gcd)

            linewidths = list(linewidths) * (l_dashes // gcd)



                                 

        dashes = [mlines._scale_dashes(o, d, lw)

                  for (o, d), lw in zip(dashes, linewidths)]



        return linewidths, dashes



    def get_antialiased(self):

        

        return self._antialiaseds



    def set_antialiased(self, aa):

        

        if aa is None:

            aa = self._get_default_antialiased()

        self._antialiaseds = np.atleast_1d(np.asarray(aa, bool))

        self.stale = True



    def _get_default_antialiased(self):

                                               

        return mpl.rcParams['patch.antialiased']



    def set_color(self, c):

        

        self.set_facecolor(c)

        self.set_edgecolor(c)

        self.set_hatchcolor(c)



    def _get_default_facecolor(self):

                                               

        return mpl.rcParams['patch.facecolor']



    def _set_facecolor(self, c):

        if c is None:

            c = self._get_default_facecolor()



        self._facecolors = mcolors.to_rgba_array(c, self._alpha)

        self.stale = True



    def set_facecolor(self, c):

        

        if isinstance(c, str) and c.lower() in ("none", "face"):

            c = c.lower()

        self._original_facecolor = c

        self._set_facecolor(c)



    def get_facecolor(self):

        return self._facecolors



    def get_edgecolor(self):

        if cbook._str_equal(self._edgecolors, 'face'):

            return self.get_facecolor()

        else:

            return self._edgecolors



    def _get_default_edgecolor(self):

                                               

        return mpl.rcParams['patch.edgecolor']



    def get_hatchcolor(self):

        if cbook._str_equal(self._hatchcolors, 'edge'):

            if len(self.get_edgecolor()) == 0:

                return mpl.colors.to_rgba_array(self._get_default_edgecolor(),

                                                self._alpha)

            return self.get_edgecolor()

        return self._hatchcolors



    def _set_edgecolor(self, c):

        if c is None:

            if (mpl.rcParams['patch.force_edgecolor']

                    or self._edge_default

                    or cbook._str_equal(self._original_facecolor, 'none')):

                c = self._get_default_edgecolor()

            else:

                c = 'none'

        if cbook._str_lower_equal(c, 'face'):

            self._edgecolors = 'face'

            self.stale = True

            return

        self._edgecolors = mcolors.to_rgba_array(c, self._alpha)

        self.stale = True



    def set_edgecolor(self, c):

        

                                                                    

                                                                     

                              

        if isinstance(c, str) and c.lower() in ("none", "face"):

            c = c.lower()

        self._original_edgecolor = c

        self._set_edgecolor(c)



    def _set_hatchcolor(self, c):

        c = mpl._val_or_rc(c, 'hatch.color')

        if cbook._str_equal(c, 'edge'):

            self._hatchcolors = 'edge'

        else:

            self._hatchcolors = mcolors.to_rgba_array(c, self._alpha)

        self.stale = True



    def set_hatchcolor(self, c):

        

        self._original_hatchcolor = c

        self._set_hatchcolor(c)



    def set_alpha(self, alpha):

        

        artist.Artist._set_alpha_for_array(self, alpha)

        self._set_facecolor(self._original_facecolor)

        self._set_edgecolor(self._original_edgecolor)

        self._set_hatchcolor(self._original_hatchcolor)



    set_alpha.__doc__ = artist.Artist._set_alpha_for_array.__doc__



    def get_linewidth(self):

        return self._linewidths



    def get_linestyle(self):

        return self._linestyles



    def _set_mappable_flags(self):

        

                                                                       

                                      

        edge0 = self._edge_is_mapped

        face0 = self._face_is_mapped

                                                                

        self._edge_is_mapped = False

        self._face_is_mapped = False

        if self._A is not None:

            if not cbook._str_equal(self._original_facecolor, 'none'):

                self._face_is_mapped = True

                if cbook._str_equal(self._original_edgecolor, 'face'):

                    self._edge_is_mapped = True

            else:

                if self._original_edgecolor is None:

                    self._edge_is_mapped = True



        mapped = self._face_is_mapped or self._edge_is_mapped

        changed = (edge0 is None or face0 is None

                   or self._edge_is_mapped != edge0

                   or self._face_is_mapped != face0)

        return mapped or changed



    def update_scalarmappable(self):

        

        if not self._set_mappable_flags():

            return

                                                           

        if self._A is not None:

                                                                           

            if self._A.ndim > 1 and not isinstance(self, _MeshData):

                raise ValueError('Collections can only map rank 1 arrays')

            if np.iterable(self._alpha):

                if self._alpha.size != self._A.size:

                    raise ValueError(

                        f'Data array shape, {self._A.shape} '

                        'is incompatible with alpha array shape, '

                        f'{self._alpha.shape}. '

                        'This can occur with the deprecated '

                        'behavior of the "flat" shading option, '

                        'in which a row and/or column of the data '

                        'array is dropped.')

                                                                    

                self._alpha = self._alpha.reshape(self._A.shape)

            self._mapped_colors = self.to_rgba(self._A, self._alpha)



        if self._face_is_mapped:

            self._facecolors = self._mapped_colors

        else:

            self._set_facecolor(self._original_facecolor)

        if self._edge_is_mapped:

            self._edgecolors = self._mapped_colors

        else:

            self._set_edgecolor(self._original_edgecolor)

        self.stale = True



    def get_fill(self):

        

        return not cbook._str_lower_equal(self._original_facecolor, "none")



    def update_from(self, other):

        



        artist.Artist.update_from(self, other)

        self._antialiaseds = other._antialiaseds

        self._mapped_colors = other._mapped_colors

        self._edge_is_mapped = other._edge_is_mapped

        self._original_edgecolor = other._original_edgecolor

        self._edgecolors = other._edgecolors

        self._face_is_mapped = other._face_is_mapped

        self._original_facecolor = other._original_facecolor

        self._facecolors = other._facecolors

        self._linewidths = other._linewidths

        self._linestyles = other._linestyles

        self._us_linestyles = other._us_linestyles

        self._pickradius = other._pickradius

        self._hatch = other._hatch

        self._hatchcolors = other._hatchcolors



                                        

        self._A = other._A

        self.norm = other.norm

        self.cmap = other.cmap

        self.stale = True





class _CollectionWithSizes(Collection):

    

    _factor = 1.0



    def get_sizes(self):

        

        return self._sizes



    def set_sizes(self, sizes, dpi=72.0):

        

        if sizes is None:

            self._sizes = np.array([])

            self._transforms = np.empty((0, 3, 3))

        else:

            self._sizes = np.asarray(sizes)

            self._transforms = np.zeros((len(self._sizes), 3, 3))

            scale = np.sqrt(self._sizes) * dpi / 72.0 * self._factor

            self._transforms[:, 0, 0] = scale

            self._transforms[:, 1, 1] = scale

            self._transforms[:, 2, 2] = 1.0

        self.stale = True



    @artist.allow_rasterization

    def draw(self, renderer):

        self.set_sizes(self._sizes, self.get_figure(root=True).dpi)

        super().draw(renderer)





class PathCollection(_CollectionWithSizes):

    



    def __init__(self, paths, sizes=None, **kwargs):

        



        super().__init__(**kwargs)

        self.set_paths(paths)

        self.set_sizes(sizes)

        self.stale = True



    def get_paths(self):

        return self._paths



    def legend_elements(self, prop="colors", num="auto",

                        fmt=None, func=lambda x: x, **kwargs):

        

        handles = []

        labels = []

        hasarray = self.get_array() is not None

        if fmt is None:

            fmt = mpl.ticker.ScalarFormatter(useOffset=False, useMathText=True)

        elif isinstance(fmt, str):

            fmt = mpl.ticker.StrMethodFormatter(fmt)

        fmt.create_dummy_axis()



        if prop == "colors":

            if not hasarray:

                warnings.warn("Collection without array used. Make sure to "

                              "specify the values to be colormapped via the "

                              "`c` argument.")

                return handles, labels

            u = np.unique(self.get_array())

            size = kwargs.pop("size", mpl.rcParams["lines.markersize"])

        elif prop == "sizes":

            u = np.unique(self.get_sizes())

            color = kwargs.pop("color", "k")

        else:

            raise ValueError("Valid values for `prop` are 'colors' or "

                             f"'sizes'. You supplied '{prop}' instead.")



        fu = func(u)

        fmt.axis.set_view_interval(fu.min(), fu.max())

        fmt.axis.set_data_interval(fu.min(), fu.max())

        if num == "auto":

            num = 9

            if len(u) <= num:

                num = None

        if num is None:

            values = u

            label_values = func(values)

        else:

            if prop == "colors":

                arr = self.get_array()

            elif prop == "sizes":

                arr = self.get_sizes()

            if isinstance(num, mpl.ticker.Locator):

                loc = num

            elif np.iterable(num):

                loc = mpl.ticker.FixedLocator(num)

            else:

                num = int(num)

                loc = mpl.ticker.MaxNLocator(nbins=num, min_n_ticks=num-1,

                                             steps=[1, 2, 2.5, 3, 5, 6, 8, 10])

            label_values = loc.tick_values(func(arr).min(), func(arr).max())

            cond = ((label_values >= func(arr).min()) &

                    (label_values <= func(arr).max()))

            label_values = label_values[cond]

            yarr = np.linspace(arr.min(), arr.max(), 256)

            xarr = func(yarr)

            ix = np.argsort(xarr)

            values = np.interp(label_values, xarr[ix], yarr[ix])



        kw = {"markeredgewidth": self.get_linewidths()[0],

              "alpha": self.get_alpha(),

              **kwargs}



        for val, lab in zip(values, label_values):

            if prop == "colors":

                color = self.cmap(self.norm(val))

            elif prop == "sizes":

                size = np.sqrt(val)

                if np.isclose(size, 0.0):

                    continue

            h = mlines.Line2D([0], [0], ls="", color=color, ms=size,

                              marker=self.get_paths()[0], **kw)

            handles.append(h)

            if hasattr(fmt, "set_locs"):

                fmt.set_locs(label_values)

            l = fmt(lab)

            labels.append(l)



        return handles, labels





class PolyCollection(_CollectionWithSizes):



    def __init__(self, verts, sizes=None, *, closed=True, **kwargs):

        

        super().__init__(**kwargs)

        self.set_sizes(sizes)

        self.set_verts(verts, closed)

        self.stale = True



    def set_verts(self, verts, closed=True):

        

        self.stale = True

        if isinstance(verts, np.ma.MaskedArray):

            verts = verts.astype(float).filled(np.nan)



                                                                

        if not closed:

            self._paths = [mpath.Path(xy) for xy in verts]

            return



                              

        if isinstance(verts, np.ndarray) and len(verts.shape) == 3 and verts.size:

            verts_pad = np.concatenate((verts, verts[:, :1]), axis=1)

                                                                          

                                           

            template_path = mpath.Path(verts_pad[0], closed=True)

            codes = template_path.codes

            _make_path = mpath.Path._fast_from_codes_and_verts

            self._paths = [_make_path(xy, codes, internals_from=template_path)

                           for xy in verts_pad]

            return



        self._paths = []

        for xy in verts:

            if len(xy):

                self._paths.append(mpath.Path._create_closed(xy))

            else:

                self._paths.append(mpath.Path(xy))



    set_paths = set_verts



    def set_verts_and_codes(self, verts, codes):

        

        if len(verts) != len(codes):

            raise ValueError("'codes' must be a 1D list or array "

                             "with the same length of 'verts'")

        self._paths = [mpath.Path(xy, cds) if len(xy) else mpath.Path(xy)

                       for xy, cds in zip(verts, codes)]

        self.stale = True





class FillBetweenPolyCollection(PolyCollection):

    

    def __init__(

            self, t_direction, t, f1, f2, *,

            where=None, interpolate=False, step=None, **kwargs):

        

        self.t_direction = t_direction

        self._interpolate = interpolate

        self._step = step

        verts = self._make_verts(t, f1, f2, where)

        super().__init__(verts, **kwargs)



    @staticmethod

    def _f_dir_from_t(t_direction):

        

        if t_direction == "x":

            return "y"

        elif t_direction == "y":

            return "x"

        else:

            msg = f"t_direction must be 'x' or 'y', got {t_direction!r}"

            raise ValueError(msg)



    @property

    def _f_direction(self):

        

        return self._f_dir_from_t(self.t_direction)



    def set_data(self, t, f1, f2, *, where=None):

        

        t, f1, f2 = self.axes._fill_between_process_units(

            self.t_direction, self._f_direction, t, f1, f2)



        verts = self._make_verts(t, f1, f2, where)

        self.set_verts(verts)



    def get_datalim(self, transData):

        

        datalim = transforms.Bbox.null()

        datalim.update_from_data_xy((self.get_transform() - transData).transform(

            np.concatenate([self._bbox, [self._bbox.minpos]])))

        return datalim



    def _make_verts(self, t, f1, f2, where):

        

        self._validate_shapes(self.t_direction, self._f_direction, t, f1, f2)



        where = self._get_data_mask(t, f1, f2, where)

        t, f1, f2 = np.broadcast_arrays(np.atleast_1d(t), f1, f2, subok=True)



        self._bbox = transforms.Bbox.null()

        self._bbox.update_from_data_xy(self._fix_pts_xy_order(np.concatenate([

            np.stack((t[where], f[where]), axis=-1) for f in (f1, f2)])))



        return [

            self._make_verts_for_region(t, f1, f2, idx0, idx1)

            for idx0, idx1 in cbook.contiguous_regions(where)

        ]



    def _get_data_mask(self, t, f1, f2, where):

        

        if where is None:

            where = True

        else:

            where = np.asarray(where, dtype=bool)

            if where.size != t.size:

                msg = "where size ({}) does not match {!r} size ({})".format(

                    where.size, self.t_direction, t.size)

                raise ValueError(msg)

        return where & ~functools.reduce(

            np.logical_or, map(np.ma.getmaskarray, [t, f1, f2]))



    @staticmethod

    def _validate_shapes(t_dir, f_dir, t, f1, f2):

        

        names = (d + s for d, s in zip((t_dir, f_dir, f_dir), ("", "1", "2")))

        for name, array in zip(names, [t, f1, f2]):

            if array.ndim > 1:

                raise ValueError(f"{name!r} is not 1-dimensional")

            if t.size > 1 and array.size > 1 and t.size != array.size:

                msg = "{!r} has size {}, but {!r} has an unequal size of {}".format(

                    t_dir, t.size, name, array.size)

                raise ValueError(msg)



    def _make_verts_for_region(self, t, f1, f2, idx0, idx1):

        

        t_slice = t[idx0:idx1]

        f1_slice = f1[idx0:idx1]

        f2_slice = f2[idx0:idx1]

        if self._step is not None:

            step_func = cbook.STEP_LOOKUP_MAP["steps-" + self._step]

            t_slice, f1_slice, f2_slice = step_func(t_slice, f1_slice, f2_slice)



        if self._interpolate:

            start = self._get_interpolating_points(t, f1, f2, idx0)

            end = self._get_interpolating_points(t, f1, f2, idx1)

        else:

                                                               

                                                                          

            start = t_slice[0], f2_slice[0]

            end = t_slice[-1], f2_slice[-1]



        pts = np.concatenate((

            np.asarray([start]),

            np.stack((t_slice, f1_slice), axis=-1),

            np.asarray([end]),

            np.stack((t_slice, f2_slice), axis=-1)[::-1]))



        return self._fix_pts_xy_order(pts)



    @classmethod

    def _get_interpolating_points(cls, t, f1, f2, idx):

        

        im1 = max(idx - 1, 0)

        t_values = t[im1:idx+1]

        diff_values = f1[im1:idx+1] - f2[im1:idx+1]

        f1_values = f1[im1:idx+1]



        if len(diff_values) == 2:

            if np.ma.is_masked(diff_values[1]):

                return t[im1], f1[im1]

            elif np.ma.is_masked(diff_values[0]):

                return t[idx], f1[idx]



        diff_root_t = cls._get_diff_root(0, diff_values, t_values)

        diff_root_f = cls._get_diff_root(diff_root_t, t_values, f1_values)

        return diff_root_t, diff_root_f



    @staticmethod

    def _get_diff_root(x, xp, fp):

        

        order = xp.argsort()

        return np.interp(x, xp[order], fp[order])



    def _fix_pts_xy_order(self, pts):

        

        return pts[:, ::-1] if self.t_direction == "y" else pts





class RegularPolyCollection(_CollectionWithSizes):

    



    _path_generator = mpath.Path.unit_regular_polygon

    _factor = np.pi ** (-1/2)



    def __init__(self,

                 numsides,

                 *,

                 rotation=0,

                 sizes=(1,),

                 **kwargs):

        

        super().__init__(**kwargs)

        self.set_sizes(sizes)

        self._numsides = numsides

        self._paths = [self._path_generator(numsides)]

        self._rotation = rotation

        self.set_transform(transforms.IdentityTransform())



    def get_numsides(self):

        return self._numsides



    def get_rotation(self):

        return self._rotation



    @artist.allow_rasterization

    def draw(self, renderer):

        self.set_sizes(self._sizes, self.get_figure(root=True).dpi)

        self._transforms = [

            transforms.Affine2D(x).rotate(-self._rotation).get_matrix()

            for x in self._transforms

        ]

                                                                              

                                    

        Collection.draw(self, renderer)





class StarPolygonCollection(RegularPolyCollection):

    

    _path_generator = mpath.Path.unit_regular_star





class AsteriskPolygonCollection(RegularPolyCollection):

    

    _path_generator = mpath.Path.unit_regular_asterisk





class LineCollection(Collection):

    



    _edge_default = True



    def __init__(self, segments,                

                 *,

                 zorder=2,                                

                 **kwargs

                 ):

        

                                                                             

        kwargs.setdefault('facecolors', 'none')

        super().__init__(

            zorder=zorder,

            **kwargs)

        self.set_segments(segments)



    def set_segments(self, segments):

        if segments is None:

            return



        self._paths = [mpath.Path(seg) if isinstance(seg, np.ma.MaskedArray)

                       else mpath.Path(np.asarray(seg, float))

                       for seg in segments]

        self.stale = True



    set_verts = set_segments                                         

    set_paths = set_segments



    def get_segments(self):

        

        segments = []



        for path in self._paths:

            vertices = [

                vertex

                for vertex, _

                                                                           

                                                                             

                                         

                in path.iter_segments(simplify=False)

            ]

            vertices = np.asarray(vertices)

            segments.append(vertices)



        return segments



    def _get_default_linewidth(self):

        return mpl.rcParams['lines.linewidth']



    def _get_default_antialiased(self):

        return mpl.rcParams['lines.antialiased']



    def _get_default_edgecolor(self):

        return mpl.rcParams['lines.color']



    def _get_default_facecolor(self):

        return 'none'



    def set_alpha(self, alpha):

                             

        super().set_alpha(alpha)

        if self._gapcolor is not None:

            self.set_gapcolor(self._original_gapcolor)



    def set_color(self, c):

        

        self.set_edgecolor(c)



    set_colors = set_color



    def get_color(self):

        return self._edgecolors



    get_colors = get_color                                       



    def set_gapcolor(self, gapcolor):

        

        self._original_gapcolor = gapcolor

        self._set_gapcolor(gapcolor)



    def _set_gapcolor(self, gapcolor):

        if gapcolor is not None:

            gapcolor = mcolors.to_rgba_array(gapcolor, self._alpha)

        self._gapcolor = gapcolor

        self.stale = True



    def get_gapcolor(self):

        return self._gapcolor



    def _get_inverse_paths_linestyles(self):

        

        path_patterns = [

            (mpath.Path(np.full((1, 2), np.nan)), ls)

            if ls == (0, None) else

            (path, mlines._get_inverse_dash_pattern(*ls))

            for (path, ls) in

            zip(self._paths, itertools.cycle(self._linestyles))]



        return zip(*path_patterns)





class EventCollection(LineCollection):

    



    _edge_default = True



    def __init__(self,

                 positions,                   

                 orientation='horizontal',

                 *,

                 lineoffset=0,

                 linelength=1,

                 linewidth=None,

                 color=None,

                 linestyle='solid',

                 antialiased=None,

                 **kwargs

                 ):

        

        super().__init__([],

                         linewidths=linewidth, linestyles=linestyle,

                         colors=color, antialiaseds=antialiased,

                         **kwargs)

        self._is_horizontal = True                                         

        self._linelength = linelength

        self._lineoffset = lineoffset

        self.set_orientation(orientation)

        self.set_positions(positions)



    def get_positions(self):

        

        pos = 0 if self.is_horizontal() else 1

        return [segment[0, pos] for segment in self.get_segments()]



    def set_positions(self, positions):

        

        if positions is None:

            positions = []

        if np.ndim(positions) != 1:

            raise ValueError('positions must be one-dimensional')

        lineoffset = self.get_lineoffset()

        linelength = self.get_linelength()

        pos_idx = 0 if self.is_horizontal() else 1

        segments = np.empty((len(positions), 2, 2))

        segments[:, :, pos_idx] = np.sort(positions)[:, None]

        segments[:, 0, 1 - pos_idx] = lineoffset + linelength / 2

        segments[:, 1, 1 - pos_idx] = lineoffset - linelength / 2

        self.set_segments(segments)



    def add_positions(self, position):

        

        if position is None or (hasattr(position, 'len') and

                                len(position) == 0):

            return

        positions = self.get_positions()

        positions = np.hstack([positions, np.asanyarray(position)])

        self.set_positions(positions)

    extend_positions = append_positions = add_positions



    def is_horizontal(self):

        

        return self._is_horizontal



    def get_orientation(self):

        

        return 'horizontal' if self.is_horizontal() else 'vertical'



    def switch_orientation(self):

        

        segments = self.get_segments()

        for i, segment in enumerate(segments):

            segments[i] = np.fliplr(segment)

        self.set_segments(segments)

        self._is_horizontal = not self.is_horizontal()

        self.stale = True



    def set_orientation(self, orientation):

        

        is_horizontal = _api.check_getitem(

            {"horizontal": True, "vertical": False},

            orientation=orientation)

        if is_horizontal == self.is_horizontal():

            return

        self.switch_orientation()



    def get_linelength(self):

        

        return self._linelength



    def set_linelength(self, linelength):

        

        if linelength == self.get_linelength():

            return

        lineoffset = self.get_lineoffset()

        segments = self.get_segments()

        pos = 1 if self.is_horizontal() else 0

        for segment in segments:

            segment[0, pos] = lineoffset + linelength / 2.

            segment[1, pos] = lineoffset - linelength / 2.

        self.set_segments(segments)

        self._linelength = linelength



    def get_lineoffset(self):

        

        return self._lineoffset



    def set_lineoffset(self, lineoffset):

        

        if lineoffset == self.get_lineoffset():

            return

        linelength = self.get_linelength()

        segments = self.get_segments()

        pos = 1 if self.is_horizontal() else 0

        for segment in segments:

            segment[0, pos] = lineoffset + linelength / 2.

            segment[1, pos] = lineoffset - linelength / 2.

        self.set_segments(segments)

        self._lineoffset = lineoffset



    def get_linewidth(self):

        

        return super().get_linewidth()[0]



    def get_linewidths(self):

        return super().get_linewidth()



    def get_color(self):

        

        return self.get_colors()[0]





class CircleCollection(_CollectionWithSizes):

    



    _factor = np.pi ** (-1/2)



    def __init__(self, sizes, **kwargs):

        

        super().__init__(**kwargs)

        self.set_sizes(sizes)

        self.set_transform(transforms.IdentityTransform())

        self._paths = [mpath.Path.unit_circle()]





class EllipseCollection(Collection):

    



    def __init__(self, widths, heights, angles, *, units='points', **kwargs):

        

        super().__init__(**kwargs)

        self.set_widths(widths)

        self.set_heights(heights)

        self.set_angles(angles)

        self._units = units

        self.set_transform(transforms.IdentityTransform())

        self._transforms = np.empty((0, 3, 3))

        self._paths = [mpath.Path.unit_circle()]



    def _set_transforms(self):

        



        ax = self.axes

        fig = self.get_figure(root=False)



        if self._units == 'xy':

            sc = 1

        elif self._units == 'x':

            sc = ax.bbox.width / ax.viewLim.width

        elif self._units == 'y':

            sc = ax.bbox.height / ax.viewLim.height

        elif self._units == 'inches':

            sc = fig.dpi

        elif self._units == 'points':

            sc = fig.dpi / 72.0

        elif self._units == 'width':

            sc = ax.bbox.width

        elif self._units == 'height':

            sc = ax.bbox.height

        elif self._units == 'dots':

            sc = 1.0

        else:

            raise ValueError(f'Unrecognized units: {self._units!r}')



        self._transforms = np.zeros((len(self._widths), 3, 3))

        widths = self._widths * sc

        heights = self._heights * sc

        sin_angle = np.sin(self._angles)

        cos_angle = np.cos(self._angles)

        self._transforms[:, 0, 0] = widths * cos_angle

        self._transforms[:, 0, 1] = heights * -sin_angle

        self._transforms[:, 1, 0] = widths * sin_angle

        self._transforms[:, 1, 1] = heights * cos_angle

        self._transforms[:, 2, 2] = 1.0



        _affine = transforms.Affine2D

        if self._units == 'xy':

            m = ax.transData.get_affine().get_matrix().copy()

            m[:2, 2:] = 0

            self.set_transform(_affine(m))



    def set_widths(self, widths):

        

        self._widths = 0.5 * np.asarray(widths).ravel()

        self.stale = True



    def set_heights(self, heights):

        

        self._heights = 0.5 * np.asarray(heights).ravel()

        self.stale = True



    def set_angles(self, angles):

        

        self._angles = np.deg2rad(angles).ravel()

        self.stale = True



    def get_widths(self):

        

        return self._widths * 2



    def get_heights(self):

        

        return self._heights * 2



    def get_angles(self):

        

        return np.rad2deg(self._angles)



    @artist.allow_rasterization

    def draw(self, renderer):

        self._set_transforms()

        super().draw(renderer)





class PatchCollection(Collection):

    



    def __init__(self, patches, *, match_original=False, **kwargs):

        



        if match_original:

            def determine_facecolor(patch):

                if patch.get_fill():

                    return patch.get_facecolor()

                return [0, 0, 0, 0]



            kwargs['facecolors'] = [determine_facecolor(p) for p in patches]

            kwargs['edgecolors'] = [p.get_edgecolor() for p in patches]

            kwargs['linewidths'] = [p.get_linewidth() for p in patches]

            kwargs['linestyles'] = [p.get_linestyle() for p in patches]

            kwargs['antialiaseds'] = [p.get_antialiased() for p in patches]



        super().__init__(**kwargs)



        self.set_paths(patches)



    def set_paths(self, patches):

        paths = [p.get_transform().transform_path(p.get_path())

                 for p in patches]

        self._paths = paths





class TriMesh(Collection):

    

    def __init__(self, triangulation, **kwargs):

        super().__init__(**kwargs)

        self._triangulation = triangulation

        self._shading = 'gouraud'



        self._bbox = transforms.Bbox.unit()



                                                                  

                        

        xy = np.hstack((triangulation.x.reshape(-1, 1),

                        triangulation.y.reshape(-1, 1)))

        self._bbox.update_from_data_xy(xy)



    def get_paths(self):

        if self._paths is None:

            self.set_paths()

        return self._paths



    def set_paths(self):

        self._paths = self.convert_mesh_to_paths(self._triangulation)



    @staticmethod

    def convert_mesh_to_paths(tri):

        

        triangles = tri.get_masked_triangles()

        verts = np.stack((tri.x[triangles], tri.y[triangles]), axis=-1)

        return [mpath.Path(x) for x in verts]



    @artist.allow_rasterization

    def draw(self, renderer):

        if not self.get_visible():

            return

        renderer.open_group(self.__class__.__name__, gid=self.get_gid())

        transform = self.get_transform()



                                                               

        tri = self._triangulation

        triangles = tri.get_masked_triangles()



        verts = np.stack((tri.x[triangles], tri.y[triangles]), axis=-1)



        self.update_scalarmappable()

        colors = self._facecolors[triangles]



        gc = renderer.new_gc()

        self._set_gc_clip(gc)

        gc.set_linewidth(self.get_linewidth()[0])

        renderer.draw_gouraud_triangles(gc, verts, colors, transform.frozen())

        gc.restore()

        renderer.close_group(self.__class__.__name__)





class _MeshData:

    

    def __init__(self, coordinates, *, shading='flat'):

        _api.check_shape((None, None, 2), coordinates=coordinates)

        self._coordinates = coordinates

        self._shading = shading



    def set_array(self, A):

        

        height, width = self._coordinates.shape[0:-1]

        if self._shading == 'flat':

            h, w = height - 1, width - 1

        else:

            h, w = height, width

        ok_shapes = [(h, w, 3), (h, w, 4), (h, w), (h * w,)]

        if A is not None:

            shape = np.shape(A)

            if shape not in ok_shapes:

                raise ValueError(

                    f"For X ({width}) and Y ({height}) with {self._shading} "

                    f"shading, A should have shape "

                    f"{' or '.join(map(str, ok_shapes))}, not {A.shape}")

        return super().set_array(A)



    def get_coordinates(self):

        

        return self._coordinates



    def get_edgecolor(self):

                             

                                                                

                                     

        return super().get_edgecolor().reshape(-1, 4)



    def get_facecolor(self):

                             

                                                                

                                     

        return super().get_facecolor().reshape(-1, 4)



    @staticmethod

    def _convert_mesh_to_paths(coordinates):

        

        if isinstance(coordinates, np.ma.MaskedArray):

            c = coordinates.data

        else:

            c = coordinates

        points = np.concatenate([

            c[:-1, :-1],

            c[:-1, 1:],

            c[1:, 1:],

            c[1:, :-1],

            c[:-1, :-1]

        ], axis=2).reshape((-1, 5, 2))

        return [mpath.Path(x) for x in points]



    def _convert_mesh_to_triangles(self, coordinates):

        

        if isinstance(coordinates, np.ma.MaskedArray):

            p = coordinates.data

        else:

            p = coordinates



        p_a = p[:-1, :-1]

        p_b = p[:-1, 1:]

        p_c = p[1:, 1:]

        p_d = p[1:, :-1]

        p_center = (p_a + p_b + p_c + p_d) / 4.0

        triangles = np.concatenate([

            p_a, p_b, p_center,

            p_b, p_c, p_center,

            p_c, p_d, p_center,

            p_d, p_a, p_center,

        ], axis=2).reshape((-1, 3, 2))



        c = self.get_facecolor().reshape((*coordinates.shape[:2], 4))

        z = self.get_array()

        mask = z.mask if np.ma.is_masked(z) else None

        if mask is not None:

            c[mask, 3] = np.nan

        c_a = c[:-1, :-1]

        c_b = c[:-1, 1:]

        c_c = c[1:, 1:]

        c_d = c[1:, :-1]

        c_center = (c_a + c_b + c_c + c_d) / 4.0

        colors = np.concatenate([

            c_a, c_b, c_center,

            c_b, c_c, c_center,

            c_c, c_d, c_center,

            c_d, c_a, c_center,

        ], axis=2).reshape((-1, 3, 4))

        tmask = np.isnan(colors[..., 2, 3])

        return triangles[~tmask], colors[~tmask]





class QuadMesh(_MeshData, Collection):

    



    def __init__(self, coordinates, *, antialiased=True, shading='flat',

                 **kwargs):

        kwargs.setdefault("pickradius", 0)

        super().__init__(coordinates=coordinates, shading=shading)

        Collection.__init__(self, **kwargs)



        self._antialiased = antialiased

        self._bbox = transforms.Bbox.unit()

        self._bbox.update_from_data_xy(self._coordinates.reshape(-1, 2))

        self.set_mouseover(False)



    def get_paths(self):

        if self._paths is None:

            self.set_paths()

        return self._paths



    def set_paths(self):

        self._paths = self._convert_mesh_to_paths(self._coordinates)

        self.stale = True



    def get_datalim(self, transData):

        return (self.get_transform() - transData).transform_bbox(self._bbox)



    @artist.allow_rasterization

    def draw(self, renderer):

        if not self.get_visible():

            return

        renderer.open_group(self.__class__.__name__, self.get_gid())

        transform = self.get_transform()

        offset_trf = self.get_offset_transform()

        offsets = self.get_offsets()



        if self.have_units():

            xs = self.convert_xunits(offsets[:, 0])

            ys = self.convert_yunits(offsets[:, 1])

            offsets = np.column_stack([xs, ys])



        self.update_scalarmappable()



        if not transform.is_affine:

            coordinates = self._coordinates.reshape((-1, 2))

            coordinates = transform.transform(coordinates)

            coordinates = coordinates.reshape(self._coordinates.shape)

            transform = transforms.IdentityTransform()

        else:

            coordinates = self._coordinates



        if not offset_trf.is_affine:

            offsets = offset_trf.transform_non_affine(offsets)

            offset_trf = offset_trf.get_affine()



        gc = renderer.new_gc()

        gc.set_snap(self.get_snap())

        self._set_gc_clip(gc)

        gc.set_linewidth(self.get_linewidth()[0])



        if self._shading == 'gouraud':

            triangles, colors = self._convert_mesh_to_triangles(coordinates)

            renderer.draw_gouraud_triangles(

                gc, triangles, colors, transform.frozen())

        else:

            renderer.draw_quad_mesh(

                gc, transform.frozen(),

                coordinates.shape[1] - 1, coordinates.shape[0] - 1,

                coordinates, offsets, offset_trf,

                                                                              

                self.get_facecolor().reshape((-1, 4)),

                self._antialiased, self.get_edgecolors().reshape((-1, 4)))

        gc.restore()

        renderer.close_group(self.__class__.__name__)

        self.stale = False



    def get_cursor_data(self, event):

        contained, info = self.contains(event)

        if contained and self.get_array() is not None:

            return self.get_array().ravel()[info["ind"]]

        return None





class PolyQuadMesh(_MeshData, PolyCollection):

    



    def __init__(self, coordinates, **kwargs):

        super().__init__(coordinates=coordinates)

        PolyCollection.__init__(self, verts=[], **kwargs)

                                                                   

                                                                       

                                                                            

        self._set_unmasked_verts()



    def _get_unmasked_polys(self):

        

                           

        mask = np.any(np.ma.getmaskarray(self._coordinates), axis=-1)



                                                                                 

        mask = (mask[0:-1, 0:-1] | mask[1:, 1:] | mask[0:-1, 1:] | mask[1:, 0:-1])

        arr = self.get_array()

        if arr is not None:

            arr = np.ma.getmaskarray(arr)

            if arr.ndim == 3:

                             

                mask |= np.any(arr, axis=-1)

            elif arr.ndim == 2:

                mask |= arr

            else:

                mask |= arr.reshape(self._coordinates[:-1, :-1, :].shape[:2])

        return ~mask



    def _set_unmasked_verts(self):

        X = self._coordinates[..., 0]

        Y = self._coordinates[..., 1]



        unmask = self._get_unmasked_polys()

        X1 = np.ma.filled(X[:-1, :-1])[unmask]

        Y1 = np.ma.filled(Y[:-1, :-1])[unmask]

        X2 = np.ma.filled(X[1:, :-1])[unmask]

        Y2 = np.ma.filled(Y[1:, :-1])[unmask]

        X3 = np.ma.filled(X[1:, 1:])[unmask]

        Y3 = np.ma.filled(Y[1:, 1:])[unmask]

        X4 = np.ma.filled(X[:-1, 1:])[unmask]

        Y4 = np.ma.filled(Y[:-1, 1:])[unmask]

        npoly = len(X1)



        xy = np.ma.stack([X1, Y1, X2, Y2, X3, Y3, X4, Y4, X1, Y1], axis=-1)

        verts = xy.reshape((npoly, 5, 2))

        self.set_verts(verts)



    def get_edgecolor(self):

                             

                                                               

                          

        ec = super().get_edgecolor()

        unmasked_polys = self._get_unmasked_polys().ravel()

        if len(ec) != len(unmasked_polys):

                            

            return ec

        return ec[unmasked_polys, :]



    def get_facecolor(self):

                             

                                                               

                          

        fc = super().get_facecolor()

        unmasked_polys = self._get_unmasked_polys().ravel()

        if len(fc) != len(unmasked_polys):

                            

            return fc

        return fc[unmasked_polys, :]



    def set_array(self, A):

                             

        prev_unmask = self._get_unmasked_polys()

        super().set_array(A)

                                                          

                                              

        if not np.array_equal(prev_unmask, self._get_unmasked_polys()):

            self._set_unmasked_verts()


import numpy as np



from matplotlib import ticker as mticker, _api

from matplotlib.transforms import Bbox, Transform





def _find_line_box_crossings(xys, bbox):

    

    crossings = []

    dxys = xys[1:] - xys[:-1]

    for sl in [slice(None), slice(None, None, -1)]:

        us, vs = xys.T[sl]                               

        dus, dvs = dxys.T[sl]

        umin, vmin = bbox.min[sl]

        umax, vmax = bbox.max[sl]

        for u0, inside in [(umin, us > umin), (umax, us < umax)]:

            cross = []

            idxs, = (inside[:-1] ^ inside[1:]).nonzero()

            vv = vs[idxs] + (u0 - us[idxs]) * dvs[idxs] / dus[idxs]

            crossings.append([

                ((u0, v)[sl], np.degrees(np.arctan2(*dxy[::-1])))                   

                for v, dxy in zip(vv, dxys[idxs]) if vmin <= v <= vmax])

    return crossings





class ExtremeFinderSimple:

    



    def __init__(self, nx, ny):

        

        self.nx = nx

        self.ny = ny



    def __call__(self, transform_xy, x1, y1, x2, y2):

        

        tbbox = self._find_transformed_bbox(

            _User2DTransform(transform_xy, None), Bbox.from_extents(x1, y1, x2, y2))

        return tbbox.x0, tbbox.x1, tbbox.y0, tbbox.y1



    def _find_transformed_bbox(self, trans, bbox):

        

        grid = np.reshape(np.meshgrid(np.linspace(bbox.x0, bbox.x1, self.nx),

                                      np.linspace(bbox.y0, bbox.y1, self.ny)),

                          (2, -1)).T

        tbbox = Bbox.null()

        tbbox.update_from_data_xy(trans.transform(grid))

        return tbbox.expanded(1 + 2 / self.nx, 1 + 2 / self.ny)





class _User2DTransform(Transform):

    



    input_dims = output_dims = 2



    def __init__(self, forward, backward):

        

                                                                         

                                                                  

        super().__init__()

        self._forward = forward

        self._backward = backward



    def transform_non_affine(self, values):

                             

        return np.transpose(self._forward(*np.transpose(values)))



    def inverted(self):

                             

        return type(self)(self._backward, self._forward)





class GridFinder:

    



    def __init__(self,

                 transform,

                 extreme_finder=None,

                 grid_locator1=None,

                 grid_locator2=None,

                 tick_formatter1=None,

                 tick_formatter2=None):

        if extreme_finder is None:

            extreme_finder = ExtremeFinderSimple(20, 20)

        if grid_locator1 is None:

            grid_locator1 = MaxNLocator()

        if grid_locator2 is None:

            grid_locator2 = MaxNLocator()

        if tick_formatter1 is None:

            tick_formatter1 = FormatterPrettyPrint()

        if tick_formatter2 is None:

            tick_formatter2 = FormatterPrettyPrint()

        self.extreme_finder = extreme_finder

        self.grid_locator1 = grid_locator1

        self.grid_locator2 = grid_locator2

        self.tick_formatter1 = tick_formatter1

        self.tick_formatter2 = tick_formatter2

        self.set_transform(transform)



    def _format_ticks(self, idx, direction, factor, levels):

        

        fmt = _api.check_getitem(

            {1: self.tick_formatter1, 2: self.tick_formatter2}, idx=idx)

        return (fmt.format_ticks(levels) if isinstance(fmt, mticker.Formatter)

                else fmt(direction, factor, levels))



    def get_grid_info(self, *args, **kwargs):

        

        params = _api.select_matching_signature(

            [lambda x1, y1, x2, y2: locals(), lambda bbox: locals()], *args, **kwargs)

        if "x1" in params:

            _api.warn_deprecated("3.11", message=(

                "Passing extents as separate arguments to get_grid_info is deprecated "

                "since %(since)s and support will be removed %(removal)s; pass a "

                "single bbox instead."))

            bbox = Bbox.from_extents(

                params["x1"], params["y1"], params["x2"], params["y2"])

        else:

            bbox = params["bbox"]



        tbbox = self.extreme_finder._find_transformed_bbox(

            self.get_transform().inverted(), bbox)



        lon_levs, lon_n, lon_factor = self.grid_locator1(*tbbox.intervalx)

        lat_levs, lat_n, lat_factor = self.grid_locator2(*tbbox.intervaly)



        lon_values = np.asarray(lon_levs[:lon_n]) / lon_factor

        lat_values = np.asarray(lat_levs[:lat_n]) / lat_factor



        lon_lines, lat_lines = self._get_raw_grid_lines(lon_values, lat_values, tbbox)



        bbox_expanded = bbox.expanded(1 + 2e-10, 1 + 2e-10)

        grid_info = {"extremes": tbbox}                                   



        for idx, lon_or_lat, levs, factor, values, lines in [

                (1, "lon", lon_levs, lon_factor, lon_values, lon_lines),

                (2, "lat", lat_levs, lat_factor, lat_values, lat_lines),

        ]:

            grid_info[lon_or_lat] = gi = {

                "lines": lines,

                "ticks": {"left": [], "right": [], "bottom": [], "top": []},

            }

            for xys, v, level in zip(lines, values, levs):

                all_crossings = _find_line_box_crossings(xys, bbox_expanded)

                for side, crossings in zip(

                        ["left", "right", "bottom", "top"], all_crossings):

                    for crossing in crossings:

                        gi["ticks"][side].append({"level": level, "loc": crossing})

            for side in gi["ticks"]:

                levs = [tick["level"] for tick in gi["ticks"][side]]

                labels = self._format_ticks(idx, side, factor, levs)

                for tick, label in zip(gi["ticks"][side], labels):

                    tick["label"] = label



        return grid_info



    def _get_raw_grid_lines(self, lon_values, lat_values, bbox):

        trans = self.get_transform()

        lons = np.linspace(bbox.x0, bbox.x1, 100)                     

        lats = np.linspace(bbox.y0, bbox.y1, 100)

        lon_lines = [trans.transform(np.column_stack([np.full_like(lats, lon), lats]))

                     for lon in lon_values]

        lat_lines = [trans.transform(np.column_stack([lons, np.full_like(lons, lat)]))

                     for lat in lat_values]

        return lon_lines, lat_lines



    def set_transform(self, aux_trans):

        if isinstance(aux_trans, Transform):

            self._aux_transform = aux_trans

        elif len(aux_trans) == 2 and all(map(callable, aux_trans)):

            self._aux_transform = _User2DTransform(*aux_trans)

        else:

            raise TypeError("'aux_trans' must be either a Transform "

                            "instance or a pair of callables")



    def get_transform(self):

        return self._aux_transform



    update_transform = set_transform                     



    @_api.deprecated("3.11", alternative="grid_finder.get_transform()")

    def transform_xy(self, x, y):

        return self._aux_transform.transform(np.column_stack([x, y])).T



    @_api.deprecated("3.11", alternative="grid_finder.get_transform().inverted()")

    def inv_transform_xy(self, x, y):

        return self._aux_transform.inverted().transform(

            np.column_stack([x, y])).T



    def update(self, **kwargs):

        for k, v in kwargs.items():

            if k in ["extreme_finder",

                     "grid_locator1",

                     "grid_locator2",

                     "tick_formatter1",

                     "tick_formatter2"]:

                setattr(self, k, v)

            else:

                raise ValueError(f"Unknown update property {k!r}")





class MaxNLocator(mticker.MaxNLocator):

    def __init__(self, nbins=10, steps=None,

                 trim=True,

                 integer=False,

                 symmetric=False,

                 prune=None):

                                                                             

        super().__init__(nbins, steps=steps, integer=integer,

                         symmetric=symmetric, prune=prune)

        self.create_dummy_axis()



    def __call__(self, v1, v2):

        locs = super().tick_values(v1, v2)

        return np.array(locs), len(locs), 1                                





class FixedLocator:

    def __init__(self, locs):

        self._locs = locs



    def __call__(self, v1, v2):

        v1, v2 = sorted([v1, v2])

        locs = np.array([l for l in self._locs if v1 <= l <= v2])

        return locs, len(locs), 1                                





                



class FormatterPrettyPrint:

    def __init__(self, useMathText=True):

        self._fmt = mticker.ScalarFormatter(

            useMathText=useMathText, useOffset=False)

        self._fmt.create_dummy_axis()



    def __call__(self, direction, factor, values):

        return self._fmt.format_ticks(values)





class DictFormatter:

    def __init__(self, format_dict, formatter=None):

        

        super().__init__()

        self._format_dict = format_dict

        self._fallback_formatter = formatter



    def __call__(self, direction, factor, values):

        

        if self._fallback_formatter:

            fallback_strings = self._fallback_formatter(

                direction, factor, values)

        else:

            fallback_strings = [""] * len(values)

        return [self._format_dict.get(k, v)

                for k, v in zip(values, fallback_strings)]


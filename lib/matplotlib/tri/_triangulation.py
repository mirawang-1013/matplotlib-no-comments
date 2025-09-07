import sys



import numpy as np



from matplotlib import _api





class Triangulation:

    

    def __init__(self, x, y, triangles=None, mask=None):

        from matplotlib import _qhull



        self.x = np.asarray(x, dtype=np.float64)

        self.y = np.asarray(y, dtype=np.float64)

        if self.x.shape != self.y.shape or self.x.ndim != 1:

            raise ValueError("x and y must be equal-length 1D arrays, but "

                             f"found shapes {self.x.shape!r} and "

                             f"{self.y.shape!r}")



        self.mask = None

        self._edges = None

        self._neighbors = None

        self.is_delaunay = False



        if triangles is None:

                                                                            

                                     

            self.triangles, self._neighbors = _qhull.delaunay(x, y, sys.flags.verbose)

            self.is_delaunay = True

        else:

                                                                          

                          

            try:

                self.triangles = np.array(triangles, dtype=np.int32, order='C')

            except ValueError as e:

                raise ValueError('triangles must be a (N, 3) int array, not '

                                 f'{triangles!r}') from e

            if self.triangles.ndim != 2 or self.triangles.shape[1] != 3:

                raise ValueError(

                    'triangles must be a (N, 3) int array, but found shape '

                    f'{self.triangles.shape!r}')

            if self.triangles.max() >= len(self.x):

                raise ValueError(

                    'triangles are indices into the points and must be in the '

                    f'range 0 <= i < {len(self.x)} but found value '

                    f'{self.triangles.max()}')

            if self.triangles.min() < 0:

                raise ValueError(

                    'triangles are indices into the points and must be in the '

                    f'range 0 <= i < {len(self.x)} but found value '

                    f'{self.triangles.min()}')



                                                                  

        self._cpp_triangulation = None



                                                     

        self._trifinder = None



        self.set_mask(mask)



    def calculate_plane_coefficients(self, z):

        

        return self.get_cpp_triangulation().calculate_plane_coefficients(z)



    @property

    def edges(self):

        

        if self._edges is None:

            self._edges = self.get_cpp_triangulation().get_edges()

        return self._edges



    def get_cpp_triangulation(self):

        

        from matplotlib import _tri

        if self._cpp_triangulation is None:

            self._cpp_triangulation = _tri.Triangulation(

                                                                          

                self.x, self.y, self.triangles,

                self.mask if self.mask is not None else (),

                self._edges if self._edges is not None else (),

                self._neighbors if self._neighbors is not None else (),

                not self.is_delaunay)

        return self._cpp_triangulation



    def get_masked_triangles(self):

        

        if self.mask is not None:

            return self.triangles[~self.mask]

        else:

            return self.triangles



    @staticmethod

    def get_from_args_and_kwargs(*args, **kwargs):

        

        if isinstance(args[0], Triangulation):

            triangulation, *args = args

            if 'triangles' in kwargs:

                _api.warn_external(

                    "Passing the keyword 'triangles' has no effect when also "

                    "passing a Triangulation")

            if 'mask' in kwargs:

                _api.warn_external(

                    "Passing the keyword 'mask' has no effect when also "

                    "passing a Triangulation")

        else:

            x, y, triangles, mask, args, kwargs =
                Triangulation._extract_triangulation_params(args, kwargs)

            triangulation = Triangulation(x, y, triangles, mask)

        return triangulation, args, kwargs



    @staticmethod

    def _extract_triangulation_params(args, kwargs):

        x, y, *args = args

                                              

        triangles = kwargs.pop('triangles', None)

        from_args = False

        if triangles is None and args:

            triangles = args[0]

            from_args = True

        if triangles is not None:

            try:

                triangles = np.asarray(triangles, dtype=np.int32)

            except ValueError:

                triangles = None

        if triangles is not None and (triangles.ndim != 2 or

                                      triangles.shape[1] != 3):

            triangles = None

        if triangles is not None and from_args:

            args = args[1:]                                

                                   

        mask = kwargs.pop('mask', None)

        return x, y, triangles, mask, args, kwargs



    def get_trifinder(self):

        

        if self._trifinder is None:

                                      

            from matplotlib.tri._trifinder import TrapezoidMapTriFinder

            self._trifinder = TrapezoidMapTriFinder(self)

        return self._trifinder



    @property

    def neighbors(self):

        

        if self._neighbors is None:

            self._neighbors = self.get_cpp_triangulation().get_neighbors()

        return self._neighbors



    def set_mask(self, mask):

        

        if mask is None:

            self.mask = None

        else:

            self.mask = np.asarray(mask, dtype=bool)

            if self.mask.shape != (self.triangles.shape[0],):

                raise ValueError('mask array must have same length as '

                                 'triangles array')



                                        

        if self._cpp_triangulation is not None:

            self._cpp_triangulation.set_mask(

                self.mask if self.mask is not None else ())



                                                                    

        self._edges = None

        self._neighbors = None



                                             

        if self._trifinder is not None:

            self._trifinder._initialize()


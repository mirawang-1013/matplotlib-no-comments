import numpy as np



from matplotlib import _api

from matplotlib.tri import Triangulation





class TriFinder:

    



    def __init__(self, triangulation):

        _api.check_isinstance(Triangulation, triangulation=triangulation)

        self._triangulation = triangulation



    def __call__(self, x, y):

        raise NotImplementedError





class TrapezoidMapTriFinder(TriFinder):

    



    def __init__(self, triangulation):

        from matplotlib import _tri

        super().__init__(triangulation)

        self._cpp_trifinder = _tri.TrapezoidMapTriFinder(

            triangulation.get_cpp_triangulation())

        self._initialize()



    def __call__(self, x, y):

        

        x = np.asarray(x, dtype=np.float64)

        y = np.asarray(y, dtype=np.float64)

        if x.shape != y.shape:

            raise ValueError("x and y must be array-like with the same shape")



                                                            

        indices = (self._cpp_trifinder.find_many(x.ravel(), y.ravel())

                   .reshape(x.shape))

        return indices



    def _get_tree_stats(self):

        

        return self._cpp_trifinder.get_tree_stats()



    def _initialize(self):

        

        self._cpp_trifinder.initialize()



    def _print_tree(self):

        

        self._cpp_trifinder.print_tree()


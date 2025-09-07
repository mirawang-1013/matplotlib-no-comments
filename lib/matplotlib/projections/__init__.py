



from .. import axes, _docstring

from .geo import AitoffAxes, HammerAxes, LambertAxes, MollweideAxes

from .polar import PolarAxes



try:

    from mpl_toolkits.mplot3d import Axes3D

except Exception:

    import warnings

    warnings.warn("Unable to import Axes3D. This may be due to multiple versions of "

                  "Matplotlib being installed (e.g. as a system package and as a pip "

                  "package). As a result, the 3D projection is not available.")

    Axes3D = None





class ProjectionRegistry:

    



    def __init__(self):

        self._all_projection_types = {}



    def register(self, *projections):

        

        for projection in projections:

            name = projection.name

            self._all_projection_types[name] = projection



    def get_projection_class(self, name):

        

        return self._all_projection_types[name]



    def get_projection_names(self):

        

        return sorted(self._all_projection_types)





projection_registry = ProjectionRegistry()

projection_registry.register(

    axes.Axes,

    PolarAxes,

    AitoffAxes,

    HammerAxes,

    LambertAxes,

    MollweideAxes,

)

if Axes3D is not None:

    projection_registry.register(Axes3D)

else:

                                             

    del Axes3D





def register_projection(cls):

    projection_registry.register(cls)





def get_projection_class(projection=None):

    

    if projection is None:

        projection = 'rectilinear'



    try:

        return projection_registry.get_projection_class(projection)

    except KeyError as err:

        raise ValueError("Unknown projection %r" % projection) from err





get_projection_names = projection_registry.get_projection_names

_docstring.interpd.register(projection_names=get_projection_names())


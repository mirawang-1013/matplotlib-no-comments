

from .. import backends



backends._QT_FORCE_QT5_BINDING = True

from .backend_qtagg import (                                              

    _BackendQTAgg, FigureCanvasQTAgg, FigureManagerQT, NavigationToolbar2QT,

    FigureCanvasAgg, FigureCanvasQT)





@_BackendQTAgg.export

class _BackendQT5Agg(_BackendQTAgg):

    pass


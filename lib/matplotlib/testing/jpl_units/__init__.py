



from .Duration import Duration

from .Epoch import Epoch

from .UnitDbl import UnitDbl



from .StrConverter import StrConverter

from .EpochConverter import EpochConverter

from .UnitDblConverter import UnitDblConverter



from .UnitDblFormatter import UnitDblFormatter





__version__ = "1.0"



__all__ = [

            'register',

            'Duration',

            'Epoch',

            'UnitDbl',

            'UnitDblFormatter',

          ]





def register():

    

    import matplotlib.units as mplU



    mplU.registry[str] = StrConverter()

    mplU.registry[Epoch] = EpochConverter()

    mplU.registry[Duration] = EpochConverter()

    mplU.registry[UnitDbl] = UnitDblConverter()





                             

           

m = UnitDbl(1.0, "m")

km = UnitDbl(1.0, "km")

mile = UnitDbl(1.0, "mile")

        

deg = UnitDbl(1.0, "deg")

rad = UnitDbl(1.0, "rad")

      

sec = UnitDbl(1.0, "sec")

min = UnitDbl(1.0, "min")

hr = UnitDbl(1.0, "hour")

day = UnitDbl(24.0, "hour")

sec = UnitDbl(1.0, "sec")


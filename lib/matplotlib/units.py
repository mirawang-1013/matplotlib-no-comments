



from decimal import Decimal

from numbers import Number



import numpy as np

from numpy import ma



from matplotlib import cbook





class ConversionError(TypeError):

    pass





def _is_natively_supported(x):

    

                                                                   

    if np.iterable(x):

                                                                         

        for thisx in x:

            if thisx is ma.masked:

                continue

            return isinstance(thisx, Number) and not isinstance(thisx, Decimal)

    else:

        return isinstance(x, Number) and not isinstance(x, Decimal)





class AxisInfo:

    

    def __init__(self, majloc=None, minloc=None,

                 majfmt=None, minfmt=None, label=None,

                 default_limits=None):

        

        self.majloc = majloc

        self.minloc = minloc

        self.majfmt = majfmt

        self.minfmt = minfmt

        self.label = label

        self.default_limits = default_limits





class ConversionInterface:

    



    @staticmethod

    def axisinfo(unit, axis):

        

        return None



    @staticmethod

    def default_units(x, axis):

        

        return None



    @staticmethod

    def convert(obj, unit, axis):

        

        return obj





class DecimalConverter(ConversionInterface):

    



    @staticmethod

    def convert(value, unit, axis):

        

        if isinstance(value, Decimal):

            return float(value)

                                    

        elif isinstance(value, ma.MaskedArray):

            return ma.asarray(value, dtype=float)

        else:

            return np.asarray(value, dtype=float)



                                                                          





class Registry(dict):

    



    def get_converter(self, x):

        

                                                        

        x = cbook._unpack_to_numpy(x)



        if isinstance(x, np.ndarray):

                                                                               

                                                                               

                               

            x = np.ma.getdata(x).ravel()

                                                                           

            if not x.size:

                return self.get_converter(np.array([0], dtype=x.dtype))

        for cls in type(x).__mro__:                         

            try:

                return self[cls]

            except KeyError:

                pass

        try:                                                            

            first = cbook._safe_first_finite(x)

        except (TypeError, StopIteration):

            pass

        else:

                                                                             

                                                                          

            if type(first) is not type(x):

                return self.get_converter(first)

        return None





registry = Registry()

registry[Decimal] = DecimalConverter()


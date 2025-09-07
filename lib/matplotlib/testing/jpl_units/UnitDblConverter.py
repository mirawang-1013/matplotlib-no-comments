



import numpy as np



from matplotlib import cbook, units

import matplotlib.projections.polar as polar



__all__ = ['UnitDblConverter']





                                                                    

                                        

                                               

def rad_fn(x, pos=None):

    

    n = int((x / np.pi) * 2.0 + 0.25)

    if n == 0:

        return str(x)

    elif n == 1:

        return r'$\pi/2$'

    elif n == 2:

        return r'$\pi$'

    elif n % 2 == 0:

        return fr'${n//2}\pi$'

    else:

        return fr'${n}\pi/2$'





class UnitDblConverter(units.ConversionInterface):

    

                          

    defaults = {

       "distance": 'km',

       "angle": 'deg',

       "time": 'sec',

       }



    @staticmethod

    def axisinfo(unit, axis):

                             



                                                  

        import matplotlib.testing.jpl_units as U



                                                                         

                                                                        

                                                 

        if unit:

            label = unit if isinstance(unit, str) else unit.label()

        else:

            label = None



        if label == "deg" and isinstance(axis.axes, polar.PolarAxes):

                                                                             

            majfmt = polar.PolarAxes.ThetaFormatter()

        else:

            majfmt = U.UnitDblFormatter(useOffset=False)



        return units.AxisInfo(majfmt=majfmt, label=label)



    @staticmethod

    def convert(value, unit, axis):

                             

        if not cbook.is_scalar_or_string(value):

            return [UnitDblConverter.convert(x, unit, axis) for x in value]

                                                                        

        if unit is None:

            unit = UnitDblConverter.default_units(value, axis)

                                                                   

        if isinstance(axis.axes, polar.PolarAxes) and value.type() == "angle":

                                                               

            return value.convert("rad")

        return value.convert(unit)



    @staticmethod

    def default_units(value, axis):

                             

                                                                           

                                                

        if cbook.is_scalar_or_string(value):

            return UnitDblConverter.defaults[value.type()]

        else:

            return UnitDblConverter.default_units(value[0], axis)


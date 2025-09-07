



from matplotlib import cbook, units

import matplotlib.dates as date_ticker



__all__ = ['EpochConverter']





class EpochConverter(units.ConversionInterface):

    



    jdRef = 1721425.5



    @staticmethod

    def axisinfo(unit, axis):

                             

        majloc = date_ticker.AutoDateLocator()

        majfmt = date_ticker.AutoDateFormatter(majloc)

        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label=unit)



    @staticmethod

    def float2epoch(value, unit):

        

                                                  

        import matplotlib.testing.jpl_units as U



        secPastRef = value * 86400.0 * U.UnitDbl(1.0, 'sec')

        return U.Epoch(unit, secPastRef, EpochConverter.jdRef)



    @staticmethod

    def epoch2float(value, unit):

        

        return value.julianDate(unit) - EpochConverter.jdRef



    @staticmethod

    def duration2float(value):

        

        return value.seconds() / 86400.0



    @staticmethod

    def convert(value, unit, axis):

                             



                                                  

        import matplotlib.testing.jpl_units as U



        if not cbook.is_scalar_or_string(value):

            return [EpochConverter.convert(x, unit, axis) for x in value]

        if unit is None:

            unit = EpochConverter.default_units(value, axis)

        if isinstance(value, U.Duration):

            return EpochConverter.duration2float(value)

        else:

            return EpochConverter.epoch2float(value, unit)



    @staticmethod

    def default_units(value, axis):

                             

        if cbook.is_scalar_or_string(value):

            return value.frame()

        else:

            return EpochConverter.default_units(value[0], axis)


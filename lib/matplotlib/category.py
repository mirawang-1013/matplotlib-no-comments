



from collections import OrderedDict

import dateutil.parser

import itertools

import logging



import numpy as np



from matplotlib import _api, cbook, ticker, units





_log = logging.getLogger(__name__)





class StrCategoryConverter(units.ConversionInterface):

    @staticmethod

    def convert(value, unit, axis):

        

        if unit is None:

            raise ValueError(

                'Missing category information for StrCategoryConverter; '

                'this might be caused by unintendedly mixing categorical and '

                'numeric data')

        StrCategoryConverter._validate_unit(unit)

                                                          

        values = np.atleast_1d(np.array(value, dtype=object))

                                                       

        unit.update(values)

        s = np.vectorize(unit._mapping.__getitem__, otypes=[float])(values)

        return s if not cbook.is_scalar_or_string(value) else s[0]



    @staticmethod

    def axisinfo(unit, axis):

        

        StrCategoryConverter._validate_unit(unit)

                                                         

                                                       

        majloc = StrCategoryLocator(unit._mapping)

        majfmt = StrCategoryFormatter(unit._mapping)

        return units.AxisInfo(majloc=majloc, majfmt=majfmt)



    @staticmethod

    def default_units(data, axis):

        

                                                                            

        if axis.units is None:

            axis.set_units(UnitData(data))

        else:

            axis.units.update(data)

        return axis.units



    @staticmethod

    def _validate_unit(unit):

        if not hasattr(unit, '_mapping'):

            raise ValueError(

                f'Provided unit "{unit}" is not valid for a categorical '

                'converter, as it does not have a _mapping attribute.')





class StrCategoryLocator(ticker.Locator):

    

    def __init__(self, units_mapping):

        

        self._units = units_mapping



    def __call__(self):

                             

        return list(self._units.values())



    def tick_values(self, vmin, vmax):

                             

        return self()





class StrCategoryFormatter(ticker.Formatter):

    

    def __init__(self, units_mapping):

        

        self._units = units_mapping



    def __call__(self, x, pos=None):

                             

        return self.format_ticks([x])[0]



    def format_ticks(self, values):

                             

        r_mapping = {v: self._text(k) for k, v in self._units.items()}

        return [r_mapping.get(round(val), '') for val in values]



    @staticmethod

    def _text(value):

        

        if isinstance(value, bytes):

            value = value.decode(encoding='utf-8')

        elif not isinstance(value, str):

            value = str(value)

        return value





class UnitData:

    def __init__(self, data=None):

        

        self._mapping = OrderedDict()

        self._counter = itertools.count()

        if data is not None:

            self.update(data)



    @staticmethod

    def _str_is_convertible(val):

        

        try:

            float(val)

        except ValueError:

            try:

                dateutil.parser.parse(val)

            except (ValueError, TypeError):

                                                                

                return False

        return True



    def update(self, data):

        

        data = np.atleast_1d(np.array(data, dtype=object))

                                         

        convertible = True

        for val in OrderedDict.fromkeys(data):

                                                                   

            _api.check_isinstance((str, bytes), value=val)

            if convertible:

                                                                          

                convertible = self._str_is_convertible(val)

            if val not in self._mapping:

                self._mapping[val] = next(self._counter)

        if data.size and convertible:

            _log.info('Using categorical units to plot a list of strings '

                      'that are all parsable as floats or dates. If these '

                      'strings should be plotted as numbers, cast to the '

                      'appropriate data type before plotting.')





                                                         

                                        

units.registry[str] =
    units.registry[np.str_] =
    units.registry[bytes] =
    units.registry[np.bytes_] = StrCategoryConverter()


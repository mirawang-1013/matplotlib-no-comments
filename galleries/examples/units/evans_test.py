



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.ticker as ticker

import matplotlib.units as units





class Foo:

    def __init__(self, val, unit=1.0):

        self.unit = unit

        self._val = val * unit



    def value(self, unit):

        if unit is None:

            unit = self.unit

        return self._val / unit





class FooConverter(units.ConversionInterface):

    @staticmethod

    def axisinfo(unit, axis):

        

        if unit == 1.0 or unit == 2.0:

            return units.AxisInfo(

                majloc=ticker.IndexLocator(8, 0),

                majfmt=ticker.FormatStrFormatter("VAL: %s"),

                label='foo',

                )



        else:

            return None



    @staticmethod

    def convert(obj, unit, axis):

        

        if np.iterable(obj):

            return [o.value(unit) for o in obj]

        else:

            return obj.value(unit)



    @staticmethod

    def default_units(x, axis):

        

        if np.iterable(x):

            for thisx in x:

                return thisx.unit

        else:

            return x.unit





units.registry[Foo] = FooConverter()



                  

x = [Foo(val, 1.0) for val in range(0, 50, 2)]

                           

y = [i for i in range(len(x))]



fig, (ax1, ax2) = plt.subplots(1, 2)

fig.suptitle("Custom units")

fig.subplots_adjust(bottom=0.2)



                       

ax2.plot(x, y, 'o', xunits=2.0)

ax2.set_title("xunits = 2.0")

ax2.tick_params(axis='x', rotation=30, rotation_mode='xtick')



                                                                      

ax1.plot(x, y)                      

ax1.set_title('default units')

ax1.tick_params(axis='x', rotation=30, rotation_mode='xtick')



plt.show()


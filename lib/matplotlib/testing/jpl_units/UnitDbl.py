



import functools

import operator



from matplotlib import _api





class UnitDbl:

    



                                                                     

                                                                       

                                                                     

                                      

    allowed = {

        "m": (0.001, "km"),

        "km": (1, "km"),

        "mile": (1.609344, "km"),



        "rad": (1, "rad"),

        "deg": (1.745329251994330e-02, "rad"),



        "sec": (1, "sec"),

        "min": (60.0, "sec"),

        "hour": (3600, "sec"),

        }



    _types = {

        "km": "distance",

        "rad": "angle",

        "sec": "time",

        }



    def __init__(self, value, units):

        

        data = _api.check_getitem(self.allowed, units=units)

        self._value = float(value * data[0])

        self._units = data[1]



    def convert(self, units):

        

        if self._units == units:

            return self._value

        data = _api.check_getitem(self.allowed, units=units)

        if self._units != data[1]:

            raise ValueError(f"Error trying to convert to different units.\n"

                             f"    Invalid conversion requested.\n"

                             f"    UnitDbl: {self}\n"

                             f"    Units:   {units}\n")

        return self._value / data[0]



    def __abs__(self):

        

        return UnitDbl(abs(self._value), self._units)



    def __neg__(self):

        

        return UnitDbl(-self._value, self._units)



    def __bool__(self):

        

        return bool(self._value)



    def _cmp(self, op, rhs):

        

        self.checkSameUnits(rhs, "compare")

        return op(self._value, rhs._value)



    __eq__ = functools.partialmethod(_cmp, operator.eq)

    __ne__ = functools.partialmethod(_cmp, operator.ne)

    __lt__ = functools.partialmethod(_cmp, operator.lt)

    __le__ = functools.partialmethod(_cmp, operator.le)

    __gt__ = functools.partialmethod(_cmp, operator.gt)

    __ge__ = functools.partialmethod(_cmp, operator.ge)



    def _binop_unit_unit(self, op, rhs):

        

        self.checkSameUnits(rhs, op.__name__)

        return UnitDbl(op(self._value, rhs._value), self._units)



    __add__ = functools.partialmethod(_binop_unit_unit, operator.add)

    __sub__ = functools.partialmethod(_binop_unit_unit, operator.sub)



    def _binop_unit_scalar(self, op, scalar):

        

        return UnitDbl(op(self._value, scalar), self._units)



    __mul__ = functools.partialmethod(_binop_unit_scalar, operator.mul)

    __rmul__ = functools.partialmethod(_binop_unit_scalar, operator.mul)



    def __str__(self):

        

        return f"{self._value:g} *{self._units}"



    def __repr__(self):

        

        return f"UnitDbl({self._value:g}, '{self._units}')"



    def type(self):

        

        return self._types[self._units]



    @staticmethod

    def range(start, stop, step=None):

        

        if step is None:

            step = UnitDbl(1, start._units)



        elems = []



        i = 0

        while True:

            d = start + i * step

            if d >= stop:

                break



            elems.append(d)

            i += 1



        return elems



    def checkSameUnits(self, rhs, func):

        

        if self._units != rhs._units:

            raise ValueError(f"Cannot {func} units of different types.\n"

                             f"LHS: {self._units}\n"

                             f"RHS: {rhs._units}")


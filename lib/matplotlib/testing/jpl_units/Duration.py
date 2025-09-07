



import functools

import operator



from matplotlib import _api





class Duration:

    



    allowed = ["ET", "UTC"]



    def __init__(self, frame, seconds):

        

        _api.check_in_list(self.allowed, frame=frame)

        self._frame = frame

        self._seconds = seconds



    def frame(self):

        

        return self._frame



    def __abs__(self):

        

        return Duration(self._frame, abs(self._seconds))



    def __neg__(self):

        

        return Duration(self._frame, -self._seconds)



    def seconds(self):

        

        return self._seconds



    def __bool__(self):

        return self._seconds != 0



    def _cmp(self, op, rhs):

        

        self.checkSameFrame(rhs, "compare")

        return op(self._seconds, rhs._seconds)



    __eq__ = functools.partialmethod(_cmp, operator.eq)

    __ne__ = functools.partialmethod(_cmp, operator.ne)

    __lt__ = functools.partialmethod(_cmp, operator.lt)

    __le__ = functools.partialmethod(_cmp, operator.le)

    __gt__ = functools.partialmethod(_cmp, operator.gt)

    __ge__ = functools.partialmethod(_cmp, operator.ge)



    def __add__(self, rhs):

        

                                                  

        import matplotlib.testing.jpl_units as U



        if isinstance(rhs, U.Epoch):

            return rhs + self



        self.checkSameFrame(rhs, "add")

        return Duration(self._frame, self._seconds + rhs._seconds)



    def __sub__(self, rhs):

        

        self.checkSameFrame(rhs, "sub")

        return Duration(self._frame, self._seconds - rhs._seconds)



    def __mul__(self, rhs):

        

        return Duration(self._frame, self._seconds * float(rhs))



    __rmul__ = __mul__



    def __str__(self):

        

        return f"{self._seconds:g} {self._frame}"



    def __repr__(self):

        

        return f"Duration('{self._frame}', {self._seconds:g})"



    def checkSameFrame(self, rhs, func):

        

        if self._frame != rhs._frame:

            raise ValueError(

                f"Cannot {func} Durations with different frames.\n"

                f"LHS: {self._frame}\n"

                f"RHS: {rhs._frame}")


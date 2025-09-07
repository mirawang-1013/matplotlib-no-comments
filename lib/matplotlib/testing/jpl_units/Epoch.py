



import functools

import operator

import math

import datetime as DT



from matplotlib import _api

from matplotlib.dates import date2num





class Epoch:

                                         

                                             

    allowed = {

        "ET": {

            "UTC": +64.1839,

            },

        "UTC": {

            "ET": -64.1839,

            },

        }



    def __init__(self, frame, sec=None, jd=None, daynum=None, dt=None):

        

        if ((sec is None and jd is not None) or

                (sec is not None and jd is None) or

                (daynum is not None and

                 (sec is not None or jd is not None)) or

                (daynum is None and dt is None and

                 (sec is None or jd is None)) or

                (daynum is not None and dt is not None) or

                (dt is not None and (sec is not None or jd is not None)) or

                ((dt is not None) and not isinstance(dt, DT.datetime))):

            raise ValueError(

                "Invalid inputs.  Must enter sec and jd together, "

                "daynum by itself, or dt (must be a python datetime).\n"

                "Sec = %s\n"

                "JD  = %s\n"

                "dnum= %s\n"

                "dt  = %s" % (sec, jd, daynum, dt))



        _api.check_in_list(self.allowed, frame=frame)

        self._frame = frame



        if dt is not None:

            daynum = date2num(dt)



        if daynum is not None:

                                          

            jd = float(daynum) + 1721425.5

            self._jd = math.floor(jd)

            self._seconds = (jd - self._jd) * 86400.0



        else:

            self._seconds = float(sec)

            self._jd = float(jd)



                                                 

            deltaDays = math.floor(self._seconds / 86400)

            self._jd += deltaDays

            self._seconds -= deltaDays * 86400.0



    def convert(self, frame):

        if self._frame == frame:

            return self



        offset = self.allowed[self._frame][frame]



        return Epoch(frame, self._seconds + offset, self._jd)



    def frame(self):

        return self._frame



    def julianDate(self, frame):

        t = self

        if frame != self._frame:

            t = self.convert(frame)



        return t._jd + t._seconds / 86400.0



    def secondsPast(self, frame, jd):

        t = self

        if frame != self._frame:

            t = self.convert(frame)



        delta = t._jd - jd

        return t._seconds + delta * 86400



    def _cmp(self, op, rhs):

        

        t = self

        if self._frame != rhs._frame:

            t = self.convert(rhs._frame)

        if t._jd != rhs._jd:

            return op(t._jd, rhs._jd)

        return op(t._seconds, rhs._seconds)



    __eq__ = functools.partialmethod(_cmp, operator.eq)

    __ne__ = functools.partialmethod(_cmp, operator.ne)

    __lt__ = functools.partialmethod(_cmp, operator.lt)

    __le__ = functools.partialmethod(_cmp, operator.le)

    __gt__ = functools.partialmethod(_cmp, operator.gt)

    __ge__ = functools.partialmethod(_cmp, operator.ge)



    def __add__(self, rhs):

        

        t = self

        if self._frame != rhs.frame():

            t = self.convert(rhs._frame)



        sec = t._seconds + rhs.seconds()



        return Epoch(t._frame, sec, t._jd)



    def __sub__(self, rhs):

        

                                                  

        import matplotlib.testing.jpl_units as U



                                 

        if isinstance(rhs, U.Duration):

            return self + -rhs



        t = self

        if self._frame != rhs._frame:

            t = self.convert(rhs._frame)



        days = t._jd - rhs._jd

        sec = t._seconds - rhs._seconds



        return U.Duration(rhs._frame, days*86400 + sec)



    def __str__(self):

        

        return f"{self.julianDate(self._frame):22.15e} {self._frame}"



    def __repr__(self):

        

        return str(self)



    @staticmethod

    def range(start, stop, step):

        

        elems = []



        i = 0

        while True:

            d = start + i * step

            if d >= stop:

                break



            elems.append(d)

            i += 1



        return elems


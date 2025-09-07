



from matplotlib.cbook import flatten, silent_list



import matplotlib as mpl



from matplotlib.dates import (

    date2num, num2date, datestr2num, drange, DateFormatter, DateLocator,

    RRuleLocator, YearLocator, MonthLocator, WeekdayLocator, DayLocator,

    HourLocator, MinuteLocator, SecondLocator, rrule, MO, TU, WE, TH, FR,

    SA, SU, YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY,

    relativedelta)



                                                        

                         



                                                                            



from matplotlib.mlab import (

    detrend, detrend_linear, detrend_mean, detrend_none, window_hanning,

    window_none)



from matplotlib import cbook, mlab, pyplot as plt

from matplotlib.pyplot import *



from numpy import *

from numpy.fft import *

from numpy.random import *

from numpy.linalg import *



import numpy as np

import numpy.ma as ma



                                        

import datetime



                                                          

                                    

bytes = __import__("builtins").bytes

                                                         

abs = __import__("builtins").abs

bool = __import__("builtins").bool

max = __import__("builtins").max

min = __import__("builtins").min

pow = __import__("builtins").pow

round = __import__("builtins").round


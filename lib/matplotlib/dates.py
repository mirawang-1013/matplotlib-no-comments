



import datetime

import functools

import logging

import re



from dateutil.rrule import (rrule, MO, TU, WE, TH, FR, SA, SU, YEARLY,

                            MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY,

                            SECONDLY)

from dateutil.relativedelta import relativedelta

import dateutil.parser

import dateutil.tz

import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook, ticker, units



__all__ = ('datestr2num', 'date2num', 'num2date', 'num2timedelta', 'drange',

           'set_epoch', 'get_epoch', 'DateFormatter', 'ConciseDateFormatter',

           'AutoDateFormatter', 'DateLocator', 'RRuleLocator',

           'AutoDateLocator', 'YearLocator', 'MonthLocator', 'WeekdayLocator',

           'DayLocator', 'HourLocator', 'MinuteLocator',

           'SecondLocator', 'MicrosecondLocator',

           'rrule', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU',

           'YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY',

           'HOURLY', 'MINUTELY', 'SECONDLY', 'MICROSECONDLY', 'relativedelta',

           'DateConverter', 'ConciseDateConverter', 'rrulewrapper')





_log = logging.getLogger(__name__)

UTC = datetime.timezone.utc





def _get_tzinfo(tz=None):

    

    tz = mpl._val_or_rc(tz, 'timezone')

    if tz == 'UTC':

        return UTC

    if isinstance(tz, str):

        tzinfo = dateutil.tz.gettz(tz)

        if tzinfo is None:

            raise ValueError(f"{tz} is not a valid timezone as parsed by"

                             " dateutil.tz.gettz.")

        return tzinfo

    if isinstance(tz, datetime.tzinfo):

        return tz

    raise TypeError(f"tz must be string or tzinfo subclass, not {tz!r}.")





                         

EPOCH_OFFSET = float(datetime.datetime(1970, 1, 1).toordinal())

                                        

MICROSECONDLY = SECONDLY + 1

HOURS_PER_DAY = 24.

MIN_PER_HOUR = 60.

SEC_PER_MIN = 60.

MONTHS_PER_YEAR = 12.



DAYS_PER_WEEK = 7.

DAYS_PER_MONTH = 30.

DAYS_PER_YEAR = 365.0



MINUTES_PER_DAY = MIN_PER_HOUR * HOURS_PER_DAY



SEC_PER_HOUR = SEC_PER_MIN * MIN_PER_HOUR

SEC_PER_DAY = SEC_PER_HOUR * HOURS_PER_DAY

SEC_PER_WEEK = SEC_PER_DAY * DAYS_PER_WEEK



MUSECONDS_PER_DAY = 1e6 * SEC_PER_DAY



MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = (

    MO, TU, WE, TH, FR, SA, SU)

WEEKDAYS = (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY)



                                           

_epoch = None





def _reset_epoch_test_example():

    

    global _epoch

    _epoch = None





def set_epoch(epoch):

    

    global _epoch

    if _epoch is not None:

        raise RuntimeError('set_epoch must be called before dates plotted.')

    _epoch = epoch





def get_epoch():

    

    global _epoch



    _epoch = mpl._val_or_rc(_epoch, 'date.epoch')

    return _epoch





def _dt64_to_ordinalf(d):

    



                                                                         

                                                     

    dseconds = d.astype('datetime64[s]')

    extra = (d - dseconds).astype('timedelta64[ns]')

    t0 = np.datetime64(get_epoch(), 's')

    dt = (dseconds - t0).astype(np.float64)

    dt += extra.astype(np.float64) / 1.0e9

    dt = dt / SEC_PER_DAY



    NaT_int = np.datetime64('NaT').astype(np.int64)

    d_int = d.astype(np.int64)

    dt[d_int == NaT_int] = np.nan

    return dt





def _from_ordinalf(x, tz=None):

    



    tz = _get_tzinfo(tz)



    dt = (np.datetime64(get_epoch()) +

          np.timedelta64(int(np.round(x * MUSECONDS_PER_DAY)), 'us'))

    if dt < np.datetime64('0001-01-01') or dt >= np.datetime64('10000-01-01'):

        raise ValueError(f'Date ordinal {x} converts to {dt} (using '

                         f'epoch {get_epoch()}), but Matplotlib dates must be '

                          'between year 0001 and 9999.')

                                          

    dt = dt.tolist()



                               

    dt = dt.replace(tzinfo=dateutil.tz.gettz('UTC'))

                                                               

    dt = dt.astimezone(tz)

                          

    if np.abs(x) > 70 * 365:

                                                                

                                                   

        ms = round(dt.microsecond / 20) * 20

        if ms == 1000000:

            dt = dt.replace(microsecond=0) + datetime.timedelta(seconds=1)

        else:

            dt = dt.replace(microsecond=ms)



    return dt





                                                              

_from_ordinalf_np_vectorized = np.vectorize(_from_ordinalf, otypes="O")

                                                                     

_dateutil_parser_parse_np_vectorized = np.vectorize(dateutil.parser.parse)





def datestr2num(d, default=None):

    

    if isinstance(d, str):

        dt = dateutil.parser.parse(d, default=default)

        return date2num(dt)

    else:

        if default is not None:

            d = [date2num(dateutil.parser.parse(s, default=default))

                 for s in d]

            return np.asarray(d)

        d = np.asarray(d)

        if not d.size:

            return d

        return date2num(_dateutil_parser_parse_np_vectorized(d))





def date2num(d):

    

                                                    

    d = cbook._unpack_to_numpy(d)



                                                       

    iterable = np.iterable(d)

    if not iterable:

        d = [d]



    masked = np.ma.is_masked(d)

    mask = np.ma.getmask(d)

    d = np.asarray(d)



                                                   

    if not np.issubdtype(d.dtype, np.datetime64):

                         

        if not d.size:

                                          

            return d

        tzi = getattr(d[0], 'tzinfo', None)

        if tzi is not None:

                                  

            d = [dt.astimezone(UTC).replace(tzinfo=None) for dt in d]

            d = np.asarray(d)

        d = d.astype('datetime64[us]')



    d = np.ma.masked_array(d, mask=mask) if masked else d

    d = _dt64_to_ordinalf(d)



    return d if iterable else d[0]





def num2date(x, tz=None):

    

    tz = _get_tzinfo(tz)

    return _from_ordinalf_np_vectorized(x, tz).tolist()





_ordinalf_to_timedelta_np_vectorized = np.vectorize(

    lambda x: datetime.timedelta(days=x), otypes="O")





def num2timedelta(x):

    

    return _ordinalf_to_timedelta_np_vectorized(x).tolist()





def drange(dstart, dend, delta):

    

    f1 = date2num(dstart)

    f2 = date2num(dend)

    step = delta.total_seconds() / SEC_PER_DAY



                                                                        

    num = int(np.ceil((f2 - f1) / step))



                                                           

    dinterval_end = dstart + num * delta



                                                                         

    if dinterval_end >= dend:

                                                           

                                 

        dinterval_end -= delta

        num -= 1



    f2 = date2num(dinterval_end)                      

    return np.linspace(f1, f2, num + 1)





def _wrap_in_tex(text):

    p = r'([a-zA-Z]+)'

    ret_text = re.sub(p, r'}$\1$\\mathdefault{', text)



                                                                 

    ret_text = ret_text.replace('-', '{-}').replace(':', '{:}')

                                               

    ret_text = ret_text.replace(' ', r'\;')

    ret_text = '$\\mathdefault{' + ret_text + '}$'

    ret_text = ret_text.replace('$\\mathdefault{}$', '')

    return ret_text





                                        





class DateFormatter(ticker.Formatter):

    



    def __init__(self, fmt, tz=None, *, usetex=None):

        

        self.tz = _get_tzinfo(tz)

        self.fmt = fmt

        self._usetex = mpl._val_or_rc(usetex, 'text.usetex')



    def __call__(self, x, pos=0):

        result = num2date(x, self.tz).strftime(self.fmt)

        return _wrap_in_tex(result) if self._usetex else result



    def set_tzinfo(self, tz):

        self.tz = _get_tzinfo(tz)





class ConciseDateFormatter(ticker.Formatter):

    



    def __init__(self, locator, tz=None, formats=None, offset_formats=None,

                 zero_formats=None, show_offset=True, *, usetex=None):

        

        self._locator = locator

        self._tz = tz

        self.defaultfmt = '%Y'

                                                                      

                                                

                                          

        if formats:

            if len(formats) != 6:

                raise ValueError('formats argument must be a list of '

                                 '6 format strings (or None)')

            self.formats = formats

        else:

            self.formats = ['%Y',                          

                            '%b',                                   

                            '%d',                                 

                            '%H:%M',            

                            '%H:%M',            

                            '%S.%f',             

                            ]

                                                       

                                                               

                                                              

                                

        if zero_formats:

            if len(zero_formats) != 6:

                raise ValueError('zero_formats argument must be a list of '

                                 '6 format strings (or None)')

            self.zero_formats = zero_formats

        elif formats:

                                                             

            self.zero_formats = [''] + self.formats[:-1]

        else:

                                            

            self.zero_formats = [''] + self.formats[:-1]

            self.zero_formats[3] = '%b-%d'



        if offset_formats:

            if len(offset_formats) != 6:

                raise ValueError('offset_formats argument must be a list of '

                                 '6 format strings (or None)')

            self.offset_formats = offset_formats

        else:

            self.offset_formats = ['',

                                   '%Y',

                                   '%Y-%b',

                                   '%Y-%b-%d',

                                   '%Y-%b-%d',

                                   '%Y-%b-%d %H:%M']

        self.offset_string = ''

        self.show_offset = show_offset

        self._usetex = mpl._val_or_rc(usetex, 'text.usetex')



    def __call__(self, x, pos=None):

        formatter = DateFormatter(self.defaultfmt, self._tz,

                                  usetex=self._usetex)

        return formatter(x, pos=pos)



    def format_ticks(self, values):

        tickdatetime = [num2date(value, tz=self._tz) for value in values]

        tickdate = np.array([tdt.timetuple()[:6] for tdt in tickdatetime])



                          

                                                                          

                                                           

                                                               

                                  

                                          

        fmts = self.formats

                                                        

        zerofmts = self.zero_formats

                                                                

                                     

        offsetfmts = self.offset_formats

        show_offset = self.show_offset



                                               

                                                

                                                           

        for level in range(5, -1, -1):

            unique = np.unique(tickdate[:, level])

            if len(unique) > 1:

                                                                        

                if level < 2 and np.any(unique == 1):

                    show_offset = False

                break

            elif level == 0:

                                                                              

                                                                            

                level = 5



                                                    

                                                           

        zerovals = [0, 1, 1, 0, 0, 0, 0]

        labels = [''] * len(tickdate)

        for nn in range(len(tickdate)):

            if level < 5:

                if tickdate[nn][level] == zerovals[level]:

                    fmt = zerofmts[level]

                else:

                    fmt = fmts[level]

            else:

                                                             

                if (tickdatetime[nn].second == tickdatetime[nn].microsecond

                        == 0):

                    fmt = zerofmts[level]

                else:

                    fmt = fmts[level]

            labels[nn] = tickdatetime[nn].strftime(fmt)



                                                       

                                                    

                                                                              

                                                                            

                                                                     

        if level >= 5:

            trailing_zeros = min(

                (len(s) - len(s.rstrip('0')) for s in labels if '.' in s),

                default=None)

            if trailing_zeros:

                for nn in range(len(labels)):

                    if '.' in labels[nn]:

                        labels[nn] = labels[nn][:-trailing_zeros].rstrip('.')



        if show_offset:

                                    

            if (self._locator.axis and

                    self._locator.axis.__name__ in ('xaxis', 'yaxis')

                    and self._locator.axis.get_inverted()):

                self.offset_string = tickdatetime[0].strftime(offsetfmts[level])

            else:

                self.offset_string = tickdatetime[-1].strftime(offsetfmts[level])

            if self._usetex:

                self.offset_string = _wrap_in_tex(self.offset_string)

        else:

            self.offset_string = ''



        if self._usetex:

            return [_wrap_in_tex(l) for l in labels]

        else:

            return labels



    def get_offset(self):

        return self.offset_string



    def format_data_short(self, value):

        return num2date(value, tz=self._tz).strftime('%Y-%m-%d %H:%M:%S')





class AutoDateFormatter(ticker.Formatter):

    



                                                                    

                                                       



                                                                    

                                                                  

                                                                    

                                      



                                                           

                    



    def __init__(self, locator, tz=None, defaultfmt='%Y-%m-%d', *,

                 usetex=None):

        

        self._locator = locator

        self._tz = tz

        self.defaultfmt = defaultfmt

        self._formatter = DateFormatter(self.defaultfmt, tz)

        rcParams = mpl.rcParams

        self._usetex = mpl._val_or_rc(usetex, 'text.usetex')

        self.scaled = {

            DAYS_PER_YEAR: rcParams['date.autoformatter.year'],

            DAYS_PER_MONTH: rcParams['date.autoformatter.month'],

            1: rcParams['date.autoformatter.day'],

            1 / HOURS_PER_DAY: rcParams['date.autoformatter.hour'],

            1 / MINUTES_PER_DAY: rcParams['date.autoformatter.minute'],

            1 / SEC_PER_DAY: rcParams['date.autoformatter.second'],

            1 / MUSECONDS_PER_DAY: rcParams['date.autoformatter.microsecond']

        }



    def _set_locator(self, locator):

        self._locator = locator



    def __call__(self, x, pos=None):

        try:

            locator_unit_scale = float(self._locator._get_unit())

        except AttributeError:

            locator_unit_scale = 1

                                                                      

        fmt = next((fmt for scale, fmt in sorted(self.scaled.items())

                    if scale >= locator_unit_scale),

                   self.defaultfmt)



        if isinstance(fmt, str):

            self._formatter = DateFormatter(fmt, self._tz, usetex=self._usetex)

            result = self._formatter(x, pos)

        elif callable(fmt):

            result = fmt(x, pos)

        else:

            raise TypeError(f'Unexpected type passed to {self!r}.')



        return result





class rrulewrapper:

    

    def __init__(self, freq, tzinfo=None, **kwargs):

        

        kwargs['freq'] = freq

        self._base_tzinfo = tzinfo



        self._update_rrule(**kwargs)



    def set(self, **kwargs):

        

        self._construct.update(kwargs)



        self._update_rrule(**self._construct)



    def _update_rrule(self, **kwargs):

        tzinfo = self._base_tzinfo



                                                                          

                                                                           

                                

        if 'dtstart' in kwargs:

            dtstart = kwargs['dtstart']

            if dtstart.tzinfo is not None:

                if tzinfo is None:

                    tzinfo = dtstart.tzinfo

                else:

                    dtstart = dtstart.astimezone(tzinfo)



                kwargs['dtstart'] = dtstart.replace(tzinfo=None)



        if 'until' in kwargs:

            until = kwargs['until']

            if until.tzinfo is not None:

                if tzinfo is not None:

                    until = until.astimezone(tzinfo)

                else:

                    raise ValueError('until cannot be aware if dtstart '

                                     'is naive and tzinfo is None')



                kwargs['until'] = until.replace(tzinfo=None)



        self._construct = kwargs.copy()

        self._tzinfo = tzinfo

        self._rrule = rrule(**self._construct)



    def _attach_tzinfo(self, dt, tzinfo):

                                                              

        if hasattr(tzinfo, 'localize'):

            return tzinfo.localize(dt, is_dst=True)



        return dt.replace(tzinfo=tzinfo)



    def _aware_return_wrapper(self, f, returns_list=False):

        

                                                                     

        if self._tzinfo is None:

            return f



                                                                               

                                                                 

        def normalize_arg(arg):

            if isinstance(arg, datetime.datetime) and arg.tzinfo is not None:

                if arg.tzinfo is not self._tzinfo:

                    arg = arg.astimezone(self._tzinfo)



                return arg.replace(tzinfo=None)



            return arg



        def normalize_args(args, kwargs):

            args = tuple(normalize_arg(arg) for arg in args)

            kwargs = {kw: normalize_arg(arg) for kw, arg in kwargs.items()}



            return args, kwargs



                                                                           

                                                    

        if not returns_list:

            def inner_func(*args, **kwargs):

                args, kwargs = normalize_args(args, kwargs)

                dt = f(*args, **kwargs)

                return self._attach_tzinfo(dt, self._tzinfo)

        else:

            def inner_func(*args, **kwargs):

                args, kwargs = normalize_args(args, kwargs)

                dts = f(*args, **kwargs)

                return [self._attach_tzinfo(dt, self._tzinfo) for dt in dts]



        return functools.wraps(f)(inner_func)



    def __getattr__(self, name):

        if name in self.__dict__:

            return self.__dict__[name]



        f = getattr(self._rrule, name)



        if name in {'after', 'before'}:

            return self._aware_return_wrapper(f)

        elif name in {'xafter', 'xbefore', 'between'}:

            return self._aware_return_wrapper(f, returns_list=True)

        else:

            return f



    def __setstate__(self, state):

        self.__dict__.update(state)





class DateLocator(ticker.Locator):

    

    hms0d = {'byhour': 0, 'byminute': 0, 'bysecond': 0}



    def __init__(self, tz=None):

        

        self.tz = _get_tzinfo(tz)



    def set_tzinfo(self, tz):

        

        self.tz = _get_tzinfo(tz)



    def datalim_to_dt(self):

        

        dmin, dmax = self.axis.get_data_interval()

        if dmin > dmax:

            dmin, dmax = dmax, dmin



        return num2date(dmin, self.tz), num2date(dmax, self.tz)



    def viewlim_to_dt(self):

        

        vmin, vmax = self.axis.get_view_interval()

        if vmin > vmax:

            vmin, vmax = vmax, vmin

        return num2date(vmin, self.tz), num2date(vmax, self.tz)



    def _get_unit(self):

        

        return 1



    def _get_interval(self):

        

        return 1



    def nonsingular(self, vmin, vmax):

        

        if not np.isfinite(vmin) or not np.isfinite(vmax):

                                                                   

            return (date2num(datetime.date(1970, 1, 1)),

                    date2num(datetime.date(1970, 1, 2)))

        if vmax < vmin:

            vmin, vmax = vmax, vmin

        unit = self._get_unit()

        interval = self._get_interval()

        if abs(vmax - vmin) < 1e-6:

            vmin -= 2 * unit * interval

            vmax += 2 * unit * interval

        return vmin, vmax





class RRuleLocator(DateLocator):

                                     



    def __init__(self, o, tz=None):

        super().__init__(tz)

        self.rule = o



    def __call__(self):

                                                                    

        try:

            dmin, dmax = self.viewlim_to_dt()

        except ValueError:

            return []



        return self.tick_values(dmin, dmax)



    def tick_values(self, vmin, vmax):

        start, stop = self._create_rrule(vmin, vmax)

        dates = self.rule.between(start, stop, True)

        if len(dates) == 0:

            return date2num([vmin, vmax])

        return self.raise_if_exceeds(date2num(dates))



    def _create_rrule(self, vmin, vmax):

                                                            

                       

        delta = relativedelta(vmax, vmin)



                                                           

        try:

            start = vmin - delta

        except (ValueError, OverflowError):

                 

            start = datetime.datetime(1, 1, 1, 0, 0, 0,

                                      tzinfo=datetime.timezone.utc)



        try:

            stop = vmax + delta

        except (ValueError, OverflowError):

                 

            stop = datetime.datetime(9999, 12, 31, 23, 59, 59,

                                     tzinfo=datetime.timezone.utc)



        self.rule.set(dtstart=start, until=stop)



        return vmin, vmax



    def _get_unit(self):

                             

        freq = self.rule._rrule._freq

        return self.get_unit_generic(freq)



    @staticmethod

    def get_unit_generic(freq):

        if freq == YEARLY:

            return DAYS_PER_YEAR

        elif freq == MONTHLY:

            return DAYS_PER_MONTH

        elif freq == WEEKLY:

            return DAYS_PER_WEEK

        elif freq == DAILY:

            return 1.0

        elif freq == HOURLY:

            return 1.0 / HOURS_PER_DAY

        elif freq == MINUTELY:

            return 1.0 / MINUTES_PER_DAY

        elif freq == SECONDLY:

            return 1.0 / SEC_PER_DAY

        else:

                   

            return -1                                   



    def _get_interval(self):

        return self.rule._rrule._interval





class AutoDateLocator(DateLocator):

    



    def __init__(self, tz=None, minticks=5, maxticks=None,

                 interval_multiples=True):

        

        super().__init__(tz=tz)

        self._freq = YEARLY

        self._freqs = [YEARLY, MONTHLY, DAILY, HOURLY, MINUTELY,

                       SECONDLY, MICROSECONDLY]

        self.minticks = minticks



        self.maxticks = {YEARLY: 11, MONTHLY: 12, DAILY: 11, HOURLY: 12,

                         MINUTELY: 11, SECONDLY: 11, MICROSECONDLY: 8}

        if maxticks is not None:

            try:

                self.maxticks.update(maxticks)

            except TypeError:

                                                                          

                                                                  

                                     

                self.maxticks = dict.fromkeys(self._freqs, maxticks)

        self.interval_multiples = interval_multiples

        self.intervald = {

            YEARLY:   [1, 2, 4, 5, 10, 20, 40, 50, 100, 200, 400, 500,

                       1000, 2000, 4000, 5000, 10000],

            MONTHLY:  [1, 2, 3, 4, 6],

            DAILY:    [1, 2, 3, 7, 14, 21],

            HOURLY:   [1, 2, 3, 4, 6, 12],

            MINUTELY: [1, 5, 10, 15, 30],

            SECONDLY: [1, 5, 10, 15, 30],

            MICROSECONDLY: [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000,

                            5000, 10000, 20000, 50000, 100000, 200000, 500000,

                            1000000],

                            }

        if interval_multiples:

                                                                        

                                                                  

                                                          

            self.intervald[DAILY] = [1, 2, 4, 7, 14]



        self._byranges = [None, range(1, 13), range(1, 32),

                          range(0, 24), range(0, 60), range(0, 60), None]



    def __call__(self):

                             

        dmin, dmax = self.viewlim_to_dt()

        locator = self.get_locator(dmin, dmax)

        return locator()



    def tick_values(self, vmin, vmax):

        return self.get_locator(vmin, vmax).tick_values(vmin, vmax)



    def nonsingular(self, vmin, vmax):

                                                          

                                                                  

        if not np.isfinite(vmin) or not np.isfinite(vmax):

                                                                   

            return (date2num(datetime.date(1970, 1, 1)),

                    date2num(datetime.date(1970, 1, 2)))

        if vmax < vmin:

            vmin, vmax = vmax, vmin

        if vmin == vmax:

            vmin = vmin - DAYS_PER_YEAR * 2

            vmax = vmax + DAYS_PER_YEAR * 2

        return vmin, vmax



    def _get_unit(self):

        if self._freq in [MICROSECONDLY]:

            return 1. / MUSECONDS_PER_DAY

        else:

            return RRuleLocator.get_unit_generic(self._freq)



    def get_locator(self, dmin, dmax):

        

        delta = relativedelta(dmax, dmin)

        tdelta = dmax - dmin



                                  

        if dmin > dmax:

            delta = -delta

            tdelta = -tdelta

                                                                          

                                                                             

                                                                            

                            

        numYears = float(delta.years)

        numMonths = numYears * MONTHS_PER_YEAR + delta.months

        numDays = tdelta.days                                              

        numHours = numDays * HOURS_PER_DAY + delta.hours

        numMinutes = numHours * MIN_PER_HOUR + delta.minutes

        numSeconds = np.floor(tdelta.total_seconds())

        numMicroseconds = np.floor(tdelta.total_seconds() * 1e6)



        nums = [numYears, numMonths, numDays, numHours, numMinutes,

                numSeconds, numMicroseconds]



        use_rrule_locator = [True] * 6 + [False]



                                                           

                                                                    

                                               

        byranges = [None, 1, 1, 0, 0, 0, None]



                                                                         

                                                                        

                                                                          

                                                                     

                                                                      

        for i, (freq, num) in enumerate(zip(self._freqs, nums)):

                                                                              

            if num < self.minticks:

                                                                      

                                                                       

                             

                byranges[i] = None

                continue



                                                                          

                   

            for interval in self.intervald[freq]:

                if num <= interval * (self.maxticks[freq] - 1):

                    break

            else:

                if not (self.interval_multiples and freq == DAILY):

                    _api.warn_external(

                        f"AutoDateLocator was unable to pick an appropriate "

                        f"interval for this date range. It may be necessary "

                        f"to add an interval value to the AutoDateLocator's "

                        f"intervald dictionary. Defaulting to {interval}.")



                                                

            self._freq = freq



            if self._byranges[i] and self.interval_multiples:

                byranges[i] = self._byranges[i][::interval]

                if i in (DAILY, WEEKLY):

                    if interval == 14:

                                                                 

                        byranges[i] = [1, 15]

                    elif interval == 7:

                        byranges[i] = [1, 8, 15, 22]



                interval = 1

            else:

                byranges[i] = self._byranges[i]

            break

        else:

            interval = 1



        if (freq == YEARLY) and self.interval_multiples:

            locator = YearLocator(interval, tz=self.tz)

        elif use_rrule_locator[i]:

            _, bymonth, bymonthday, byhour, byminute, bysecond, _ = byranges

            rrule = rrulewrapper(self._freq, interval=interval,

                                 dtstart=dmin, until=dmax,

                                 bymonth=bymonth, bymonthday=bymonthday,

                                 byhour=byhour, byminute=byminute,

                                 bysecond=bysecond)



            locator = RRuleLocator(rrule, tz=self.tz)

        else:

            locator = MicrosecondLocator(interval, tz=self.tz)

            if date2num(dmin) > 70 * 365 and interval < 1000:

                _api.warn_external(

                    'Plotting microsecond time intervals for dates far from '

                    f'the epoch (time origin: {get_epoch()}) is not well-'

                    'supported. See matplotlib.dates.set_epoch to change the '

                    'epoch.')



        locator.set_axis(self.axis)

        return locator





class YearLocator(RRuleLocator):

    

    def __init__(self, base=1, month=1, day=1, tz=None):

        

        rule = rrulewrapper(YEARLY, interval=base, bymonth=month,

                            bymonthday=day, **self.hms0d)

        super().__init__(rule, tz=tz)

        self.base = ticker._Edge_integer(base, 0)



    def _create_rrule(self, vmin, vmax):

                                                                           

                                                              

        ymin = max(self.base.le(vmin.year) * self.base.step, 1)

        ymax = min(self.base.ge(vmax.year) * self.base.step, 9999)



        c = self.rule._construct

        replace = {'year': ymin,

                   'month': c.get('bymonth', 1),

                   'day': c.get('bymonthday', 1),

                   'hour': 0, 'minute': 0, 'second': 0}



        start = vmin.replace(**replace)

        stop = start.replace(year=ymax)

        self.rule.set(dtstart=start, until=stop)



        return start, stop





class MonthLocator(RRuleLocator):

    

    def __init__(self, bymonth=None, bymonthday=1, interval=1, tz=None):

        

        if bymonth is None:

            bymonth = range(1, 13)



        rule = rrulewrapper(MONTHLY, bymonth=bymonth, bymonthday=bymonthday,

                            interval=interval, **self.hms0d)

        super().__init__(rule, tz=tz)





class WeekdayLocator(RRuleLocator):

    



    def __init__(self, byweekday=1, interval=1, tz=None):

        

        rule = rrulewrapper(DAILY, byweekday=byweekday,

                            interval=interval, **self.hms0d)

        super().__init__(rule, tz=tz)





class DayLocator(RRuleLocator):

    

    def __init__(self, bymonthday=None, interval=1, tz=None):

        

        if interval != int(interval) or interval < 1:

            raise ValueError("interval must be an integer greater than 0")

        if bymonthday is None:

            bymonthday = range(1, 32)



        rule = rrulewrapper(DAILY, bymonthday=bymonthday,

                            interval=interval, **self.hms0d)

        super().__init__(rule, tz=tz)





class HourLocator(RRuleLocator):

    

    def __init__(self, byhour=None, interval=1, tz=None):

        

        if byhour is None:

            byhour = range(24)



        rule = rrulewrapper(HOURLY, byhour=byhour, interval=interval,

                            byminute=0, bysecond=0)

        super().__init__(rule, tz=tz)





class MinuteLocator(RRuleLocator):

    

    def __init__(self, byminute=None, interval=1, tz=None):

        

        if byminute is None:

            byminute = range(60)



        rule = rrulewrapper(MINUTELY, byminute=byminute, interval=interval,

                            bysecond=0)

        super().__init__(rule, tz=tz)





class SecondLocator(RRuleLocator):

    

    def __init__(self, bysecond=None, interval=1, tz=None):

        

        if bysecond is None:

            bysecond = range(60)



        rule = rrulewrapper(SECONDLY, bysecond=bysecond, interval=interval)

        super().__init__(rule, tz=tz)





class MicrosecondLocator(DateLocator):

    

    def __init__(self, interval=1, tz=None):

        

        super().__init__(tz=tz)

        self._interval = interval

        self._wrapped_locator = ticker.MultipleLocator(interval)



    def set_axis(self, axis):

        self._wrapped_locator.set_axis(axis)

        return super().set_axis(axis)



    def __call__(self):

                                                                    

        try:

            dmin, dmax = self.viewlim_to_dt()

        except ValueError:

            return []



        return self.tick_values(dmin, dmax)



    def tick_values(self, vmin, vmax):

        nmin, nmax = date2num((vmin, vmax))

        t0 = np.floor(nmin)

        nmax = nmax - t0

        nmin = nmin - t0

        nmin *= MUSECONDS_PER_DAY

        nmax *= MUSECONDS_PER_DAY



        ticks = self._wrapped_locator.tick_values(nmin, nmax)



        ticks = ticks / MUSECONDS_PER_DAY + t0

        return ticks



    def _get_unit(self):

                             

        return 1. / MUSECONDS_PER_DAY



    def _get_interval(self):

                             

        return self._interval





class DateConverter(units.ConversionInterface):

    



    def __init__(self, *, interval_multiples=True):

        self._interval_multiples = interval_multiples

        super().__init__()



    def axisinfo(self, unit, axis):

        

        tz = unit



        majloc = AutoDateLocator(tz=tz,

                                 interval_multiples=self._interval_multiples)

        majfmt = AutoDateFormatter(majloc, tz=tz)

        datemin = datetime.date(1970, 1, 1)

        datemax = datetime.date(1970, 1, 2)



        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label='',

                              default_limits=(datemin, datemax))



    @staticmethod

    def convert(value, unit, axis):

        

        return date2num(value)



    @staticmethod

    def default_units(x, axis):

        

        if isinstance(x, np.ndarray):

            x = x.ravel()



        try:

            x = cbook._safe_first_finite(x)

        except (TypeError, StopIteration):

            pass



        try:

            return x.tzinfo

        except AttributeError:

            pass

        return None





class ConciseDateConverter(DateConverter):

                         



    def __init__(self, formats=None, zero_formats=None, offset_formats=None,

                 show_offset=True, *, interval_multiples=True):

        self._formats = formats

        self._zero_formats = zero_formats

        self._offset_formats = offset_formats

        self._show_offset = show_offset

        self._interval_multiples = interval_multiples

        super().__init__()



    def axisinfo(self, unit, axis):

                             

        tz = unit

        majloc = AutoDateLocator(tz=tz,

                                 interval_multiples=self._interval_multiples)

        majfmt = ConciseDateFormatter(majloc, tz=tz, formats=self._formats,

                                      zero_formats=self._zero_formats,

                                      offset_formats=self._offset_formats,

                                      show_offset=self._show_offset)

        datemin = datetime.date(1970, 1, 1)

        datemax = datetime.date(1970, 1, 2)

        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label='',

                              default_limits=(datemin, datemax))





class _SwitchableDateConverter:

    



    @staticmethod

    def _get_converter():

        converter_cls = {

            "concise": ConciseDateConverter, "auto": DateConverter}[

                mpl.rcParams["date.converter"]]

        interval_multiples = mpl.rcParams["date.interval_multiples"]

        return converter_cls(interval_multiples=interval_multiples)



    def axisinfo(self, *args, **kwargs):

        return self._get_converter().axisinfo(*args, **kwargs)



    def default_units(self, *args, **kwargs):

        return self._get_converter().default_units(*args, **kwargs)



    def convert(self, *args, **kwargs):

        return self._get_converter().convert(*args, **kwargs)





units.registry[np.datetime64] =
    units.registry[datetime.date] =
    units.registry[datetime.datetime] =
    _SwitchableDateConverter()


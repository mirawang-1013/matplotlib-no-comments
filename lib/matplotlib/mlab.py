



import functools

from numbers import Integral, Number

import sys



import numpy as np



from matplotlib import _api, _docstring, cbook





def window_hanning(x):

    

    return np.hanning(len(x))*x





def window_none(x):

    

    return x





def detrend(x, key=None, axis=None):

    

    if key is None or key in ['constant', 'mean', 'default']:

        return detrend(x, key=detrend_mean, axis=axis)

    elif key == 'linear':

        return detrend(x, key=detrend_linear, axis=axis)

    elif key == 'none':

        return detrend(x, key=detrend_none, axis=axis)

    elif callable(key):

        x = np.asarray(x)

        if axis is not None and axis + 1 > x.ndim:

            raise ValueError(f'axis(={axis}) out of bounds')

        if (axis is None and x.ndim == 0) or (not axis and x.ndim == 1):

            return key(x)

                                                                     

                                                 

        try:

            return key(x, axis=axis)

        except TypeError:

            return np.apply_along_axis(key, axis=axis, arr=x)

    else:

        raise ValueError(

            f"Unknown value for key: {key!r}, must be one of: 'default', "

            f"'constant', 'mean', 'linear', or a function")





def detrend_mean(x, axis=None):

    

    x = np.asarray(x)



    if axis is not None and axis+1 > x.ndim:

        raise ValueError('axis(=%s) out of bounds' % axis)



    return x - x.mean(axis, keepdims=True)





def detrend_none(x, axis=None):

    

    return x





def detrend_linear(y):

    

                                                             

    y = np.asarray(y)



    if y.ndim > 1:

        raise ValueError('y cannot have ndim > 1')



                              

    if not y.ndim:

        return np.array(0., dtype=y.dtype)



    x = np.arange(y.size, dtype=float)



    C = np.cov(x, y, bias=1)

    b = C[0, 1]/C[0, 0]



    a = y.mean() - b*x.mean()

    return y - (b*x + a)





def _stride_windows(x, n, noverlap=0):

    _api.check_isinstance(Integral, n=n, noverlap=noverlap)

    x = np.asarray(x)

    step = n - noverlap

    shape = (n, (x.shape[-1]-noverlap)//step)

    strides = (x.strides[0], step*x.strides[0])

    return np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)





def _spectral_helper(x, y=None, NFFT=None, Fs=None, detrend_func=None,

                     window=None, noverlap=None, pad_to=None,

                     sides=None, scale_by_freq=None, mode=None):

    

    if y is None:

                                  

        same_data = True

    else:

                                                                              

                                                                             

                                                                          

        same_data = y is x



    if Fs is None:

        Fs = 2

    if noverlap is None:

        noverlap = 0

    if detrend_func is None:

        detrend_func = detrend_none

    if window is None:

        window = window_hanning



                                                 

    if NFFT is None:

        NFFT = 256



    if not (0 <= noverlap < NFFT):

        raise ValueError('noverlap must be less than NFFT')



    if mode is None or mode == 'default':

        mode = 'psd'

    _api.check_in_list(

        ['default', 'psd', 'complex', 'magnitude', 'angle', 'phase'],

        mode=mode)



    if not same_data and mode != 'psd':

        raise ValueError("x and y must be equal if mode is not 'psd'")



                                                                          

                                              

    x = np.asarray(x)

    if not same_data:

        y = np.asarray(y)



    if sides is None or sides == 'default':

        if np.iscomplexobj(x):

            sides = 'twosided'

        else:

            sides = 'onesided'

    _api.check_in_list(['default', 'onesided', 'twosided'], sides=sides)



                                                               

    if len(x) < NFFT:

        n = len(x)

        x = np.resize(x, NFFT)

        x[n:] = 0



    if not same_data and len(y) < NFFT:

        n = len(y)

        y = np.resize(y, NFFT)

        y[n:] = 0



    if pad_to is None:

        pad_to = NFFT



    if mode != 'psd':

        scale_by_freq = False

    elif scale_by_freq is None:

        scale_by_freq = True



                                                                       

    if sides == 'twosided':

        numFreqs = pad_to

        if pad_to % 2:

            freqcenter = (pad_to - 1)//2 + 1

        else:

            freqcenter = pad_to//2

        scaling_factor = 1.

    elif sides == 'onesided':

        if pad_to % 2:

            numFreqs = (pad_to + 1)//2

        else:

            numFreqs = pad_to//2 + 1

        scaling_factor = 2.



    if not np.iterable(window):

        window = window(np.ones(NFFT, x.dtype))

    if len(window) != NFFT:

        raise ValueError(

            "The window length must match the data's first dimension")



    if sys.maxsize > 2**32:

        result = np.lib.stride_tricks.sliding_window_view(

            x, NFFT, axis=0)[::NFFT - noverlap].T

    else:

                                                                          

        result = _stride_windows(x, NFFT, noverlap=noverlap)

    result = detrend(result, detrend_func, axis=0)

    result = result * window.reshape((-1, 1))

    result = np.fft.fft(result, n=pad_to, axis=0)[:numFreqs, :]

    freqs = np.fft.fftfreq(pad_to, 1/Fs)[:numFreqs]



    if not same_data:

                                                   

        if sys.maxsize > 2**32:

            resultY = np.lib.stride_tricks.sliding_window_view(

                y, NFFT, axis=0)[::NFFT - noverlap].T

        else:

                                                                              

            resultY = _stride_windows(y, NFFT, noverlap=noverlap)

        resultY = detrend(resultY, detrend_func, axis=0)

        resultY = resultY * window.reshape((-1, 1))

        resultY = np.fft.fft(resultY, n=pad_to, axis=0)[:numFreqs, :]

        result = np.conj(result) * resultY

    elif mode == 'psd':

        result = np.conj(result) * result

    elif mode == 'magnitude':

        result = np.abs(result) / window.sum()

    elif mode == 'angle' or mode == 'phase':

                                                                            

        result = np.angle(result)

    elif mode == 'complex':

        result /= window.sum()



    if mode == 'psd':



                                                                              

                                                                             

                                             



                                                                     

        if not NFFT % 2:

            slc = slice(1, -1, None)

                                                       

        else:

            slc = slice(1, None, None)



        result[slc] *= scaling_factor



                                                                           

                                                                           

                                                

        if scale_by_freq:

            result /= Fs

                                                                            

                                                              

            result /= (window**2).sum()

        else:

                                                                        

            result /= window.sum()**2



    t = np.arange(NFFT/2, len(x) - NFFT/2 + 1, NFFT - noverlap)/Fs



    if sides == 'twosided':

                                            

        freqs = np.roll(freqs, -freqcenter, axis=0)

        result = np.roll(result, -freqcenter, axis=0)

    elif not pad_to % 2:

                                                                

        freqs[-1] *= -1



                                                                       

    if mode == 'phase':

        result = np.unwrap(result, axis=0)



    return result, freqs, t





def _single_spectrum_helper(

        mode, x, Fs=None, window=None, pad_to=None, sides=None):

    

    _api.check_in_list(['complex', 'magnitude', 'angle', 'phase'], mode=mode)



    if pad_to is None:

        pad_to = len(x)



    spec, freqs, _ = _spectral_helper(x=x, y=None, NFFT=len(x), Fs=Fs,

                                      detrend_func=detrend_none, window=window,

                                      noverlap=0, pad_to=pad_to,

                                      sides=sides,

                                      scale_by_freq=False,

                                      mode=mode)

    if mode != 'complex':

        spec = spec.real



    if spec.ndim == 2 and spec.shape[1] == 1:

        spec = spec[:, 0]



    return spec, freqs





                                                                 

_docstring.interpd.register(

    Spectral="""\
Fs : float, default: 2
    The sampling frequency (samples per time unit).  It is used to calculate
    the Fourier frequencies, *freqs*, in cycles per time unit.

window : callable or ndarray, default: `.window_hanning`
    A function or a vector of length *NFFT*.  To create window vectors see
    `.window_hanning`, `.window_none`, `numpy.blackman`, `numpy.hamming`,
    `numpy.bartlett`, `scipy.signal`, `scipy.signal.get_window`, etc.  If a
    function is passed as the argument, it must take a data segment as an
    argument and return the windowed version of the segment.

sides : {'default', 'onesided', 'twosided'}, optional
    Which sides of the spectrum to return. 'default' is one-sided for real
    data and two-sided for complex data. 'onesided' forces the return of a
    one-sided spectrum, while 'twosided' forces two-sided.""",



    Single_Spectrum="""\
pad_to : int, optional
    The number of points to which the data segment is padded when performing
    the FFT.  While not increasing the actual resolution of the spectrum (the
    minimum distance between resolvable peaks), this can give more points in
    the plot, allowing for more detail. This corresponds to the *n* parameter
    in the call to `~numpy.fft.fft`.  The default is None, which sets *pad_to*
    equal to the length of the input signal (i.e. no padding).""",



    PSD="""\
pad_to : int, optional
    The number of points to which the data segment is padded when performing
    the FFT.  This can be different from *NFFT*, which specifies the number
    of data points used.  While not increasing the actual resolution of the
    spectrum (the minimum distance between resolvable peaks), this can give
    more points in the plot, allowing for more detail. This corresponds to
    the *n* parameter in the call to `~numpy.fft.fft`. The default is None,
    which sets *pad_to* equal to *NFFT*

NFFT : int, default: 256
    The number of data points used in each block for the FFT.  A power 2 is
    most efficient.  This should *NOT* be used to get zero padding, or the
    scaling of the result will be incorrect; use *pad_to* for this instead.

detrend : {'none', 'mean', 'linear'} or callable, default: 'none'
    The function applied to each segment before fft-ing, designed to remove
    the mean or linear trend.  Unlike in MATLAB, where the *detrend* parameter
    is a vector, in Matplotlib it is a function.  The :mod:`~matplotlib.mlab`
    module defines `.detrend_none`, `.detrend_mean`, and `.detrend_linear`,
    but you can use a custom function as well.  You can also use a string to
    choose one of the functions: 'none' calls `.detrend_none`. 'mean' calls
    `.detrend_mean`. 'linear' calls `.detrend_linear`.

scale_by_freq : bool, default: True
    Whether the resulting density values should be scaled by the scaling
    frequency, which gives density in units of 1/Hz.  This allows for
    integration over the returned frequency values.  The default is True for
    MATLAB compatibility.""")





@_docstring.interpd

def psd(x, NFFT=None, Fs=None, detrend=None, window=None,

        noverlap=None, pad_to=None, sides=None, scale_by_freq=None):

    

    Pxx, freqs = csd(x=x, y=None, NFFT=NFFT, Fs=Fs, detrend=detrend,

                     window=window, noverlap=noverlap, pad_to=pad_to,

                     sides=sides, scale_by_freq=scale_by_freq)

    return Pxx.real, freqs





@_docstring.interpd

def csd(x, y, NFFT=None, Fs=None, detrend=None, window=None,

        noverlap=None, pad_to=None, sides=None, scale_by_freq=None):

    

    if NFFT is None:

        NFFT = 256

    Pxy, freqs, _ = _spectral_helper(x=x, y=y, NFFT=NFFT, Fs=Fs,

                                     detrend_func=detrend, window=window,

                                     noverlap=noverlap, pad_to=pad_to,

                                     sides=sides, scale_by_freq=scale_by_freq,

                                     mode='psd')



    if Pxy.ndim == 2:

        if Pxy.shape[1] > 1:

            Pxy = Pxy.mean(axis=1)

        else:

            Pxy = Pxy[:, 0]

    return Pxy, freqs





_single_spectrum_docs = """\
Compute the {quantity} of *x*.
Data is padded to a length of *pad_to* and the windowing function *window* is
applied to the signal.

Parameters
----------
x : 1-D array or sequence
    Array or sequence containing the data

{Spectral}

{Single_Spectrum}

Returns
-------
spectrum : 1-D array
    The {quantity}.
freqs : 1-D array
    The frequencies corresponding to the elements in *spectrum*.

See Also
--------
psd
    Returns the power spectral density.
complex_spectrum
    Returns the complex-valued frequency spectrum.
magnitude_spectrum
    Returns the absolute value of the `complex_spectrum`.
angle_spectrum
    Returns the angle of the `complex_spectrum`.
phase_spectrum
    Returns the phase (unwrapped angle) of the `complex_spectrum`.
specgram
    Can return the complex spectrum of segments within the signal.
"""





complex_spectrum = functools.partial(_single_spectrum_helper, "complex")

complex_spectrum.__doc__ = _single_spectrum_docs.format(

    quantity="complex-valued frequency spectrum",

    **_docstring.interpd.params)

magnitude_spectrum = functools.partial(_single_spectrum_helper, "magnitude")

magnitude_spectrum.__doc__ = _single_spectrum_docs.format(

    quantity="magnitude (absolute value) of the frequency spectrum",

    **_docstring.interpd.params)

angle_spectrum = functools.partial(_single_spectrum_helper, "angle")

angle_spectrum.__doc__ = _single_spectrum_docs.format(

    quantity="angle of the frequency spectrum (wrapped phase spectrum)",

    **_docstring.interpd.params)

phase_spectrum = functools.partial(_single_spectrum_helper, "phase")

phase_spectrum.__doc__ = _single_spectrum_docs.format(

    quantity="phase of the frequency spectrum (unwrapped phase spectrum)",

    **_docstring.interpd.params)





@_docstring.interpd

def specgram(x, NFFT=None, Fs=None, detrend=None, window=None,

             noverlap=None, pad_to=None, sides=None, scale_by_freq=None,

             mode=None):

    

    if noverlap is None:

        noverlap = 128                                                 

    if NFFT is None:

        NFFT = 256                                         

    if len(x) <= NFFT:

        _api.warn_external("Only one segment is calculated since parameter "

                           f"NFFT (={NFFT}) >= signal length (={len(x)}).")



    spec, freqs, t = _spectral_helper(x=x, y=None, NFFT=NFFT, Fs=Fs,

                                      detrend_func=detrend, window=window,

                                      noverlap=noverlap, pad_to=pad_to,

                                      sides=sides,

                                      scale_by_freq=scale_by_freq,

                                      mode=mode)



    if mode != 'complex':

        spec = spec.real                                              



    return spec, freqs, t





@_docstring.interpd

def cohere(x, y, NFFT=256, Fs=2, detrend=detrend_none, window=window_hanning,

           noverlap=0, pad_to=None, sides='default', scale_by_freq=None):

    

    if len(x) < 2 * NFFT:

        raise ValueError(

            "Coherence is calculated by averaging over *NFFT* length "

            "segments.  Your signal is too short for your choice of *NFFT*.")

    Pxx, f = psd(x, NFFT, Fs, detrend, window, noverlap, pad_to, sides,

                 scale_by_freq)

    Pyy, f = psd(y, NFFT, Fs, detrend, window, noverlap, pad_to, sides,

                 scale_by_freq)

    Pxy, f = csd(x, y, NFFT, Fs, detrend, window, noverlap, pad_to, sides,

                 scale_by_freq)

    Cxy = np.abs(Pxy) ** 2 / (Pxx * Pyy)

    return Cxy, f





class GaussianKDE:

    



                                                                          

                                                                               



    def __init__(self, dataset, bw_method=None):

        self.dataset = np.atleast_2d(dataset)

        if not np.array(self.dataset).size > 1:

            raise ValueError("`dataset` input should have multiple elements.")



        self.dim, self.num_dp = np.array(self.dataset).shape



        if bw_method is None:

            pass

        elif cbook._str_equal(bw_method, 'scott'):

            self.covariance_factor = self.scotts_factor

        elif cbook._str_equal(bw_method, 'silverman'):

            self.covariance_factor = self.silverman_factor

        elif isinstance(bw_method, Number):

            self._bw_method = 'use constant'

            self.covariance_factor = lambda: bw_method

        elif callable(bw_method):

            self._bw_method = bw_method

            self.covariance_factor = lambda: self._bw_method(self)

        else:

            raise ValueError("`bw_method` should be 'scott', 'silverman', a "

                             "scalar or a callable")



                                                                       

                              



        self.factor = self.covariance_factor()

                                                             

        if not hasattr(self, '_data_inv_cov'):

            self.data_covariance = np.atleast_2d(

                np.cov(

                    self.dataset,

                    rowvar=1,

                    bias=False))

            self.data_inv_cov = np.linalg.inv(self.data_covariance)



        self.covariance = self.data_covariance * self.factor ** 2

        self.inv_cov = self.data_inv_cov / self.factor ** 2

        self.norm_factor = (np.sqrt(np.linalg.det(2 * np.pi * self.covariance))

                            * self.num_dp)



    def scotts_factor(self):

        return np.power(self.num_dp, -1. / (self.dim + 4))



    def silverman_factor(self):

        return np.power(

            self.num_dp * (self.dim + 2.0) / 4.0, -1. / (self.dim + 4))



                                                                            

    covariance_factor = scotts_factor



    def evaluate(self, points):

        

        points = np.atleast_2d(points)



        dim, num_m = np.array(points).shape

        if dim != self.dim:

            raise ValueError(f"points have dimension {dim}, dataset has "

                             f"dimension {self.dim}")



        result = np.zeros(num_m)



        if num_m >= self.num_dp:

                                                                

            for i in range(self.num_dp):

                diff = self.dataset[:, i, np.newaxis] - points

                tdiff = np.dot(self.inv_cov, diff)

                energy = np.sum(diff * tdiff, axis=0) / 2.0

                result = result + np.exp(-energy)

        else:

                              

            for i in range(num_m):

                diff = self.dataset - points[:, i, np.newaxis]

                tdiff = np.dot(self.inv_cov, diff)

                energy = np.sum(diff * tdiff, axis=0) / 2.0

                result[i] = np.sum(np.exp(-energy), axis=0)



        result = result / self.norm_factor



        return result



    __call__ = evaluate


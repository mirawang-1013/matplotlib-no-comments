



import atexit

import functools

import hashlib

import logging

import os

from pathlib import Path

import shutil

import subprocess

import sys

from tempfile import TemporaryDirectory, TemporaryFile

import weakref

import re



import numpy as np

from PIL import Image



import matplotlib as mpl

from matplotlib import cbook, _image

from matplotlib.testing.exceptions import ImageComparisonFailure



_log = logging.getLogger(__name__)



__all__ = ['calculate_rms', 'comparable_formats', 'compare_images']





def make_test_filename(fname, purpose):

    

    base, ext = os.path.splitext(fname)

    return f'{base}-{purpose}{ext}'





def _get_cache_path():

    cache_dir = Path(mpl.get_cachedir(), 'test_cache')

    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir





def get_cache_dir():

    return str(_get_cache_path())





def get_file_hash(path, block_size=2 ** 20):

    sha256 = hashlib.sha256(usedforsecurity=False)

    with open(path, 'rb') as fd:

        while True:

            data = fd.read(block_size)

            if not data:

                break

            sha256.update(data)



    if Path(path).suffix == '.pdf':

        sha256.update(str(mpl._get_executable_info("gs").version).encode('utf-8'))

    elif Path(path).suffix == '.svg':

        sha256.update(str(mpl._get_executable_info("inkscape").version).encode('utf-8'))



    return sha256.hexdigest()





class _ConverterError(Exception):

    pass





class _Converter:

    def __init__(self):

        self._proc = None

                                                                           

                                                                              

                                                                         

                                        

        atexit.register(self.__del__)



    def __del__(self):

        if self._proc:

            self._proc.kill()

            self._proc.wait()

            for stream in filter(None, [self._proc.stdin,

                                        self._proc.stdout,

                                        self._proc.stderr]):

                stream.close()

            self._proc = None



    def _read_until(self, terminator):

        

        buf = bytearray()

        while True:

            c = self._proc.stdout.read(1)

            if not c:

                raise _ConverterError(os.fsdecode(bytes(buf)))

            buf.extend(c)

            if buf.endswith(terminator):

                return bytes(buf)





class _MagickConverter:

    def __call__(self, orig, dest):

        try:

            subprocess.run(

                [mpl._get_executable_info("magick").executable, orig, dest],

                check=True)

        except subprocess.CalledProcessError as e:

            raise _ConverterError() from e





class _GSConverter(_Converter):

    def __call__(self, orig, dest):

        if not self._proc:

            self._proc = subprocess.Popen(

                [mpl._get_executable_info("gs").executable,

                 "-dNOSAFER", "-dNOPAUSE", "-dEPSCrop", "-sDEVICE=png16m"],

                                                                           

                stdin=subprocess.PIPE, stdout=subprocess.PIPE)

            try:

                self._read_until(b"\nGS")

            except _ConverterError as e:

                raise OSError(f"Failed to start Ghostscript:\n\n{e.args[0]}") from None



        def encode_and_escape(name):

            return (os.fsencode(name)

                    .replace(b"\\", b"\\\\")

                    .replace(b"(", br"\(")

                    .replace(b")", br"\)"))



        self._proc.stdin.write(

            b"<< /OutputFile ("

            + encode_and_escape(dest)

            + b") >> setpagedevice ("

            + encode_and_escape(orig)

            + b") run flush\n")

        self._proc.stdin.flush()

                                                                               

        err = self._read_until((b"GS<", b"GS>"))

        stack = self._read_until(b">") if err.endswith(b"GS<") else b""

        if stack or not os.path.exists(dest):

            stack_size = int(stack[:-1]) if stack else 0

            self._proc.stdin.write(b"pop\n" * stack_size)

                                                                               

            raise ImageComparisonFailure(

                (err + stack).decode(sys.getfilesystemencoding(), "replace"))





class _SVGConverter(_Converter):

    def __call__(self, orig, dest):

        old_inkscape = mpl._get_executable_info("inkscape").version.major < 1

        terminator = b"\n>" if old_inkscape else b"> "

        if not hasattr(self, "_tmpdir"):

            self._tmpdir = TemporaryDirectory()

                                                                          

                                                           

            weakref.finalize(self._tmpdir, self.__del__)

        if (not self._proc              

                or self._proc.poll() is not None):                        

            if self._proc is not None and self._proc.poll() is not None:

                for stream in filter(None, [self._proc.stdin,

                                            self._proc.stdout,

                                            self._proc.stderr]):

                    stream.close()

            env = {

                **os.environ,

                                                                           

                                                                            

                                                                           

                                                                            

                                                                 

                "DISPLAY": "",

                                               

                "INKSCAPE_PROFILE_DIR": self._tmpdir.name,

            }

                                                                        

                                                                             

                                                                               

                              

            stderr = TemporaryFile()

            self._proc = subprocess.Popen(

                ["inkscape", "--without-gui", "--shell"] if old_inkscape else

                ["inkscape", "--shell"],

                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,

                env=env, cwd=self._tmpdir.name)

                                                               

            self._proc.stderr = stderr

            try:

                self._read_until(terminator)

            except _ConverterError as err:

                raise OSError(

                    "Failed to start Inkscape in interactive mode:\n\n"

                    + err.args[0]) from err



                                                                               

                                                                           

                                                                       

        inkscape_orig = Path(self._tmpdir.name, os.fsdecode(b"f.svg"))

        inkscape_dest = Path(self._tmpdir.name, os.fsdecode(b"f.png"))

        try:

            inkscape_orig.symlink_to(Path(orig).resolve())

        except OSError:

            shutil.copyfile(orig, inkscape_orig)

        self._proc.stdin.write(

            b"f.svg --export-png=f.png\n" if old_inkscape else

            b"file-open:f.svg;export-filename:f.png;export-do;file-close\n")

        self._proc.stdin.flush()

        try:

            self._read_until(terminator)

        except _ConverterError as err:

                                                                            

                                                                         

                                                                 

            self._proc.stderr.seek(0)

            raise ImageComparisonFailure(

                self._proc.stderr.read().decode(

                    sys.getfilesystemencoding(), "replace")) from err

        os.remove(inkscape_orig)

        shutil.move(inkscape_dest, dest)



    def __del__(self):

        super().__del__()

        if hasattr(self, "_tmpdir"):

            self._tmpdir.cleanup()





class _SVGWithMatplotlibFontsConverter(_SVGConverter):

    



    def __call__(self, orig, dest):

        if not hasattr(self, "_tmpdir"):

            self._tmpdir = TemporaryDirectory()

            shutil.copytree(cbook._get_data_path("fonts/ttf"),

                            Path(self._tmpdir.name, "fonts"))

        return super().__call__(orig, dest)





def _update_converter():

    try:

        mpl._get_executable_info("magick")

    except mpl.ExecutableNotFoundError:

        pass

    else:

        converter['gif'] = _MagickConverter()

    try:

        mpl._get_executable_info("gs")

    except mpl.ExecutableNotFoundError:

        pass

    else:

        converter['pdf'] = converter['eps'] = _GSConverter()

    try:

        mpl._get_executable_info("inkscape")

    except mpl.ExecutableNotFoundError:

        pass

    else:

        converter['svg'] = _SVGConverter()





                                                                           

                                                         

converter = {}

_update_converter()

_svg_with_matplotlib_fonts_converter = _SVGWithMatplotlibFontsConverter()





def comparable_formats():

    

    return ['png', *converter]





def convert(filename, cache):

    

    path = Path(filename)

    if not path.exists():

        raise OSError(f"{path} does not exist")

    if path.suffix[1:] not in converter:

        import pytest

        pytest.skip(f"Don't know how to convert {path.suffix} files to png")

    newpath = path.parent / f"{path.stem}_{path.suffix[1:]}.png"



                                                                       

                     

    if not newpath.exists() or newpath.stat().st_mtime < path.stat().st_mtime:

        cache_dir = _get_cache_path() if cache else None



        if cache_dir is not None:

            _register_conversion_cache_cleaner_once()

            hash_value = get_file_hash(path)

            cached_path = cache_dir / (hash_value + newpath.suffix)

            if cached_path.exists():

                _log.debug("For %s: reusing cached conversion.", filename)

                shutil.copyfile(cached_path, newpath)

                return str(newpath)



        _log.debug("For %s: converting to png.", filename)

        convert = converter[path.suffix[1:]]

        if path.suffix == ".svg":

            contents = path.read_text(encoding="utf-8")

                                                                          

                                                                                      

                                                                                     

                                                                                 

                                                          

            if re.search(

                                           

                                                      

                                                               

                                                                             

                                                        

                r'style="[^"]*font(|-size|-weight|-family|-variant|-style):',

                contents                                

                    ):

                                                                              

                                                                     

                convert = _svg_with_matplotlib_fonts_converter

        convert(path, newpath)



        if cache_dir is not None:

            _log.debug("For %s: caching conversion result.", filename)

            shutil.copyfile(newpath, cached_path)



    return str(newpath)





def _clean_conversion_cache():

                                                                         

                       

    baseline_images_size = sum(

        path.stat().st_size

        for path in Path(mpl.__file__).parent.glob("**/baseline_images/**/*"))

                                                                       

                                                                             

    max_cache_size = 2 * baseline_images_size

                                 

    with cbook._lock_path(_get_cache_path()):

        cache_stat = {

            path: path.stat() for path in _get_cache_path().glob("*")}

        cache_size = sum(stat.st_size for stat in cache_stat.values())

        paths_by_atime = sorted(                      

            cache_stat, key=lambda path: cache_stat[path].st_atime,

            reverse=True)

        while cache_size > max_cache_size:

            path = paths_by_atime.pop()

            cache_size -= cache_stat[path].st_size

            path.unlink()





@functools.cache                                        

def _register_conversion_cache_cleaner_once():

    atexit.register(_clean_conversion_cache)





def crop_to_same(actual_path, actual_image, expected_path, expected_image):

                                                                  

                          

    if actual_path[-7:-4] == 'eps' and expected_path[-7:-4] == 'pdf':

        aw, ah, ad = actual_image.shape

        ew, eh, ed = expected_image.shape

        actual_image = actual_image[int(aw / 2 - ew / 2):int(

            aw / 2 + ew / 2), int(ah / 2 - eh / 2):int(ah / 2 + eh / 2)]

    return actual_image, expected_image





def calculate_rms(expected_image, actual_image):

    

    if expected_image.shape != actual_image.shape:

        raise ImageComparisonFailure(

            f"Image sizes do not match expected size: {expected_image.shape} "

            f"actual size {actual_image.shape}")

                                                                 

    return np.sqrt(((expected_image - actual_image).astype(float) ** 2).mean())





                                                                             

                                                            





def _load_image(path):

    img = Image.open(path)

                                                                              

                                                                        

                                                                             

    if img.mode != "RGBA" or img.getextrema()[3][0] == 255:

        img = img.convert("RGB")

    return np.asarray(img)





def compare_images(expected, actual, tol, in_decorator=False):

    

    actual = os.fspath(actual)

    if not os.path.exists(actual):

        raise Exception(f"Output image {actual} does not exist.")

    if os.stat(actual).st_size == 0:

        raise Exception(f"Output image file {actual} is empty.")



                              

    expected = os.fspath(expected)

    if not os.path.exists(expected):

        raise OSError(f'Baseline image {expected!r} does not exist.')

    extension = expected.split('.')[-1]

    if extension != 'png':

        actual = convert(actual, cache=True)

        expected = convert(expected, cache=True)



                          

    expected_image = _load_image(expected)

    actual_image = _load_image(actual)



    actual_image, expected_image = crop_to_same(

        actual, actual_image, expected, expected_image)



    diff_image = make_test_filename(actual, 'failed-diff')



    if tol <= 0:

        if np.array_equal(expected_image, actual_image):

            return None



    rms, abs_diff = _image.calculate_rms_and_diff(expected_image, actual_image)



    if rms <= tol:

        return None



    Image.fromarray(abs_diff).save(diff_image, format="png")



    results = dict(rms=rms, expected=str(expected),

                   actual=str(actual), diff=str(diff_image), tol=tol)



    if not in_decorator:

                                                                  

        template = ['Error: Image files did not match.',

                    'RMS Value: {rms}',

                    'Expected:  \n    {expected}',

                    'Actual:    \n    {actual}',

                    'Difference:\n    {diff}',

                    'Tolerance: \n    {tol}', ]

        results = '\n  '.join([line.format(**results) for line in template])

    return results





def save_diff_image(expected, actual, output):

    

    expected_image = _load_image(expected)

    actual_image = _load_image(actual)

    actual_image, expected_image = crop_to_same(

        actual, actual_image, expected, expected_image)

    expected_image = np.array(expected_image, float)

    actual_image = np.array(actual_image, float)

    if expected_image.shape != actual_image.shape:

        raise ImageComparisonFailure(

            f"Image sizes do not match expected size: {expected_image.shape} "

            f"actual size {actual_image.shape}")

    abs_diff = np.abs(expected_image - actual_image)



                                            

    abs_diff *= 10

    abs_diff = np.clip(abs_diff, 0, 255).astype(np.uint8)



    if abs_diff.shape[2] == 4:                                              

        abs_diff[:, :, 3] = 255



    Image.fromarray(abs_diff).save(output, format="png")


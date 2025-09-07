import abc

import base64

import collections

import contextlib

from io import BytesIO, TextIOWrapper

import itertools

import logging

from pathlib import Path

import shutil

import subprocess

import sys

from tempfile import TemporaryDirectory

import uuid

import warnings



import numpy as np

from PIL import Image



import matplotlib as mpl

from matplotlib._animation_data import (

    DISPLAY_TEMPLATE, INCLUDED_FRAMES, JS_INCLUDE, STYLE_INCLUDE)

from matplotlib import _api, cbook

import matplotlib.colors as mcolors



_log = logging.getLogger(__name__)



                                                                       

                                                               

subprocess_creation_flags = (

    subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)





def adjusted_figsize(w, h, dpi, n):

    



                                                                      

                                         

    def correct_roundoff(x, dpi, n):

        if int(x*dpi) % n != 0:

            if int(np.nextafter(x, np.inf)*dpi) % n == 0:

                x = np.nextafter(x, np.inf)

            elif int(np.nextafter(x, -np.inf)*dpi) % n == 0:

                x = np.nextafter(x, -np.inf)

        return x



    wnew = int(w * dpi / n) * n / dpi

    hnew = int(h * dpi / n) * n / dpi

    return correct_roundoff(wnew, dpi, n), correct_roundoff(hnew, dpi, n)





class MovieWriterRegistry:

    



    def __init__(self):

        self._registered = dict()



    def register(self, name):

        

        def wrapper(writer_cls):

            self._registered[name] = writer_cls

            return writer_cls

        return wrapper



    def is_available(self, name):

        

        try:

            cls = self._registered[name]

        except KeyError:

            return False

        return cls.isAvailable()



    def __iter__(self):

        

        for name in self._registered:

            if self.is_available(name):

                yield name



    def list(self):

        

        return [*self]



    def __getitem__(self, name):

        

        if self.is_available(name):

            return self._registered[name]

        raise RuntimeError(f"Requested MovieWriter ({name}) not available")





writers = MovieWriterRegistry()





class AbstractMovieWriter(abc.ABC):

    



    def __init__(self, fps=5, metadata=None, codec=None, bitrate=None):

        self.fps = fps

        self.metadata = metadata if metadata is not None else {}

        self.codec = mpl._val_or_rc(codec, 'animation.codec')

        self.bitrate = mpl._val_or_rc(bitrate, 'animation.bitrate')



    @abc.abstractmethod

    def setup(self, fig, outfile, dpi=None):

        

                                  

        Path(outfile).parent.resolve(strict=True)

        self.outfile = outfile

        self.fig = fig

        if dpi is None:

            dpi = self.fig.dpi

        self.dpi = dpi



    @property

    def frame_size(self):

        

        w, h = self.fig.get_size_inches()

        return int(w * self.dpi), int(h * self.dpi)



    def _supports_transparency(self):

        

        return False



    @abc.abstractmethod

    def grab_frame(self, **savefig_kwargs):

        



    @abc.abstractmethod

    def finish(self):

        



    @contextlib.contextmanager

    def saving(self, fig, outfile, dpi, *args, **kwargs):

        

        if mpl.rcParams['savefig.bbox'] == 'tight':

            _log.info("Disabling savefig.bbox = 'tight', as it may cause "

                      "frame size to vary, which is inappropriate for "

                      "animation.")



                                                                          

        self.setup(fig, outfile, dpi, *args, **kwargs)

        with mpl.rc_context({'savefig.bbox': None}):

            try:

                yield self

            finally:

                self.finish()





class MovieWriter(AbstractMovieWriter):

    



                                                                               

                                                                           

                                                                            

                                                                               

                                    



                                                                            

              

    supported_formats = ["rgba"]



    def __init__(self, fps=5, codec=None, bitrate=None, extra_args=None,

                 metadata=None):

        

        if type(self) is MovieWriter:

                                                                         

                                                                          

                                                                         

                                    

            raise TypeError(

                'MovieWriter cannot be instantiated directly. Please use one '

                'of its subclasses.')



        super().__init__(fps=fps, metadata=metadata, codec=codec,

                         bitrate=bitrate)

        self.frame_format = self.supported_formats[0]

        self.extra_args = extra_args



    def _adjust_frame_size(self):

        if self.codec == 'h264':

            wo, ho = self.fig.get_size_inches()

            w, h = adjusted_figsize(wo, ho, self.dpi, 2)

            if (wo, ho) != (w, h):

                self.fig.set_size_inches(w, h, forward=True)

                _log.info('figure size in inches has been adjusted '

                          'from %s x %s to %s x %s', wo, ho, w, h)

        else:

            w, h = self.fig.get_size_inches()

        _log.debug('frame size in pixels is %s x %s', *self.frame_size)

        return w, h



    def setup(self, fig, outfile, dpi=None):

                             

        super().setup(fig, outfile, dpi=dpi)

        self._w, self._h = self._adjust_frame_size()

                                                                          

                                             

        self._run()



    def _run(self):

                                                                          

                                                                            

                                           

        command = self._args()

        _log.info('MovieWriter._run: running command: %s',

                  cbook._pformat_subprocess(command))

        PIPE = subprocess.PIPE

        self._proc = subprocess.Popen(

            command, stdin=PIPE, stdout=PIPE, stderr=PIPE,

            creationflags=subprocess_creation_flags)



    def finish(self):

        

        out, err = self._proc.communicate()

                                                                    

        out = TextIOWrapper(BytesIO(out)).read()

        err = TextIOWrapper(BytesIO(err)).read()

        if out:

            _log.log(

                logging.WARNING if self._proc.returncode else logging.DEBUG,

                "MovieWriter stdout:\n%s", out)

        if err:

            _log.log(

                logging.WARNING if self._proc.returncode else logging.DEBUG,

                "MovieWriter stderr:\n%s", err)

        if self._proc.returncode:

            raise subprocess.CalledProcessError(

                self._proc.returncode, self._proc.args, out, err)



    def grab_frame(self, **savefig_kwargs):

                             

        _validate_grabframe_kwargs(savefig_kwargs)

        _log.debug('MovieWriter.grab_frame: Grabbing frame.')

                                                                           

                                                                         

        self.fig.set_size_inches(self._w, self._h)

                                                                           

        self.fig.savefig(self._proc.stdin, format=self.frame_format,

                         dpi=self.dpi, **savefig_kwargs)



    def _args(self):

        

        return NotImplementedError("args needs to be implemented by subclass.")



    @classmethod

    def bin_path(cls):

        

        return str(mpl.rcParams[cls._exec_key])



    @classmethod

    def isAvailable(cls):

        

        return shutil.which(cls.bin_path()) is not None





class FileMovieWriter(MovieWriter):

    

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.frame_format = mpl.rcParams['animation.frame_format']



    def setup(self, fig, outfile, dpi=None, frame_prefix=None):

        

                                  

        Path(outfile).parent.resolve(strict=True)

        self.fig = fig

        self.outfile = outfile

        if dpi is None:

            dpi = self.fig.dpi

        self.dpi = dpi

        self._adjust_frame_size()



        if frame_prefix is None:

            self._tmpdir = TemporaryDirectory()

            self.temp_prefix = str(Path(self._tmpdir.name, 'tmp'))

        else:

            self._tmpdir = None

            self.temp_prefix = frame_prefix

        self._frame_counter = 0                                             

        self._temp_paths = list()

        self.fname_format_str = '%s%%07d.%s'



    def __del__(self):

        if hasattr(self, '_tmpdir') and self._tmpdir:

            self._tmpdir.cleanup()



    @property

    def frame_format(self):

        

        return self._frame_format



    @frame_format.setter

    def frame_format(self, frame_format):

        if frame_format in self.supported_formats:

            self._frame_format = frame_format

        else:

            _api.warn_external(

                f"Ignoring file format {frame_format!r} which is not "

                f"supported by {type(self).__name__}; using "

                f"{self.supported_formats[0]} instead.")

            self._frame_format = self.supported_formats[0]



    def _base_temp_name(self):

                                                                           

                                       

        return self.fname_format_str % (self.temp_prefix, self.frame_format)



    def grab_frame(self, **savefig_kwargs):

                             

                                                                   

        _validate_grabframe_kwargs(savefig_kwargs)

        path = Path(self._base_temp_name() % self._frame_counter)

        self._temp_paths.append(path)                                      

        self._frame_counter += 1                                        

        _log.debug('FileMovieWriter.grab_frame: Grabbing frame %d to path=%s',

                   self._frame_counter, path)

        with open(path, 'wb') as sink:                            

            self.fig.savefig(sink, format=self.frame_format, dpi=self.dpi,

                             **savefig_kwargs)



    def finish(self):

                                                                           

                                        

        try:

            self._run()

            super().finish()

        finally:

            if self._tmpdir:

                _log.debug(

                    'MovieWriter: clearing temporary path=%s', self._tmpdir

                )

                self._tmpdir.cleanup()





@writers.register('pillow')

class PillowWriter(AbstractMovieWriter):

    def _supports_transparency(self):

        return True



    @classmethod

    def isAvailable(cls):

        return True



    def setup(self, fig, outfile, dpi=None):

        super().setup(fig, outfile, dpi=dpi)

        self._frames = []



    def grab_frame(self, **savefig_kwargs):

        _validate_grabframe_kwargs(savefig_kwargs)

        buf = BytesIO()

        self.fig.savefig(

            buf, **{**savefig_kwargs, "format": "rgba", "dpi": self.dpi})

        im = Image.frombuffer(

            "RGBA", self.frame_size, buf.getbuffer(), "raw", "RGBA", 0, 1)

        if im.getextrema()[3][0] < 255:

                                                                      

            self._frames.append(im)

        else:

                                                                                     

                                                                                 

            self._frames.append(im.convert("RGB"))



    def finish(self):

        self._frames[0].save(

            self.outfile, save_all=True, append_images=self._frames[1:],

            duration=int(1000 / self.fps), loop=0)





                                                                          

                                                         

class FFMpegBase:

    



    _exec_key = 'animation.ffmpeg_path'

    _args_key = 'animation.ffmpeg_args'



    def _supports_transparency(self):

        suffix = Path(self.outfile).suffix

        if suffix in {'.apng', '.avif', '.gif', '.webm', '.webp'}:

            return True

                                                                                   

                                                                                     

                                                                                     

                                                                                   

                                                                          

        return self.codec in {

            'apng', 'avrp', 'bmp', 'cfhd', 'dpx', 'ffv1', 'ffvhuff', 'gif', 'huffyuv',

            'jpeg2000', 'ljpeg', 'png', 'prores', 'prores_aw', 'prores_ks', 'qtrle',

            'rawvideo', 'targa', 'tiff', 'utvideo', 'v408', }



    @property

    def output_args(self):

        args = []

        suffix = Path(self.outfile).suffix

        if suffix in {'.apng', '.avif', '.gif', '.webm', '.webp'}:

            self.codec = suffix[1:]

        else:

            args.extend(['-vcodec', self.codec])

        extra_args = (self.extra_args if self.extra_args is not None

                      else mpl.rcParams[self._args_key])

                                                                          

                                                                           

                                                                                

                                                                         

        if self.codec == 'h264' and '-pix_fmt' not in extra_args:

            args.extend(['-pix_fmt', 'yuv420p'])

                                                                              

                                                  

        elif self.codec == 'gif' and '-filter_complex' not in extra_args:

            args.extend(['-filter_complex',

                         'split [a][b];[a] palettegen [p];[b][p] paletteuse'])

                                                                                      

                                                                                  

        elif self.codec == 'avif' and '-filter_complex' not in extra_args:

            args.extend(['-filter_complex',

                         'split [rgb][rgba]; [rgba] alphaextract [alpha]',

                         '-map', '[rgb]', '-map', '[alpha]'])

        if self.bitrate > 0:

            args.extend(['-b', '%dk' % self.bitrate])                         

        for k, v in self.metadata.items():

            args.extend(['-metadata', f'{k}={v}'])

        args.extend(extra_args)



        return args + ['-y', self.outfile]





                                                

@writers.register('ffmpeg')

class FFMpegWriter(FFMpegBase, MovieWriter):

    

    def _args(self):

                                                                   

                                                

        args = [self.bin_path(), '-f', 'rawvideo', '-vcodec', 'rawvideo',

                '-s', '%dx%d' % self.frame_size, '-pix_fmt', self.frame_format,

                '-framerate', str(self.fps)]

                                                                             

                                                                          

                                                

        if _log.getEffectiveLevel() > logging.DEBUG:

            args += ['-loglevel', 'error']

        args += ['-i', 'pipe:'] + self.output_args

        return args





                                                     

@writers.register('ffmpeg_file')

class FFMpegFileWriter(FFMpegBase, FileMovieWriter):

    

    supported_formats = ['png', 'jpeg', 'tiff', 'raw', 'rgba']



    def _args(self):

                                                                   

                                                                    

        args = []

                                                                         

        if self.frame_format in {'raw', 'rgba'}:

            args += [

                '-f', 'image2', '-vcodec', 'rawvideo',

                '-video_size', '%dx%d' % self.frame_size,

                '-pixel_format', 'rgba',

            ]

        args += ['-framerate', str(self.fps), '-i', self._base_temp_name()]

        if not self._tmpdir:

            args += ['-frames:v', str(self._frame_counter)]

                                                                             

                                                                          

                                                

        if _log.getEffectiveLevel() > logging.DEBUG:

            args += ['-loglevel', 'error']

        return [self.bin_path(), *args, *self.output_args]





                                               

class ImageMagickBase:

    



    _exec_key = 'animation.convert_path'

    _args_key = 'animation.convert_args'



    def _supports_transparency(self):

        suffix = Path(self.outfile).suffix

        return suffix in {'.apng', '.avif', '.gif', '.webm', '.webp'}



    def _args(self):

                                               

        fmt = "rgba" if self.frame_format == "raw" else self.frame_format

        extra_args = (self.extra_args if self.extra_args is not None

                      else mpl.rcParams[self._args_key])

        return [

            self.bin_path(),

            "-size", "%ix%i" % self.frame_size,

            "-depth", "8",

            "-delay", str(100 / self.fps),

            "-loop", "0",

            f"{fmt}:{self.input_names}",

            *extra_args,

            self.outfile,

        ]



    @classmethod

    def bin_path(cls):

        binpath = super().bin_path()

        if binpath == 'convert':

            binpath = mpl._get_executable_info('magick').executable

        return binpath



    @classmethod

    def isAvailable(cls):

        try:

            return super().isAvailable()

        except mpl.ExecutableNotFoundError as _enf:

                                                   

            _log.debug('ImageMagick unavailable due to: %s', _enf)

            return False





                                                     

@writers.register('imagemagick')

class ImageMagickWriter(ImageMagickBase, MovieWriter):

    



    input_names = "-"         





                                                          

@writers.register('imagemagick_file')

class ImageMagickFileWriter(ImageMagickBase, FileMovieWriter):

    



    supported_formats = ['png', 'jpeg', 'tiff', 'raw', 'rgba']

    input_names = property(

        lambda self: f'{self.temp_prefix}*.{self.frame_format}')





                                                      

                                       

def _included_frames(frame_count, frame_format, frame_dir):

    return INCLUDED_FRAMES.format(Nframes=frame_count,

                                  frame_dir=frame_dir,

                                  frame_format=frame_format)





def _embedded_frames(frame_list, frame_format):

    

    if frame_format == 'svg':

                               

        frame_format = 'svg+xml'

    template = '  frames[{0}] = "data:image/{1};base64,{2}"\n'

    return "\n" + "".join(

        template.format(i, frame_format, frame_data.replace('\n', '\\\n'))

        for i, frame_data in enumerate(frame_list))





@writers.register('html')

class HTMLWriter(FileMovieWriter):

    



    supported_formats = ['png', 'jpeg', 'tiff', 'svg']



    @classmethod

    def isAvailable(cls):

        return True



    def __init__(self, fps=30, codec=None, bitrate=None, extra_args=None,

                 metadata=None, embed_frames=False, default_mode='loop',

                 embed_limit=None):



        if extra_args:

            _log.warning("HTMLWriter ignores 'extra_args'")

        extra_args = ()                                               

        self.embed_frames = embed_frames

        self.default_mode = default_mode.lower()

        _api.check_in_list(['loop', 'once', 'reflect'],

                           default_mode=self.default_mode)



                                                

        self._bytes_limit = mpl._val_or_rc(embed_limit, 'animation.embed_limit')

                                  

        self._bytes_limit *= 1024 * 1024



        super().__init__(fps, codec, bitrate, extra_args, metadata)



    def setup(self, fig, outfile, dpi=None, frame_dir=None):

        outfile = Path(outfile)

        _api.check_in_list(['.html', '.htm'], outfile_extension=outfile.suffix)



        self._saved_frames = []

        self._total_bytes = 0

        self._hit_limit = False



        if not self.embed_frames:

            if frame_dir is None:

                frame_dir = outfile.with_name(outfile.stem + '_frames')

            frame_dir.mkdir(parents=True, exist_ok=True)

            frame_prefix = frame_dir / 'frame'

        else:

            frame_prefix = None



        super().setup(fig, outfile, dpi, frame_prefix)

        self._clear_temp = False



    def grab_frame(self, **savefig_kwargs):

        _validate_grabframe_kwargs(savefig_kwargs)

        if self.embed_frames:

                                                      

            if self._hit_limit:

                return

            f = BytesIO()

            self.fig.savefig(f, format=self.frame_format,

                             dpi=self.dpi, **savefig_kwargs)

            imgdata64 = base64.encodebytes(f.getvalue()).decode('ascii')

            self._total_bytes += len(imgdata64)

            if self._total_bytes >= self._bytes_limit:

                _log.warning(

                    "Animation size has reached %s bytes, exceeding the limit "

                    "of %s. If you're sure you want a larger animation "

                    "embedded, set the animation.embed_limit rc parameter to "

                    "a larger value (in MB). This and further frames will be "

                    "dropped.", self._total_bytes, self._bytes_limit)

                self._hit_limit = True

            else:

                self._saved_frames.append(imgdata64)

        else:

            return super().grab_frame(**savefig_kwargs)



    def finish(self):

                                         

        if self.embed_frames:

            fill_frames = _embedded_frames(self._saved_frames,

                                           self.frame_format)

            frame_count = len(self._saved_frames)

        else:

                                                     

            frame_count = len(self._temp_paths)

            fill_frames = _included_frames(

                frame_count, self.frame_format,

                self._temp_paths[0].parent.relative_to(self.outfile.parent))

        mode_dict = dict(once_checked='',

                         loop_checked='',

                         reflect_checked='')

        mode_dict[self.default_mode + '_checked'] = 'checked'



        interval = 1000 // self.fps



        with open(self.outfile, 'w') as of:

            of.write(JS_INCLUDE + STYLE_INCLUDE)

            of.write(DISPLAY_TEMPLATE.format(id=uuid.uuid4().hex,

                                             Nframes=frame_count,

                                             fill_frames=fill_frames,

                                             interval=interval,

                                             **mode_dict))



                                                          

                                                                          

                                                                             

                                                                       

                                                   

        if self._tmpdir:

            _log.debug('MovieWriter: clearing temporary path=%s', self._tmpdir)

            self._tmpdir.cleanup()





class Animation:

    



    def __init__(self, fig, event_source=None, blit=False):

        self._draw_was_started = False



        self._fig = fig

                                                                     

                                                                   

                                           

        self._blit = blit and fig.canvas.supports_blit



                                                                               

                                                                            

                                                                             

                                                       

        self.frame_seq = self.new_frame_seq()

        self.event_source = event_source

        self.event_source.add_callback(self._step)



                                                                              

                                                                           

        self._first_draw_id = fig.canvas.mpl_connect('draw_event', self._start)



                                                                          

                                                          

        self._close_id = self._fig.canvas.mpl_connect('close_event',

                                                      self._stop)

        if self._blit:

            self._setup_blit()



    def __del__(self):

        if not getattr(self, '_draw_was_started', True):

            warnings.warn(

                'Animation was deleted without rendering anything. This is '

                'most likely not intended. To prevent deletion, assign the '

                'Animation to a variable, e.g. `anim`, that exists until you '

                'output the Animation using `plt.show()` or '

                '`anim.save()`.'

            )



    def _start(self, *args):

        

                                                       

        if self._fig.canvas.is_saving():

            return

                                                 

        self._fig.canvas.mpl_disconnect(self._first_draw_id)

                                 

        self._init_draw()

                                          

        self.event_source.start()



    def _stop(self, *args):

                                                  

        if self._blit:

            self._fig.canvas.mpl_disconnect(self._resize_id)

        self._fig.canvas.mpl_disconnect(self._close_id)

        self.event_source.remove_callback(self._step)

        self.event_source = None



    def save(self, filename, writer=None, fps=None, dpi=None, codec=None,

             bitrate=None, extra_args=None, metadata=None, extra_anim=None,

             savefig_kwargs=None, *, progress_callback=None):

        



        all_anim = [self]

        if extra_anim is not None:

            all_anim.extend(anim for anim in extra_anim

                            if anim._fig is self._fig)



                                                                    

        for anim in all_anim:

            anim._draw_was_started = True



        if writer is None:

            writer = mpl.rcParams['animation.writer']

        elif (not isinstance(writer, str) and

              any(arg is not None

                  for arg in (fps, codec, bitrate, extra_args, metadata))):

            raise RuntimeError('Passing in values for arguments '

                               'fps, codec, bitrate, extra_args, or metadata '

                               'is not supported when writer is an existing '

                               'MovieWriter instance. These should instead be '

                               'passed as arguments when creating the '

                               'MovieWriter instance.')



        if savefig_kwargs is None:

            savefig_kwargs = {}

        else:

                                               

            savefig_kwargs = dict(savefig_kwargs)



        if fps is None and hasattr(self, '_interval'):

                                                         

            fps = 1000. / self._interval



                                                          

        dpi = mpl._val_or_rc(dpi, 'savefig.dpi')

        if dpi == 'figure':

            dpi = self._fig.dpi



        writer_kwargs = {}

        if codec is not None:

            writer_kwargs['codec'] = codec

        if bitrate is not None:

            writer_kwargs['bitrate'] = bitrate

        if extra_args is not None:

            writer_kwargs['extra_args'] = extra_args

        if metadata is not None:

            writer_kwargs['metadata'] = metadata



                                                                         

                           

        if isinstance(writer, str):

            try:

                writer_cls = writers[writer]

            except RuntimeError:                            

                writer_cls = PillowWriter                     

                _log.warning("MovieWriter %s unavailable; using Pillow "

                             "instead.", writer)

            writer = writer_cls(fps, **writer_kwargs)

        _log.info('Animation.save using %s', type(writer))



        if 'bbox_inches' in savefig_kwargs:

            _log.warning("Warning: discarding the 'bbox_inches' argument in "

                         "'savefig_kwargs' as it may cause frame size "

                         "to vary, which is inappropriate for animation.")

            savefig_kwargs.pop('bbox_inches')



                                                                           

                                                                           

                                              

                                                                              

                                                                         

                                                                             



        def _pre_composite_to_white(color):

            r, g, b, a = mcolors.to_rgba(color)

            return a * np.array([r, g, b]) + 1 - a



                                                                          

                                                                           

                                                       

        with (writer.saving(self._fig, filename, dpi),

              cbook._setattr_cm(self._fig.canvas, _is_saving=True, manager=None)):

            if not writer._supports_transparency():

                facecolor = savefig_kwargs.get('facecolor',

                                               mpl.rcParams['savefig.facecolor'])

                if facecolor == 'auto':

                    facecolor = self._fig.get_facecolor()

                savefig_kwargs['facecolor'] = _pre_composite_to_white(facecolor)

                savefig_kwargs['transparent'] = False                     



            for anim in all_anim:

                anim._init_draw()                           

            frame_number = 0

                                                                 

                                                                        

            save_count_list = [getattr(a, '_save_count', None)

                               for a in all_anim]

            if None in save_count_list:

                total_frames = None

            else:

                total_frames = sum(save_count_list)

            for data in zip(*[a.new_saved_frame_seq() for a in all_anim]):

                for anim, d in zip(all_anim, data):

                                                                       

                    anim._draw_next_frame(d, blit=False)

                    if progress_callback is not None:

                        progress_callback(frame_number, total_frames)

                        frame_number += 1

                writer.grab_frame(**savefig_kwargs)



    def _step(self, *args):

        

                                                                           

                                                                            

                                                

        try:

            framedata = next(self.frame_seq)

            self._draw_next_frame(framedata, self._blit)

            return True

        except StopIteration:

            return False



    def new_frame_seq(self):

        

                                                                         

        return iter(self._framedata)



    def new_saved_frame_seq(self):

        

                                                           

        return self.new_frame_seq()



    def _draw_next_frame(self, framedata, blit):

                                                                          

                                                                 

        self._pre_draw(framedata, blit)

        self._draw_frame(framedata)

        self._post_draw(framedata, blit)



    def _init_draw(self):

                                                                         

                                        

        self._draw_was_started = True



    def _pre_draw(self, framedata, blit):

                                                                          

                                                                     

        if blit:

            self._blit_clear(self._drawn_artists)



    def _draw_frame(self, framedata):

                                               

        raise NotImplementedError('Needs to be implemented by subclasses to'

                                  ' actually make an animation.')



    def _post_draw(self, framedata, blit):

                                                                          

                                                                        

                   

        if blit and self._drawn_artists:

            self._blit_draw(self._drawn_artists)

        else:

            self._fig.canvas.draw_idle()



                                                                       

    def _blit_draw(self, artists):

                                                                               

                               

        updated_ax = {a.axes for a in artists}

                                                                     

                                                                         

        for ax in updated_ax:

                                                                              

                                                                            

                                                      

            cur_view = ax._get_view()

            view, bg = self._blit_cache.get(ax, (object(), None))

            if cur_view != view:

                self._blit_cache[ax] = (

                    cur_view, ax.figure.canvas.copy_from_bbox(ax.bbox))

                                                  

        for a in artists:

            a.axes.draw_artist(a)

                                                                              

        for ax in updated_ax:

            ax.figure.canvas.blit(ax.bbox)



    def _blit_clear(self, artists):

                                                                         

                                                                         

                            

        axes = {a.axes for a in artists}

        for ax in axes:

            try:

                view, bg = self._blit_cache[ax]

            except KeyError:

                continue

            if ax._get_view() == view:

                ax.figure.canvas.restore_region(bg)

            else:

                self._blit_cache.pop(ax)



    def _setup_blit(self):

                                                                              

        self._blit_cache = dict()

        self._drawn_artists = []

                                                                        

        self._post_draw(None, self._blit)

                                                              

                                                                   

                                                                         

                                                            

        self._init_draw()

                                         

        self._resize_id = self._fig.canvas.mpl_connect('resize_event',

                                                       self._on_resize)



    def _on_resize(self, event):

                                                                             

                                                                      

                                                                            

                                                          

        self._fig.canvas.mpl_disconnect(self._resize_id)

        self.event_source.stop()

        self._blit_cache.clear()

        self._init_draw()

        self._resize_id = self._fig.canvas.mpl_connect('draw_event',

                                                       self._end_redraw)



    def _end_redraw(self, event):

                                                                         

                                                                   

        self._post_draw(None, False)

        self.event_source.start()

        self._fig.canvas.mpl_disconnect(self._resize_id)

        self._resize_id = self._fig.canvas.mpl_connect('resize_event',

                                                       self._on_resize)



    def to_html5_video(self, embed_limit=None):

        

        VIDEO_TAG = r'''<video {size} {options}>
  <source type="video/mp4" src="data:video/mp4;base64,{video}">
  Your browser does not support the video tag.
</video>'''

                                                  

        if not hasattr(self, '_base64_video'):

                                                    

            embed_limit = mpl._val_or_rc(embed_limit, 'animation.embed_limit')



                                      

            embed_limit *= 1024 * 1024



                                                                        

                                         

            with TemporaryDirectory() as tmpdir:

                path = Path(tmpdir, "temp.m4v")

                                                                    

                                              

                Writer = writers[mpl.rcParams['animation.writer']]

                writer = Writer(codec='h264',

                                bitrate=mpl.rcParams['animation.bitrate'],

                                fps=1000. / self._interval)

                self.save(str(path), writer=writer)

                                             

                vid64 = base64.encodebytes(path.read_bytes())



            vid_len = len(vid64)

            if vid_len >= embed_limit:

                _log.warning(

                    "Animation movie is %s bytes, exceeding the limit of %s. "

                    "If you're sure you want a large animation embedded, set "

                    "the animation.embed_limit rc parameter to a larger value "

                    "(in MB).", vid_len, embed_limit)

            else:

                self._base64_video = vid64.decode('ascii')

                self._video_size = 'width="{}" height="{}"'.format(

                        *writer.frame_size)



                                                             

        if hasattr(self, '_base64_video'):

                                                                              

            options = ['controls', 'autoplay']



                                                  

            if getattr(self, '_repeat', False):

                options.append('loop')



            return VIDEO_TAG.format(video=self._base64_video,

                                    size=self._video_size,

                                    options=' '.join(options))

        else:

            return 'Video too large to embed.'



    def to_jshtml(self, fps=None, embed_frames=True, default_mode=None):

        

        if fps is None and hasattr(self, '_interval'):

                                                         

            fps = 1000 / self._interval



                                                                            

                               

        if default_mode is None:

            default_mode = 'loop' if getattr(self, '_repeat',

                                             False) else 'once'



        if not hasattr(self, "_html_representation"):

                                                                        

                                         

            with TemporaryDirectory() as tmpdir:

                path = Path(tmpdir, "temp.html")

                writer = HTMLWriter(fps=fps,

                                    embed_frames=embed_frames,

                                    default_mode=default_mode)

                self.save(str(path), writer=writer)

                self._html_representation = path.read_text()



        return self._html_representation



    def _repr_html_(self):

        

        fmt = mpl.rcParams['animation.html']

        if fmt == 'html5':

            return self.to_html5_video()

        elif fmt == 'jshtml':

            return self.to_jshtml()



    def pause(self):

        

        self.event_source.stop()

        if self._blit:

            for artist in self._drawn_artists:

                artist.set_animated(False)



    def resume(self):

        

        self.event_source.start()

        if self._blit:

            for artist in self._drawn_artists:

                artist.set_animated(True)





class TimedAnimation(Animation):

    

    def __init__(self, fig, interval=200, repeat_delay=0, repeat=True,

                 event_source=None, *args, **kwargs):

        self._interval = interval

                                                                     

        self._repeat_delay = repeat_delay if repeat_delay is not None else 0

        self._repeat = repeat

                                                                              

                                                                          

        if event_source is None:

            event_source = fig.canvas.new_timer(interval=self._interval)

        super().__init__(fig, event_source=event_source, *args, **kwargs)



    def _step(self, *args):

        

                                                                 

                                                                        

                                                                   

                                                                              

                                                                            

               

        still_going = super()._step(*args)

        if not still_going:

            if self._repeat:

                                       

                self._init_draw()

                self.frame_seq = self.new_frame_seq()

                self.event_source.interval = self._repeat_delay

                return True

            else:

                                                                      

                                                                      

                self.pause()

                if self._blit:

                                                                    

                    self._fig.canvas.mpl_disconnect(self._resize_id)

                self._fig.canvas.mpl_disconnect(self._close_id)

                self.event_source = None

                return False



        self.event_source.interval = self._interval

        return True





class ArtistAnimation(TimedAnimation):

    



    def __init__(self, fig, artists, *args, **kwargs):

                                                                  

        self._drawn_artists = []



                                                                          

                                

        self._framedata = artists

        super().__init__(fig, *args, **kwargs)



    def _init_draw(self):

        super()._init_draw()

                                                                

        figs = set()

        for f in self.new_frame_seq():

            for artist in f:

                artist.set_visible(False)

                artist.set_animated(self._blit)

                                                                      

                if artist.get_figure() not in figs:

                    figs.add(artist.get_figure())



                                  

        for fig in figs:

            fig.canvas.draw_idle()



    def _pre_draw(self, framedata, blit):

        

        if blit:

                                      

            self._blit_clear(self._drawn_artists)

        else:

                                                                               

            for artist in self._drawn_artists:

                artist.set_visible(False)



    def _draw_frame(self, artists):

                                                                         

                                       

        self._drawn_artists = artists



                                                             

        for artist in artists:

            artist.set_visible(True)





class FuncAnimation(TimedAnimation):

    

    def __init__(self, fig, func, frames=None, init_func=None, fargs=None,

                 save_count=None, *, cache_frame_data=True, **kwargs):

        if fargs:

            self._args = fargs

        else:

            self._args = ()

        self._func = func

        self._init_func = init_func



                                                                            

                                                                          

                                                       

        self._save_count = save_count

                                                                               

                                                                            

                                                                             

                                                                           

                                                

        if frames is None:

            self._iter_gen = itertools.count

        elif callable(frames):

            self._iter_gen = frames

        elif np.iterable(frames):

            if kwargs.get('repeat', True):

                self._tee_from = frames

                def iter_frames(frames=frames):

                    this, self._tee_from = itertools.tee(self._tee_from, 2)

                    yield from this

                self._iter_gen = iter_frames

            else:

                self._iter_gen = lambda: iter(frames)

            if hasattr(frames, '__len__'):

                self._save_count = len(frames)

                if save_count is not None:

                    _api.warn_external(

                        f"You passed in an explicit {save_count=} "

                        "which is being ignored in favor of "

                        f"{len(frames)=}."

                    )

        else:

            self._iter_gen = lambda: iter(range(frames))

            self._save_count = frames

            if save_count is not None:

                _api.warn_external(

                    f"You passed in an explicit {save_count=} which is being "

                    f"ignored in favor of {frames=}."

                )

        if self._save_count is None and cache_frame_data:

            _api.warn_external(

                f"{frames=!r} which we can infer the length of, "

                "did not pass an explicit *save_count* "

                f"and passed {cache_frame_data=}.  To avoid a possibly "

                "unbounded cache, frame data caching has been disabled. "

                "To suppress this warning either pass "

                "`cache_frame_data=False` or `save_count=MAX_FRAMES`."

            )

            cache_frame_data = False



        self._cache_frame_data = cache_frame_data



                                                                             

        self._save_seq = collections.deque([], self._save_count)



        super().__init__(fig, **kwargs)



                                                                           

                                                                  

        self._save_seq.clear()



    def new_frame_seq(self):

                                                                      

        return self._iter_gen()



    def new_saved_frame_seq(self):

                                                                           

                                                                           

                                   

        if self._save_seq:

                                                              

                                                   

            return iter([*self._save_seq])

        else:

            if self._save_count is None:

                frame_seq = self.new_frame_seq()



                def gen():

                    try:

                        while True:

                            yield next(frame_seq)

                    except StopIteration:

                        pass

                return gen()

            else:

                return itertools.islice(self.new_frame_seq(), self._save_count)



    def _init_draw(self):

        super()._init_draw()

                                                                       

                                                                              

                                                                          

                  

        if self._init_func is None:

            try:

                frame_data = next(self.new_frame_seq())

            except StopIteration:

                                                                        

                                                                   

                                

                warnings.warn(

                    "Can not start iterating the frames for the initial draw. "

                    "This can be caused by passing in a 0 length sequence "

                    "for *frames*.\n\n"

                    "If you passed *frames* as a generator "

                    "it may be exhausted due to a previous display or save."

                )

                return

            self._draw_frame(frame_data)

        else:

            self._drawn_artists = self._init_func()

            if self._blit:

                if self._drawn_artists is None:

                    raise RuntimeError('When blit=True, the init_func must '

                                       'return a sequence of Artist objects.')

                for a in self._drawn_artists:

                    a.set_animated(self._blit)

        self._save_seq.clear()



    def _draw_frame(self, framedata):

        if self._cache_frame_data:

                                                           

            self._save_seq.append(framedata)



                                                                        

                                                                            

        self._drawn_artists = self._func(framedata, *self._args)



        if self._blit:



            err = RuntimeError('When blit=True, the animation function must '

                               'return a sequence of Artist objects.')

            try:

                                     

                iter(self._drawn_artists)

            except TypeError:

                raise err from None



                                            

            for i in self._drawn_artists:

                if not isinstance(i, mpl.artist.Artist):

                    raise err



            self._drawn_artists = sorted(self._drawn_artists,

                                         key=lambda x: x.get_zorder())



            for a in self._drawn_artists:

                a.set_animated(self._blit)





def _validate_grabframe_kwargs(savefig_kwargs):

    if mpl.rcParams['savefig.bbox'] == 'tight':

        raise ValueError(

            f"{mpl.rcParams['savefig.bbox']=} must not be 'tight' as it "

            "may cause frame size to vary, which is inappropriate for animation."

        )

    for k in ('dpi', 'bbox_inches', 'format'):

        if k in savefig_kwargs:

            raise TypeError(

                f"grab_frame got an unexpected keyword argument {k!r}"

            )


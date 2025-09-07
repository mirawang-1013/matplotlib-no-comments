



import dataclasses

import enum

import logging

import os

import re

import struct

import subprocess

import sys

from collections import namedtuple

from functools import cache, lru_cache, partial, wraps

from pathlib import Path



import numpy as np



from matplotlib import _api, cbook, font_manager



_log = logging.getLogger(__name__)



                                                                      

                                                                              

                               



                                        

                              

                                        

 

                                                                     

                                                                    

                                       

 

                                     

                                                                  

                                                      

                                

                                                                    

                                  

                                                                       



_dvistate = enum.Enum('DviState', 'pre outer inpage post_post finale')



                                                                            

Page = namedtuple('Page', 'text boxes height width descent')

Box = namedtuple('Box', 'x y height width')





                                    

class Text(namedtuple('Text', 'x y font glyph width')):

    



    def _get_pdftexmap_entry(self):

        return PsfontsMap(find_tex_file("pdftex.map"))[self.font.texname]



    @property

    def font_path(self):

        

        psfont = self._get_pdftexmap_entry()

        if psfont.filename is None:

            raise ValueError("No usable font file found for {} ({}); "

                             "the font may lack a Type-1 version"

                             .format(psfont.psname.decode("ascii"),

                                     psfont.texname.decode("ascii")))

        return Path(psfont.filename)



    @property

    def font_size(self):

        

        return self.font.size



    @property

    def font_effects(self):

        

        return self._get_pdftexmap_entry().effects



    @property

    def index(self):

        

                                                                              

        return self.font._index_dvi_to_freetype(self.glyph)



    @property                                                           

    def glyph_name_or_index(self):

        

        entry = self._get_pdftexmap_entry()

        return (_parse_enc(entry.encoding)[self.glyph]

                if entry.encoding is not None else self.glyph)





                         

 

                                                                            

                                                                             

                                                                      

_arg_mapping = dict(

                              

    raw=lambda dvi, delta: delta,

                                            

    u1=lambda dvi, delta: dvi._read_arg(1, signed=False),

                                             

    u4=lambda dvi, delta: dvi._read_arg(4, signed=False),

                                          

    s4=lambda dvi, delta: dvi._read_arg(4, signed=True),

                                                                          

    slen=lambda dvi, delta: dvi._read_arg(delta, signed=True) if delta else None,

                                                       

    slen1=lambda dvi, delta: dvi._read_arg(delta + 1, signed=True),

                                                          

    ulen1=lambda dvi, delta: dvi._read_arg(delta + 1, signed=False),

                                                                               

                                    

    olen1=lambda dvi, delta: dvi._read_arg(delta + 1, signed=(delta == 3)),

)





def _dispatch(table, min, max=None, state=None, args=('raw',)):

    

    def decorate(method):

        get_args = [_arg_mapping[x] for x in args]



        @wraps(method)

        def wrapper(self, byte):

            if state is not None and self.state != state:

                raise ValueError("state precondition failed")

            return method(self, *[f(self, byte-min) for f in get_args])

        if max is None:

            table[min] = wrapper

        else:

            for i in range(min, max+1):

                assert table[i] is None

                table[i] = wrapper

        return wrapper

    return decorate





class Dvi:

    

                    

    _dtable = [None] * 256

    _dispatch = partial(_dispatch, _dtable)



    def __init__(self, filename, dpi):

        

        _log.debug('Dvi: %s', filename)

        self.file = open(filename, 'rb')

        self.dpi = dpi

        self.fonts = {}

        self.state = _dvistate.pre

        self._missing_font = None



    def __enter__(self):

        

        return self



    def __exit__(self, etype, evalue, etrace):

        

        self.close()



    def __iter__(self):

        

        while self._read():

            yield self._output()



    def close(self):

        

        if not self.file.closed:

            self.file.close()



    def _output(self):

        

        minx = miny = np.inf

        maxx = maxy = -np.inf

        maxy_pure = -np.inf

        for elt in self.text + self.boxes:

            if isinstance(elt, Box):

                x, y, h, w = elt

                e = 0              

            else:         

                x, y, font, g, w = elt

                h, e = font._height_depth_of(g)

            minx = min(minx, x)

            miny = min(miny, y - h)

            maxx = max(maxx, x + w)

            maxy = max(maxy, y + e)

            maxy_pure = max(maxy_pure, y)

        if self._baseline_v is not None:

            maxy_pure = self._baseline_v                                     

            self._baseline_v = None



        if not self.text and not self.boxes:                                   

            return Page(text=[], boxes=[], width=0, height=0, descent=0)



        if self.dpi is None:

                                                                            

            return Page(text=self.text, boxes=self.boxes,

                        width=maxx-minx, height=maxy_pure-miny,

                        descent=maxy-maxy_pure)



                                                         

        d = self.dpi / (72.27 * 2**16)

        descent = (maxy - maxy_pure) * d



        text = [Text((x-minx)*d, (maxy-y)*d - descent, f, g, w*d)

                for (x, y, f, g, w) in self.text]

        boxes = [Box((x-minx)*d, (maxy-y)*d - descent, h*d, w*d)

                 for (x, y, h, w) in self.boxes]



        return Page(text=text, boxes=boxes, width=(maxx-minx)*d,

                    height=(maxy_pure-miny)*d, descent=descent)



    def _read(self):

        

                                                 

                               

                       

                                                    

                

                

                  

                                                                        

                  

                  

                                        

                                                           

                      

                                                       

                                                                              

                                                                               

                                                                               

                                                                    

        down_stack = [0]

        self._baseline_v = None

        while True:

            byte = self.file.read(1)[0]

            self._dtable[byte](self, byte)

            if self._missing_font:

                raise self._missing_font.to_exception()

            name = self._dtable[byte].__name__

            if name == "_push":

                down_stack.append(down_stack[-1])

            elif name == "_pop":

                down_stack.pop()

            elif name == "_down":

                down_stack[-1] += 1

            if (self._baseline_v is None

                    and len(getattr(self, "stack", [])) == 3

                    and down_stack[-1] >= 4):

                self._baseline_v = self.v

            if byte == 140:                                      

                return True

            if self.state is _dvistate.post_post:                

                self.close()

                return False



    def _read_arg(self, nbytes, signed=False):

        

        return int.from_bytes(self.file.read(nbytes), "big", signed=signed)



    @_dispatch(min=0, max=127, state=_dvistate.inpage)

    def _set_char_immediate(self, char):

        self._put_char_real(char)

        if isinstance(self.fonts[self.f], cbook._ExceptionInfo):

            return

        self.h += self.fonts[self.f]._width_of(char)



    @_dispatch(min=128, max=131, state=_dvistate.inpage, args=('olen1',))

    def _set_char(self, char):

        self._put_char_real(char)

        if isinstance(self.fonts[self.f], cbook._ExceptionInfo):

            return

        self.h += self.fonts[self.f]._width_of(char)



    @_dispatch(132, state=_dvistate.inpage, args=('s4', 's4'))

    def _set_rule(self, a, b):

        self._put_rule_real(a, b)

        self.h += b



    @_dispatch(min=133, max=136, state=_dvistate.inpage, args=('olen1',))

    def _put_char(self, char):

        self._put_char_real(char)



    def _put_char_real(self, char):

        font = self.fonts[self.f]

        if isinstance(font, cbook._ExceptionInfo):

            self._missing_font = font

        elif font._vf is None:

            self.text.append(Text(self.h, self.v, font, char,

                                  font._width_of(char)))

        else:

            scale = font._scale

            for x, y, f, g, w in font._vf[char].text:

                newf = DviFont(scale=_mul1220(scale, f._scale),

                               tfm=f._tfm, texname=f.texname, vf=f._vf)

                self.text.append(Text(self.h + _mul1220(x, scale),

                                      self.v + _mul1220(y, scale),

                                      newf, g, newf._width_of(g)))

            self.boxes.extend([Box(self.h + _mul1220(x, scale),

                                   self.v + _mul1220(y, scale),

                                   _mul1220(a, scale), _mul1220(b, scale))

                               for x, y, a, b in font._vf[char].boxes])



    @_dispatch(137, state=_dvistate.inpage, args=('s4', 's4'))

    def _put_rule(self, a, b):

        self._put_rule_real(a, b)



    def _put_rule_real(self, a, b):

        if a > 0 and b > 0:

            self.boxes.append(Box(self.h, self.v, a, b))



    @_dispatch(138)

    def _nop(self, _):

        pass



    @_dispatch(139, state=_dvistate.outer, args=('s4',)*11)

    def _bop(self, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, p):

        self.state = _dvistate.inpage

        self.h = self.v = self.w = self.x = self.y = self.z = 0

        self.stack = []

        self.text = []                                

        self.boxes = []                              



    @_dispatch(140, state=_dvistate.inpage)

    def _eop(self, _):

        self.state = _dvistate.outer

        del self.h, self.v, self.w, self.x, self.y, self.z, self.stack



    @_dispatch(141, state=_dvistate.inpage)

    def _push(self, _):

        self.stack.append((self.h, self.v, self.w, self.x, self.y, self.z))



    @_dispatch(142, state=_dvistate.inpage)

    def _pop(self, _):

        self.h, self.v, self.w, self.x, self.y, self.z = self.stack.pop()



    @_dispatch(min=143, max=146, state=_dvistate.inpage, args=('slen1',))

    def _right(self, b):

        self.h += b



    @_dispatch(min=147, max=151, state=_dvistate.inpage, args=('slen',))

    def _right_w(self, new_w):

        if new_w is not None:

            self.w = new_w

        self.h += self.w



    @_dispatch(min=152, max=156, state=_dvistate.inpage, args=('slen',))

    def _right_x(self, new_x):

        if new_x is not None:

            self.x = new_x

        self.h += self.x



    @_dispatch(min=157, max=160, state=_dvistate.inpage, args=('slen1',))

    def _down(self, a):

        self.v += a



    @_dispatch(min=161, max=165, state=_dvistate.inpage, args=('slen',))

    def _down_y(self, new_y):

        if new_y is not None:

            self.y = new_y

        self.v += self.y



    @_dispatch(min=166, max=170, state=_dvistate.inpage, args=('slen',))

    def _down_z(self, new_z):

        if new_z is not None:

            self.z = new_z

        self.v += self.z



    @_dispatch(min=171, max=234, state=_dvistate.inpage)

    def _fnt_num_immediate(self, k):

        self.f = k



    @_dispatch(min=235, max=238, state=_dvistate.inpage, args=('olen1',))

    def _fnt_num(self, new_f):

        self.f = new_f



    @_dispatch(min=239, max=242, args=('ulen1',))

    def _xxx(self, datalen):

        special = self.file.read(datalen)

        _log.debug(

            'Dvi._xxx: encountered special: %s',

            ''.join([chr(ch) if 32 <= ch < 127 else '<%02x>' % ch

                     for ch in special]))



    @_dispatch(min=243, max=246, args=('olen1', 'u4', 'u4', 'u4', 'u1', 'u1'))

    def _fnt_def(self, k, c, s, d, a, l):

        self._fnt_def_real(k, c, s, d, a, l)



    def _fnt_def_real(self, k, c, s, d, a, l):

        n = self.file.read(a + l)

        fontname = n[-l:].decode('ascii')

        try:

            tfm = _tfmfile(fontname)

        except FileNotFoundError as exc:

                                                                             

                                                                               

                                                                          

                                                                            

                                         

            self.fonts[k] = cbook._ExceptionInfo.from_exception(exc)

            return

        if c != 0 and tfm.checksum != 0 and c != tfm.checksum:

            raise ValueError(f'tfm checksum mismatch: {n}')

        try:

            vf = _vffile(fontname)

        except FileNotFoundError:

            vf = None

        self.fonts[k] = DviFont(scale=s, tfm=tfm, texname=n, vf=vf)



    @_dispatch(247, state=_dvistate.pre, args=('u1', 'u4', 'u4', 'u4', 'u1'))

    def _pre(self, i, num, den, mag, k):

        self.file.read(k)                           

        if i != 2:

            raise ValueError(f"Unknown dvi format {i}")

        if num != 25400000 or den != 7227 * 2**16:

            raise ValueError("Nonstandard units in dvi file")

                                                                

                                                      

                                                         

                                                                    

                                                     

        if mag != 1000:

            raise ValueError("Nonstandard magnification in dvi file")

                                                               

                                                    

        self.state = _dvistate.outer



    @_dispatch(248, state=_dvistate.outer)

    def _post(self, _):

        self.state = _dvistate.post_post

                                                       

                                                            



    @_dispatch(249)

    def _post_post(self, _):

        raise NotImplementedError



    @_dispatch(min=250, max=255)

    def _malformed(self, offset):

        raise ValueError(f"unknown command: byte {250 + offset}")





class DviFont:

    

    __slots__ = ('texname', 'size', '_scale', '_vf', '_tfm', '_encoding')



    def __init__(self, scale, tfm, texname, vf):

        _api.check_isinstance(bytes, texname=texname)

        self._scale = scale

        self._tfm = tfm

        self.texname = texname

        self._vf = vf

        self.size = scale * (72.0 / (72.27 * 2**16))

        self._encoding = None



    widths = _api.deprecated("3.11")(property(lambda self: [

        (1000 * self._tfm.width.get(char, 0)) >> 20

        for char in range(max(self._tfm.width, default=-1) + 1)]))



    @property

    def fname(self):

        

        return self.texname.decode('latin-1')



    def _get_fontmap(self, string):

        

        return {char: self for char in string}



    def __eq__(self, other):

        return (type(self) is type(other)

                and self.texname == other.texname and self.size == other.size)



    def __ne__(self, other):

        return not self.__eq__(other)



    def __repr__(self):

        return f"<{type(self).__name__}: {self.texname}>"



    def _width_of(self, char):

        

        metrics = self._tfm.get_metrics(char)

        if metrics is None:

            _log.debug('No width for char %d in font %s.', char, self.texname)

            return 0

        return _mul1220(metrics.tex_width, self._scale)



    def _height_depth_of(self, char):

        

        metrics = self._tfm.get_metrics(char)

        if metrics is None:

            _log.debug('No metrics for char %d in font %s', char, self.texname)

            return [0, 0]

        hd = [

            _mul1220(metrics.tex_height, self._scale),

            _mul1220(metrics.tex_depth, self._scale),

        ]

                                                                       

                                               

                                                   

                                                                     

                                      

        if re.match(br'^cmsy\d+$', self.texname) and char == 0:

            hd[-1] = 0

        return hd



    def _index_dvi_to_freetype(self, idx):

        

                                                                             

                                                                       

                                                                               

                                                                            

                                                          

                                                                          

                                                                            

                   

                                                                            

                                                                         

        if self._encoding is None:

            psfont = PsfontsMap(find_tex_file("pdftex.map"))[self.texname]

            if psfont.filename is None:

                raise ValueError("No usable font file found for {} ({}); "

                                 "the font may lack a Type-1 version"

                                 .format(psfont.psname.decode("ascii"),

                                         psfont.texname.decode("ascii")))

            face = font_manager.get_font(psfont.filename)

            if psfont.encoding:

                self._encoding = [face.get_name_index(name)

                                  for name in _parse_enc(psfont.encoding)]

            else:

                self._encoding = face._get_type1_encoding_vector()

        return self._encoding[idx]





class Vf(Dvi):

    



    def __init__(self, filename):

        super().__init__(filename, 0)

        try:

            self._first_font = None

            self._chars = {}

            self._read()

        finally:

            self.close()



    def __getitem__(self, code):

        return self._chars[code]



    def _read(self):

        

        packet_char = packet_ends = None

        packet_len = packet_width = None

        while True:

            byte = self.file.read(1)[0]

                                                                 

            if self.state is _dvistate.inpage:

                byte_at = self.file.tell()-1

                if byte_at == packet_ends:

                    self._finalize_packet(packet_char, packet_width)

                    packet_len = packet_char = packet_width = None

                                                        

                elif byte_at > packet_ends:

                    raise ValueError("Packet length mismatch in vf file")

                else:

                    if byte in (139, 140) or byte >= 243:

                        raise ValueError(f"Inappropriate opcode {byte} in vf file")

                    Dvi._dtable[byte](self, byte)

                    continue



                                     

            if byte < 242:                                                 

                packet_len = byte

                packet_char = self._read_arg(1)

                packet_width = self._read_arg(3)

                packet_ends = self._init_packet(byte)

                self.state = _dvistate.inpage

            elif byte == 242:                      

                packet_len = self._read_arg(4)

                packet_char = self._read_arg(4)

                packet_width = self._read_arg(4)

                self._init_packet(packet_len)

            elif 243 <= byte <= 246:

                k = self._read_arg(byte - 242, byte == 246)

                c = self._read_arg(4)

                s = self._read_arg(4)

                d = self._read_arg(4)

                a = self._read_arg(1)

                l = self._read_arg(1)

                self._fnt_def_real(k, c, s, d, a, l)

                if self._first_font is None:

                    self._first_font = k

            elif byte == 247:                 

                i = self._read_arg(1)

                k = self._read_arg(1)

                x = self.file.read(k)

                cs = self._read_arg(4)

                ds = self._read_arg(4)

                self._pre(i, x, cs, ds)

            elif byte == 248:                                             

                break

            else:

                raise ValueError(f"Unknown vf opcode {byte}")



    def _init_packet(self, pl):

        if self.state != _dvistate.outer:

            raise ValueError("Misplaced packet in vf file")

        self.h = self.v = self.w = self.x = self.y = self.z = 0

        self.stack = []

        self.text = []

        self.boxes = []

        self.f = self._first_font

        self._missing_font = None

        return self.file.tell() + pl



    def _finalize_packet(self, packet_char, packet_width):

        if not self._missing_font:                                                  

            self._chars[packet_char] = Page(

                text=self.text, boxes=self.boxes, width=packet_width,

                height=None, descent=None)

        self.state = _dvistate.outer



    def _pre(self, i, x, cs, ds):

        if self.state is not _dvistate.pre:

            raise ValueError("pre command in middle of vf file")

        if i != 202:

            raise ValueError(f"Unknown vf format {i}")

        if len(x):

            _log.debug('vf file comment: %s', x)

        self.state = _dvistate.outer

                                         





def _mul1220(num1, num2):

    

                                                                    

    return (num1*num2) >> 20





@dataclasses.dataclass(frozen=True, kw_only=True)

class TexMetrics:

    

    tex_width: int

    tex_height: int

    tex_depth: int





class Tfm:

    



    def __init__(self, filename):

        _log.debug('opening tfm file %s', filename)

        with open(filename, 'rb') as file:

            header1 = file.read(24)

            lh, bc, ec, nw, nh, nd = struct.unpack('!6H', header1[2:14])

            _log.debug('lh=%d, bc=%d, ec=%d, nw=%d, nh=%d, nd=%d',

                       lh, bc, ec, nw, nh, nd)

            header2 = file.read(4*lh)

            self.checksum, self.design_size = struct.unpack('!2I', header2[:8])

                                                     

            char_info = file.read(4*(ec-bc+1))

            widths = struct.unpack(f'!{nw}i', file.read(4*nw))

            heights = struct.unpack(f'!{nh}i', file.read(4*nh))

            depths = struct.unpack(f'!{nd}i', file.read(4*nd))

        self._glyph_metrics = {}

        for idx, char in enumerate(range(bc, ec+1)):

            byte0 = char_info[4*idx]

            byte1 = char_info[4*idx+1]

            self._glyph_metrics[char] = TexMetrics(

                tex_width=widths[byte0],

                tex_height=heights[byte1 >> 4],

                tex_depth=depths[byte1 & 0xf],

            )



    def get_metrics(self, idx):

        

        return self._glyph_metrics.get(idx)



    width = _api.deprecated("3.11", alternative="get_metrics")(

        property(lambda self: {c: m.tex_width for c, m in self._glyph_metrics}))

    height = _api.deprecated("3.11", alternative="get_metrics")(

        property(lambda self: {c: m.tex_height for c, m in self._glyph_metrics}))

    depth = _api.deprecated("3.11", alternative="get_metrics")(

        property(lambda self: {c: m.tex_depth for c, m in self._glyph_metrics}))





PsFont = namedtuple('PsFont', 'texname psname effects encoding filename')





class PsfontsMap:

    

    __slots__ = ('_filename', '_unparsed', '_parsed')



                                                            

                                                                             

                              

    @lru_cache

    def __new__(cls, filename):

        self = object.__new__(cls)

        self._filename = os.fsdecode(filename)

                                                                           

                                                                               

                                                                         

                                            

        with open(filename, 'rb') as file:

            self._unparsed = {}

            for line in file:

                tfmname = line.split(b' ', 1)[0]

                self._unparsed.setdefault(tfmname, []).append(line)

        self._parsed = {}

        return self



    def __getitem__(self, texname):

        assert isinstance(texname, bytes)

        if texname in self._unparsed:

            for line in self._unparsed.pop(texname):

                if self._parse_and_cache_line(line):

                    break

        try:

            return self._parsed[texname]

        except KeyError:

            raise LookupError(

                f"The font map {self._filename!r} is missing a PostScript font "

                f"associated to TeX font {texname.decode('ascii')!r}; this problem can "

                f"often be solved by installing a suitable PostScript font package in "

                f"your TeX package manager") from None



    def _parse_and_cache_line(self, line):

        

                                                                     

                                                                

                                                               

                                                



        if not line or line.startswith((b" ", b"%", b"*", b";", b"#")):

            return

        tfmname = basename = special = encodingfile = fontfile = None

        is_subsetted = is_t1 = is_truetype = False

        matches = re.finditer(br'"([^"]*)(?:"|$)|(\S+)', line)

        for match in matches:

            quoted, unquoted = match.groups()

            if unquoted:

                if unquoted.startswith(b"<<"):        

                    fontfile = unquoted[2:]

                elif unquoted.startswith(b"<["):            

                    encodingfile = unquoted[2:]

                elif unquoted.startswith(b"<"):                    

                    word = (

                                     

                        unquoted[1:]

                                                           

                        or next(filter(None, next(matches).groups())))

                    if word.endswith(b".enc"):

                        encodingfile = word

                    else:

                        fontfile = word

                        is_subsetted = True

                elif tfmname is None:

                    tfmname = unquoted

                elif basename is None:

                    basename = unquoted

            elif quoted:

                special = quoted

        effects = {}

        if special:

            words = reversed(special.split())

            for word in words:

                if word == b"SlantFont":

                    effects["slant"] = float(next(words))

                elif word == b"ExtendFont":

                    effects["extend"] = float(next(words))



                                                                              

                    

        if fontfile is not None:

            if fontfile.endswith((b".ttf", b".ttc")):

                is_truetype = True

            elif not fontfile.endswith(b".otf"):

                is_t1 = True

        elif basename is not None:

            is_t1 = True

        if is_truetype and is_subsetted and encodingfile is None:

            return

        if not is_t1 and ("slant" in effects or "extend" in effects):

            return

        if abs(effects.get("slant", 0)) > 1:

            return

        if abs(effects.get("extend", 0)) > 2:

            return



        if basename is None:

            basename = tfmname

        if encodingfile is not None:

            encodingfile = find_tex_file(encodingfile)

        if fontfile is not None:

            fontfile = find_tex_file(fontfile)

        self._parsed[tfmname] = PsFont(

            texname=tfmname, psname=basename, effects=effects,

            encoding=encodingfile, filename=fontfile)

        return True





def _parse_enc(path):

    

    no_comments = re.sub("%.*", "", Path(path).read_text(encoding="ascii"))

    array = re.search(r"(?s)\[(.*)\]", no_comments).group(1)

    lines = [line for line in array.split() if line]

    if all(line.startswith("/") for line in lines):

        return [line[1:] for line in lines]

    else:

        raise ValueError(f"Failed to parse {path} as Postscript encoding")





class _LuatexKpsewhich:

    @cache                

    def __new__(cls):

        self = object.__new__(cls)

        self._proc = self._new_proc()

        return self



    def _new_proc(self):

        return subprocess.Popen(

            ["luatex", "--luaonly",

             str(cbook._get_data_path("kpsewhich.lua"))],

            stdin=subprocess.PIPE, stdout=subprocess.PIPE)



    def search(self, filename):

        if self._proc.poll() is not None:                     

            self._proc = self._new_proc()

        self._proc.stdin.write(os.fsencode(filename) + b"\n")

        self._proc.stdin.flush()

        out = self._proc.stdout.readline().rstrip()

        return None if out == b"nil" else os.fsdecode(out)





@lru_cache

def find_tex_file(filename):

    



                                                               

                    

    if isinstance(filename, bytes):

        filename = filename.decode('utf-8', errors='replace')



    try:

        lk = _LuatexKpsewhich()

    except FileNotFoundError:

        lk = None                                                     



    if lk:

        path = lk.search(filename)

    else:

        if sys.platform == 'win32':

                                                                              

                                                                              

                                                                            

            kwargs = {'env': {**os.environ, 'command_line_encoding': 'utf-8'},

                      'encoding': 'utf-8'}

        else:                                                          

            kwargs = {'encoding': sys.getfilesystemencoding(),

                      'errors': 'surrogateescape'}



        try:

            path = (cbook._check_and_log_subprocess(['kpsewhich', filename],

                                                    _log, **kwargs)

                    .rstrip('\n'))

        except (FileNotFoundError, RuntimeError):

            path = None



    if path:

        return path

    else:

        raise FileNotFoundError(

            f"Matplotlib's TeX implementation searched for a file named "

            f"{filename!r} in your texmf tree, but could not find it")





@lru_cache

def _fontfile(cls, suffix, texname):

    return cls(find_tex_file(texname + suffix))





_tfmfile = partial(_fontfile, Tfm, ".tfm")

_vffile = partial(_fontfile, Vf, ".vf")





if __name__ == '__main__':

    import itertools

    from argparse import ArgumentParser



    import fontTools.agl



    from matplotlib.ft2font import FT2Font



    parser = ArgumentParser()

    parser.add_argument("filename")

    parser.add_argument("dpi", nargs="?", type=float, default=None)

    args = parser.parse_args()



    def _print_fields(*args):

        print(" ".join(map("{:>11}".format, args)))



    with Dvi(args.filename, args.dpi) as dvi:

        fontmap = PsfontsMap(find_tex_file('pdftex.map'))

        for page in dvi:

            print(f"=== NEW PAGE === "

                  f"(w: {page.width}, h: {page.height}, d: {page.descent})")

            print("--- GLYPHS ---")

            for font, group in itertools.groupby(

                    page.text, lambda text: text.font):

                psfont = fontmap[font.texname]

                fontpath = psfont.filename

                print(f"font: {font.texname.decode('latin-1')} "

                      f"(scale: {font._scale / 2 ** 20}) at {fontpath}")

                face = FT2Font(fontpath)

                _print_fields("x", "y", "glyph", "chr", "w")

                for text in group:

                    glyph_str = fontTools.agl.toUnicode(face.get_glyph_name(text.index))

                    _print_fields(text.x, text.y, text.glyph, glyph_str, text.width)

            if page.boxes:

                print("--- BOXES ---")

                _print_fields("x", "y", "h", "w")

                for box in page.boxes:

                    _print_fields(box.x, box.y, box.height, box.width)


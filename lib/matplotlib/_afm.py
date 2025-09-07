



from collections import namedtuple

import logging

import re



from ._mathtext_data import uni2type1





_log = logging.getLogger(__name__)





def _to_int(x):

                                                                        

                                                                             

                                                                         

                                                                           

                              

    return int(float(x))





def _to_float(x):

                                                                        

                                                                           

                              

    if isinstance(x, bytes):

                                                                               

                                        

        x = x.decode('latin-1')

    return float(x.replace(',', '.'))





def _to_str(x):

    return x.decode('utf8')





def _to_list_of_ints(s):

    s = s.replace(b',', b' ')

    return [_to_int(val) for val in s.split()]





def _to_list_of_floats(s):

    return [_to_float(val) for val in s.split()]





def _to_bool(s):

    if s.lower().strip() in (b'false', b'0', b'no'):

        return False

    else:

        return True





def _parse_header(fh):

    

    header_converters = {

        b'StartFontMetrics': _to_float,

        b'FontName': _to_str,

        b'FullName': _to_str,

        b'FamilyName': _to_str,

        b'Weight': _to_str,

        b'ItalicAngle': _to_float,

        b'IsFixedPitch': _to_bool,

        b'FontBBox': _to_list_of_ints,

        b'UnderlinePosition': _to_float,

        b'UnderlineThickness': _to_float,

        b'Version': _to_str,

                                                                            

                                                                               

                                                       

        b'Notice': lambda x: x,

        b'EncodingScheme': _to_str,

        b'CapHeight': _to_float,                                       

        b'Capheight': _to_float,                                               

        b'XHeight': _to_float,

        b'Ascender': _to_float,

        b'Descender': _to_float,

        b'StdHW': _to_float,

        b'StdVW': _to_float,

        b'StartCharMetrics': _to_int,

        b'CharacterSet': _to_str,

        b'Characters': _to_int,

    }

    d = {}

    first_line = True

    for line in fh:

        line = line.rstrip()

        if line.startswith(b'Comment'):

            continue

        lst = line.split(b' ', 1)

        key = lst[0]

        if first_line:

                                                               

                                                                      

                                                                  

                                                                 

                                 

            if key != b'StartFontMetrics':

                raise RuntimeError('Not an AFM file')

            first_line = False

        if len(lst) == 2:

            val = lst[1]

        else:

            val = b''

        try:

            converter = header_converters[key]

        except KeyError:

            _log.error("Found an unknown keyword in AFM header (was %r)", key)

            continue

        try:

            d[key] = converter(val)

        except ValueError:

            _log.error('Value error parsing header in AFM: %s, %s', key, val)

            continue

        if key == b'StartCharMetrics':

            break

    else:

        raise RuntimeError('Bad parse')

    return d





CharMetrics = namedtuple('CharMetrics', 'width, name, bbox')

CharMetrics.__doc__ = """
    Represents the character metrics of a single character.

    Notes
    -----
    The fields do currently only describe a subset of character metrics
    information defined in the AFM standard.
    """

CharMetrics.width.__doc__ = """The character width (WX)."""

CharMetrics.name.__doc__ = """The character name (N)."""

CharMetrics.bbox.__doc__ = """
    The bbox of the character (B) as a tuple (*llx*, *lly*, *urx*, *ury*)."""





def _parse_char_metrics(fh):

    

    required_keys = {'C', 'WX', 'N', 'B'}



    ascii_d = {}

    name_d = {}

    for line in fh:

                                                                      

                                                                 

        line = _to_str(line.rstrip())                             

        if line.startswith('EndCharMetrics'):

            return ascii_d, name_d

                                                                              

        vals = dict(s.strip().split(' ', 1) for s in line.split(';') if s)

                                                                       

        if not required_keys.issubset(vals):

            raise RuntimeError('Bad char metrics line: %s' % line)

        num = _to_int(vals['C'])

        wx = _to_float(vals['WX'])

        name = vals['N']

        bbox = _to_list_of_floats(vals['B'])

        bbox = list(map(int, bbox))

        metrics = CharMetrics(wx, name, bbox)

                                                                  

                                                                             

                     

        if name == 'Euro':

            num = 128

        elif name == 'minus':

            num = ord("\N{MINUS SIGN}")          

        if num != -1:

            ascii_d[num] = metrics

        name_d[name] = metrics

    raise RuntimeError('Bad parse')





def _parse_kern_pairs(fh):

    



    line = next(fh)

    if not line.startswith(b'StartKernPairs'):

        raise RuntimeError('Bad start of kern pairs data: %s' % line)



    d = {}

    for line in fh:

        line = line.rstrip()

        if not line:

            continue

        if line.startswith(b'EndKernPairs'):

            next(fh)               

            return d

        vals = line.split()

        if len(vals) != 4 or vals[0] != b'KPX':

            raise RuntimeError('Bad kern pairs line: %s' % line)

        c1, c2, val = _to_str(vals[1]), _to_str(vals[2]), _to_float(vals[3])

        d[(c1, c2)] = val

    raise RuntimeError('Bad kern pairs parse')





CompositePart = namedtuple('CompositePart', 'name, dx, dy')

CompositePart.__doc__ = """
    Represents the information on a composite element of a composite char."""

CompositePart.name.__doc__ = """Name of the part, e.g. 'acute'."""

CompositePart.dx.__doc__ = """x-displacement of the part from the origin."""

CompositePart.dy.__doc__ = """y-displacement of the part from the origin."""





def _parse_composites(fh):

    

    composites = {}

    for line in fh:

        line = line.rstrip()

        if not line:

            continue

        if line.startswith(b'EndComposites'):

            return composites

        vals = line.split(b';')

        cc = vals[0].split()

        name, _num_parts = cc[1], _to_int(cc[2])

        pccParts = []

        for s in vals[1:-1]:

            pcc = s.split()

            part = CompositePart(pcc[1], _to_float(pcc[2]), _to_float(pcc[3]))

            pccParts.append(part)

        composites[name] = pccParts



    raise RuntimeError('Bad composites parse')





def _parse_optional(fh):

    

    optional = {

        b'StartKernData': _parse_kern_pairs,

        b'StartComposites':  _parse_composites,

        }



    d = {b'StartKernData': {},

         b'StartComposites': {}}

    for line in fh:

        line = line.rstrip()

        if not line:

            continue

        key = line.split()[0]



        if key in optional:

            d[key] = optional[key](fh)



    return d[b'StartKernData'], d[b'StartComposites']





class AFM:



    def __init__(self, fh):

        

        self._header = _parse_header(fh)

        self._metrics, self._metrics_by_name = _parse_char_metrics(fh)

        self._kern, self._composite = _parse_optional(fh)



    def get_str_bbox_and_descent(self, s):

        

        if not len(s):

            return 0, 0, 0, 0, 0

        total_width = 0

        namelast = None

        miny = 1e9

        maxy = 0

        left = 0

        if not isinstance(s, str):

            s = _to_str(s)

        for c in s:

            if c == '\n':

                continue

            name = uni2type1.get(ord(c), f"uni{ord(c):04X}")

            try:

                wx, _, bbox = self._metrics_by_name[name]

            except KeyError:

                name = 'question'

                wx, _, bbox = self._metrics_by_name[name]

            total_width += wx + self._kern.get((namelast, name), 0)

            l, b, w, h = bbox

            left = min(left, l)

            miny = min(miny, b)

            maxy = max(maxy, b + h)



            namelast = name



        return left, miny, total_width, maxy - miny, -miny



    def get_glyph_name(self, glyph_ind):                                 

        

        return self._metrics[glyph_ind].name



    def get_char_index(self, c):                                 

        

        return c



    def get_width_char(self, c):

        

        return self._metrics[c].width



    def get_width_from_char_name(self, name):

        

        return self._metrics_by_name[name].width



    def get_kern_dist_from_name(self, name1, name2):

        

        return self._kern.get((name1, name2), 0)



    def get_fontname(self):

        

        return self._header[b'FontName']



    @property

    def postscript_name(self):                                 

        return self.get_fontname()



    def get_fullname(self):

        

        name = self._header.get(b'FullName')

        if name is None:                                

            name = self._header[b'FontName']

        return name



    def get_familyname(self):

        

        name = self._header.get(b'FamilyName')

        if name is not None:

            return name



                                                        

        name = self.get_fullname()

        extras = (r'(?i)([ -](regular|plain|italic|oblique|bold|semibold|'

                  r'light|ultralight|extra|condensed))+$')

        return re.sub(extras, '', name)



    @property

    def family_name(self):                                 

        

        return self.get_familyname()



    def get_weight(self):

        

        return self._header[b'Weight']



    def get_angle(self):

        

        return self._header[b'ItalicAngle']



    def get_capheight(self):

        

        return self._header[b'CapHeight']



    def get_xheight(self):

        

        return self._header[b'XHeight']



    def get_underline_thickness(self):

        

        return self._header[b'UnderlineThickness']


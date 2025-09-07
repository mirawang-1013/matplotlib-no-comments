



                                                                           

                                                                              

                                                                             



from functools import cache, lru_cache, partial

import re



from pyparsing import (

    Group, Optional, ParseException, Regex, StringEnd, Suppress, ZeroOrMore, one_of)





_family_punc = r'\\\-:,'

_family_unescape = partial(re.compile(r'\\(?=[%s])' % _family_punc).sub, '')

_family_escape = partial(re.compile(r'(?=[%s])' % _family_punc).sub, r'\\')

_value_punc = r'\\=_:,'

_value_unescape = partial(re.compile(r'\\(?=[%s])' % _value_punc).sub, '')

_value_escape = partial(re.compile(r'(?=[%s])' % _value_punc).sub, r'\\')





_CONSTANTS = {

    'thin':           ('weight', 'light'),

    'extralight':     ('weight', 'light'),

    'ultralight':     ('weight', 'light'),

    'light':          ('weight', 'light'),

    'book':           ('weight', 'book'),

    'regular':        ('weight', 'regular'),

    'normal':         ('weight', 'normal'),

    'medium':         ('weight', 'medium'),

    'demibold':       ('weight', 'demibold'),

    'semibold':       ('weight', 'semibold'),

    'bold':           ('weight', 'bold'),

    'extrabold':      ('weight', 'extra bold'),

    'black':          ('weight', 'black'),

    'heavy':          ('weight', 'heavy'),

    'roman':          ('slant', 'normal'),

    'italic':         ('slant', 'italic'),

    'oblique':        ('slant', 'oblique'),

    'ultracondensed': ('width', 'ultra-condensed'),

    'extracondensed': ('width', 'extra-condensed'),

    'condensed':      ('width', 'condensed'),

    'semicondensed':  ('width', 'semi-condensed'),

    'expanded':       ('width', 'expanded'),

    'extraexpanded':  ('width', 'extra-expanded'),

    'ultraexpanded':  ('width', 'ultra-expanded'),

}





@cache                                       

def _make_fontconfig_parser():

    def comma_separated(elem):

        return elem + ZeroOrMore(Suppress(",") + elem)



    family = Regex(fr"([^{_family_punc}]|(\\[{_family_punc}]))*")

    size = Regex(r"([0-9]+\.?[0-9]*|\.[0-9]+)")

    name = Regex(r"[a-z]+")

    value = Regex(fr"([^{_value_punc}]|(\\[{_value_punc}]))*")

    prop = Group((name + Suppress("=") + comma_separated(value)) | one_of(_CONSTANTS))

    return (

        Optional(comma_separated(family)("families"))

        + Optional("-" + comma_separated(size)("sizes"))

        + ZeroOrMore(":" + prop("properties*"))

        + StringEnd()

    )





                                                                           

                                                                        

                                                                              

                        

@lru_cache

def parse_fontconfig_pattern(pattern):

    

    parser = _make_fontconfig_parser()

    try:

        parse = parser.parse_string(pattern)

    except ParseException as err:

                                                                         

        raise ValueError("\n" + ParseException.explain(err, 0)) from None

    parser.reset_cache()

    props = {}

    if "families" in parse:

        props["family"] = [*map(_family_unescape, parse["families"])]

    if "sizes" in parse:

        props["size"] = [*parse["sizes"]]

    for prop in parse.get("properties", []):

        if len(prop) == 1:

            prop = _CONSTANTS[prop[0]]

        k, *v = prop

        props.setdefault(k, []).extend(map(_value_unescape, v))

    return props





def generate_fontconfig_pattern(d):

    

    kvs = [(k, getattr(d, f"get_{k}")())

           for k in ["style", "variant", "weight", "stretch", "file", "size"]]

                                                                              

                                                                     

    return (",".join(_family_escape(f) for f in d.get_family())

            + "".join(f":{k}={_value_escape(str(v))}"

                      for k, v in kvs if v is not None))


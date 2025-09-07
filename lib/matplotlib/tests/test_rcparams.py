import copy

import os

import subprocess

import sys

from unittest import mock



from cycler import cycler, Cycler

from packaging.version import parse as parse_version

import pytest



import matplotlib as mpl

from matplotlib import _api, _c_internal_utils

import matplotlib.pyplot as plt

import matplotlib.colors as mcolors

import numpy as np

from matplotlib.rcsetup import (

    validate_bool,

    validate_color,

    validate_colorlist,

    _validate_color_or_linecolor,

    validate_cycler,

    validate_float,

    validate_fontstretch,

    validate_fontweight,

    validate_hatch,

    validate_hist_bins,

    validate_int,

    validate_markevery,

    validate_stringlist,

    validate_sketch,

    _validate_linestyle,

    _listify_validator)

from matplotlib.testing import subprocess_run_for_testing





def test_rcparams(tmp_path):

    mpl.rc('text', usetex=False)

    mpl.rc('lines', linewidth=22)



    usetex = mpl.rcParams['text.usetex']

    linewidth = mpl.rcParams['lines.linewidth']



    rcpath = tmp_path / 'test_rcparams.rc'

    rcpath.write_text('lines.linewidth: 33', encoding='utf-8')



                                   

    with mpl.rc_context(rc={'text.usetex': not usetex}):

        assert mpl.rcParams['text.usetex'] == (not usetex)

    assert mpl.rcParams['text.usetex'] == usetex



                                                               

    with mpl.rc_context(fname=rcpath):

        assert mpl.rcParams['lines.linewidth'] == 33

    assert mpl.rcParams['lines.linewidth'] == linewidth



                                                

    with mpl.rc_context(fname=rcpath, rc={'lines.linewidth': 44}):

        assert mpl.rcParams['lines.linewidth'] == 44

    assert mpl.rcParams['lines.linewidth'] == linewidth



                                                                             

    @mpl.rc_context({'lines.linewidth': 44})

    def func():

        assert mpl.rcParams['lines.linewidth'] == 44



    func()

    func()



                  

    mpl.rc_file(rcpath)

    assert mpl.rcParams['lines.linewidth'] == 33





def test_RcParams_class():

    rc = mpl.RcParams({'font.cursive': ['Apple Chancery',

                                        'Textile',

                                        'Zapf Chancery',

                                        'cursive'],

                       'font.family': 'sans-serif',

                       'font.weight': 'normal',

                       'font.size': 12})



    expected_repr = """
RcParams({'font.cursive': ['Apple Chancery',
                           'Textile',
                           'Zapf Chancery',
                           'cursive'],
          'font.family': ['sans-serif'],
          'font.size': 12.0,
          'font.weight': 'normal'})""".lstrip()



    assert expected_repr == repr(rc)



    expected_str = """
font.cursive: ['Apple Chancery', 'Textile', 'Zapf Chancery', 'cursive']
font.family: ['sans-serif']
font.size: 12.0
font.weight: normal""".lstrip()



    assert expected_str == str(rc)



                                     

    assert ['font.cursive', 'font.size'] == sorted(rc.find_all('i[vz]'))

    assert ['font.family'] == list(rc.find_all('family'))





def test_rcparams_update():

    rc = mpl.RcParams({'figure.figsize': (3.5, 42)})

    bad_dict = {'figure.figsize': (3.5, 42, 1)}

                                           

    with pytest.raises(ValueError):

        rc.update(bad_dict)





def test_rcparams_init():

    with pytest.raises(ValueError):

        mpl.RcParams({'figure.figsize': (3.5, 42, 1)})





def test_nargs_cycler():

    from matplotlib.rcsetup import cycler as ccl

    with pytest.raises(TypeError, match='3 were given'):

                                       

        ccl(ccl(color=list('rgb')), 2, 3)





def test_Bug_2543():

                                                                  

                                                          

                                                                        

                                                                        

                                

    with _api.suppress_matplotlib_deprecation_warning():

        with mpl.rc_context():

            _copy = mpl.rcParams.copy()

            for key in _copy:

                mpl.rcParams[key] = _copy[key]

        with mpl.rc_context():

            copy.deepcopy(mpl.rcParams)

    with pytest.raises(ValueError):

        validate_bool(None)

    with pytest.raises(ValueError):

        with mpl.rc_context():

            mpl.rcParams['svg.fonttype'] = True





legend_color_tests = [

    ('face', {'color': 'r'}, mcolors.to_rgba('r')),

    ('face', {'color': 'inherit', 'axes.facecolor': 'r'},

     mcolors.to_rgba('r')),

    ('face', {'color': 'g', 'axes.facecolor': 'r'}, mcolors.to_rgba('g')),

    ('edge', {'color': 'r'}, mcolors.to_rgba('r')),

    ('edge', {'color': 'inherit', 'axes.edgecolor': 'r'},

     mcolors.to_rgba('r')),

    ('edge', {'color': 'g', 'axes.facecolor': 'r'}, mcolors.to_rgba('g'))

]

legend_color_test_ids = [

    'same facecolor',

    'inherited facecolor',

    'different facecolor',

    'same edgecolor',

    'inherited edgecolor',

    'different facecolor',

]





@pytest.mark.parametrize('color_type, param_dict, target', legend_color_tests,

                         ids=legend_color_test_ids)

def test_legend_colors(color_type, param_dict, target):

    param_dict[f'legend.{color_type}color'] = param_dict.pop('color')

    get_func = f'get_{color_type}color'



    with mpl.rc_context(param_dict):

        _, ax = plt.subplots()

        ax.plot(range(3), label='test')

        leg = ax.legend()

        assert getattr(leg.legendPatch, get_func)() == target





def test_mfc_rcparams():

    mpl.rcParams['lines.markerfacecolor'] = 'r'

    ln = mpl.lines.Line2D([1, 2], [1, 2])

    assert ln.get_markerfacecolor() == 'r'





def test_mec_rcparams():

    mpl.rcParams['lines.markeredgecolor'] = 'r'

    ln = mpl.lines.Line2D([1, 2], [1, 2])

    assert ln.get_markeredgecolor() == 'r'





def test_axes_titlecolor_rcparams():

    mpl.rcParams['axes.titlecolor'] = 'r'

    _, ax = plt.subplots()

    title = ax.set_title("Title")

    assert title.get_color() == 'r'





def test_Issue_1713(tmp_path):

    rcpath = tmp_path / 'test_rcparams.rc'

    rcpath.write_text('timezone: UTC', encoding='utf-8')

    with mock.patch('locale.getpreferredencoding', return_value='UTF-32-BE'):

        rc = mpl.rc_params_from_file(rcpath, True, False)

    assert rc.get('timezone') == 'UTC'





def test_animation_frame_formats():

                                                              

                                                                  

                              

    for fmt in ['png', 'jpeg', 'tiff', 'raw', 'rgba', 'ppm',

                'sgi', 'bmp', 'pbm', 'svg']:

        mpl.rcParams['animation.frame_format'] = fmt





def generate_validator_testcases(valid):

    validation_tests = (

        {'validator': validate_bool,

         'success': (*((_, True) for _ in

                       ('t', 'y', 'yes', 'on', 'true', '1', 1, True)),

                     *((_, False) for _ in

                       ('f', 'n', 'no', 'off', 'false', '0', 0, False))),

         'fail': ((_, ValueError)

                  for _ in ('aardvark', 2, -1, [], ))

         },

        {'validator': validate_stringlist,

         'success': (('', []),

                     ('a,b', ['a', 'b']),

                     ('aardvark', ['aardvark']),

                     ('aardvark, ', ['aardvark']),

                     ('aardvark, ,', ['aardvark']),

                     (['a', 'b'], ['a', 'b']),

                     (('a', 'b'), ['a', 'b']),

                     (iter(['a', 'b']), ['a', 'b']),

                     (np.array(['a', 'b']), ['a', 'b']),

                     ),

         'fail': ((set(), ValueError),

                  (1, ValueError),

                  )

         },

        {'validator': _listify_validator(validate_int, n=2),

         'success': ((_, [1, 2])

                     for _ in ('1, 2', [1.5, 2.5], [1, 2],

                               (1, 2), np.array((1, 2)))),

         'fail': ((_, ValueError)

                  for _ in ('aardvark', ('a', 1),

                            (1, 2, 3)

                            ))

         },

        {'validator': _listify_validator(validate_float, n=2),

         'success': ((_, [1.5, 2.5])

                     for _ in ('1.5, 2.5', [1.5, 2.5], [1.5, 2.5],

                               (1.5, 2.5), np.array((1.5, 2.5)))),

         'fail': ((_, ValueError)

                  for _ in ('aardvark', ('a', 1), (1, 2, 3), (None, ), None))

         },

        {'validator': validate_cycler,

         'success': (('cycler("color", "rgb")',

                      cycler("color", 'rgb')),

                     ('cycler("color", "Dark2")',

                      cycler("color", mpl.color_sequences["Dark2"])),

                     (cycler('linestyle', ['-', '--']),

                      cycler('linestyle', ['-', '--'])),

                     ("""(cycler("color", ["r", "g", "b"]) +
                          cycler("mew", [2, 3, 5]))""",

                      (cycler("color", 'rgb') +

                       cycler("markeredgewidth", [2, 3, 5]))),

                     ("cycler(c='rgb', lw=[1, 2, 3])",

                      cycler('color', 'rgb') + cycler('linewidth', [1, 2, 3])),

                     ("cycler('c', 'rgb') * cycler('linestyle', ['-', '--'])",

                      (cycler('color', 'rgb') *

                       cycler('linestyle', ['-', '--']))),

                     (cycler('ls', ['-', '--']),

                      cycler('linestyle', ['-', '--'])),

                     (cycler(mew=[2, 5]),

                      cycler('markeredgewidth', [2, 5])),

                     ),

                                                                      

                                                                     

                                            

                                                                           

                                                                       

                                                                        

                      

         'fail': ((4, ValueError),                                      

                  ('cycler("bleh, [])', ValueError),                

                  ('Cycler("linewidth", [1, 2, 3])',

                   ValueError),                                       

                                                          

                  ("cycler('c', [j.__class__(j) for j in ['r', 'b']])",

                   ValueError),

                  ("cycler('c', [j. __class__(j) for j in ['r', 'b']])",

                   ValueError),

                  ("cycler('c', [j.\t__class__(j) for j in ['r', 'b']])",

                   ValueError),

                  ("cycler('c', [j.\u000c__class__(j) for j in ['r', 'b']])",

                   ValueError),

                  ("cycler('c', [j.__class__(j).lower() for j in ['r', 'b']])",

                   ValueError),

                  ('1 + 2', ValueError),                                   

                  ('os.system("echo Gotcha")', ValueError),                    

                  ('import os', ValueError),                                

                  ('def badjuju(a): return a; badjuju(cycler("color", "rgb"))',

                   ValueError),                                         

                                                   

                  ('cycler("waka", [1, 2, 3])', ValueError),                  

                  ('cycler(c=[1, 2, 3])', ValueError),                  

                  ("cycler(lw=['a', 'b', 'c'])", ValueError),                  

                  (cycler('waka', [1, 3, 5]), ValueError),                  

                  (cycler('color', ['C1', 'r', 'g']), ValueError)         

                  )

         },

        {'validator': validate_hatch,

         'success': (('--|', '--|'), ('\\oO', '\\oO'),

                     ('/+*/.x', '/+*/.x'), ('', '')),

         'fail': (('--_', ValueError),

                  (8, ValueError),

                  ('X', ValueError)),

         },

        {'validator': validate_colorlist,

         'success': (('r,g,b', ['r', 'g', 'b']),

                     (['r', 'g', 'b'], ['r', 'g', 'b']),

                     ('r, ,', ['r']),

                     (['', 'g', 'blue'], ['g', 'blue']),

                     ([np.array([1, 0, 0]), np.array([0, 1, 0])],

                     np.array([[1, 0, 0], [0, 1, 0]])),

                     (np.array([[1, 0, 0], [0, 1, 0]]),

                     np.array([[1, 0, 0], [0, 1, 0]])),

                     ),

         'fail': (('fish', ValueError),

                  ),

         },

        {'validator': validate_color,

         'success': (('None', 'none'),

                     ('none', 'none'),

                     ('AABBCC', '#AABBCC'),                

                     ('AABBCC00', '#AABBCC00'),                 

                     ('tab:blue', 'tab:blue'),               

                     ('C12', 'C12'),                    

                     ('(0, 1, 0)', (0.0, 1.0, 0.0)),             

                     ((0, 1, 0), (0, 1, 0)),                      

                     ('(0, 1, 0, 1)', (0.0, 1.0, 0.0, 1.0)),              

                     ((0, 1, 0, 1), (0, 1, 0, 1)),                      

                     ),

         'fail': (('tab:veryblue', ValueError),                

                  ('(0, 1)', ValueError),                         

                  ('(0, 1, 0, 1, 0)', ValueError),                         

                  ('(0, 1, none)', ValueError),                             

                  ('(0, 1, "0.5")', ValueError),                        

                  ),

         },

        {'validator': _validate_color_or_linecolor,

         'success': (('linecolor', 'linecolor'),

                     ('markerfacecolor', 'markerfacecolor'),

                     ('mfc', 'markerfacecolor'),

                     ('markeredgecolor', 'markeredgecolor'),

                     ('mec', 'markeredgecolor')

                     ),

         'fail': (('line', ValueError),

                  ('marker', ValueError)

                  )

         },

        {'validator': validate_hist_bins,

         'success': (('auto', 'auto'),

                     ('fd', 'fd'),

                     ('10', 10),

                     ('1, 2, 3', [1, 2, 3]),

                     ([1, 2, 3], [1, 2, 3]),

                     (np.arange(15), np.arange(15))

                     ),

         'fail': (('aardvark', ValueError),

                  )

         },

        {'validator': validate_markevery,

         'success': ((None, None),

                     (1, 1),

                     (0.1, 0.1),

                     ((1, 1), (1, 1)),

                     ((0.1, 0.1), (0.1, 0.1)),

                     ([1, 2, 3], [1, 2, 3]),

                     (slice(2), slice(None, 2, None)),

                     (slice(1, 2, 3), slice(1, 2, 3))

                     ),

         'fail': (((1, 2, 3), TypeError),

                  ([1, 2, 0.3], TypeError),

                  (['a', 2, 3], TypeError),

                  ([1, 2, 'a'], TypeError),

                  ((0.1, 0.2, 0.3), TypeError),

                  ((0.1, 2, 3), TypeError),

                  ((1, 0.2, 0.3), TypeError),

                  ((1, 0.1), TypeError),

                  ((0.1, 1), TypeError),

                  (('abc'), TypeError),

                  ((1, 'a'), TypeError),

                  ((0.1, 'b'), TypeError),

                  (('a', 1), TypeError),

                  (('a', 0.1), TypeError),

                  ('abc', TypeError),

                  ('a', TypeError),

                  (object(), TypeError)

                  )

         },

        {'validator': _validate_linestyle,

         'success': (('-', '-'), ('solid', 'solid'),

                     ('--', '--'), ('dashed', 'dashed'),

                     ('-.', '-.'), ('dashdot', 'dashdot'),

                     (':', ':'), ('dotted', 'dotted'),

                     ('', ''), (' ', ' '),

                     ('None', 'none'), ('none', 'none'),

                     ('DoTtEd', 'dotted'),                    

                     ('1, 3', (0, (1, 3))),

                     ([1.23, 456], (0, [1.23, 456.0])),

                     ([1, 2, 3, 4], (0, [1.0, 2.0, 3.0, 4.0])),

                     ((0, [1, 2]), (0, [1, 2])),

                     ((-1, [1, 2]), (-1, [1, 2])),

                     ),

         'fail': (('aardvark', ValueError),                      

                  (b'dotted', ValueError),

                  ('dotted'.encode('utf-16'), ValueError),

                  ([1, 2, 3], ValueError),                            

                  (1.23, ValueError),                  

                  (("a", [1, 2]), ValueError),                         

                  ((None, [1, 2]), ValueError),                         

                  ((1, [1, 2, 3]), ValueError),                       

                  (([1, 2], 1), ValueError),                         

                  )

         },

    )



    for validator_dict in validation_tests:

        validator = validator_dict['validator']

        if valid:

            for arg, target in validator_dict['success']:

                yield validator, arg, target

        else:

            for arg, error_type in validator_dict['fail']:

                yield validator, arg, error_type





@pytest.mark.parametrize('validator, arg, target',

                         generate_validator_testcases(True))

def test_validator_valid(validator, arg, target):

    res = validator(arg)

    if isinstance(target, np.ndarray):

        np.testing.assert_equal(res, target)

    elif not isinstance(target, Cycler):

        assert res == target

    else:

                                                                             

        assert list(res) == list(target)





@pytest.mark.parametrize('validator, arg, exception_type',

                         generate_validator_testcases(False))

def test_validator_invalid(validator, arg, exception_type):

    with pytest.raises(exception_type):

        validator(arg)





def test_validate_cycler_bad_color_string():

    msg = "'foo' is neither a color sequence name nor can it be interpreted as a list"

    with pytest.raises(ValueError, match=msg):

        validate_cycler("cycler('color', 'foo')")





@pytest.mark.parametrize('weight, parsed_weight', [

    ('bold', 'bold'),

    ('BOLD', ValueError),                            

    (100, 100),

    ('100', 100),

    (np.array(100), 100),

                                                                          

                                           

    (20.6, 20),

    ('20.6', ValueError),

    ([100], ValueError),

])

def test_validate_fontweight(weight, parsed_weight):

    if parsed_weight is ValueError:

        with pytest.raises(ValueError):

            validate_fontweight(weight)

    else:

        assert validate_fontweight(weight) == parsed_weight





@pytest.mark.parametrize('stretch, parsed_stretch', [

    ('expanded', 'expanded'),

    ('EXPANDED', ValueError),                             

    (100, 100),

    ('100', 100),

    (np.array(100), 100),

                                                                          

                                           

    (20.6, 20),

    ('20.6', ValueError),

    ([100], ValueError),

])

def test_validate_fontstretch(stretch, parsed_stretch):

    if parsed_stretch is ValueError:

        with pytest.raises(ValueError):

            validate_fontstretch(stretch)

    else:

        assert validate_fontstretch(stretch) == parsed_stretch





def test_keymaps():

    key_list = [k for k in mpl.rcParams if 'keymap' in k]

    for k in key_list:

        assert isinstance(mpl.rcParams[k], list)





def test_no_backend_reset_rccontext():

    assert mpl.rcParams['backend'] != 'module://aardvark'

    with mpl.rc_context():

        mpl.rcParams['backend'] = 'module://aardvark'

    assert mpl.rcParams['backend'] == 'module://aardvark'





def test_rcparams_reset_after_fail():

                                                                         

                                                                          

                                                         

    with mpl.rc_context(rc={'text.usetex': False}):

        assert mpl.rcParams['text.usetex'] is False

        with pytest.raises(KeyError):

            with mpl.rc_context(rc={'text.usetex': True, 'test.blah': True}):

                pass

        assert mpl.rcParams['text.usetex'] is False





@pytest.mark.skipif(sys.platform != "linux", reason="Linux only")

def test_backend_fallback_headless_invalid_backend(tmp_path):

    env = {**os.environ,

           "DISPLAY": "", "WAYLAND_DISPLAY": "",

           "MPLBACKEND": "", "MPLCONFIGDIR": str(tmp_path)}

                                                                                    

    with pytest.raises(subprocess.CalledProcessError):

        subprocess_run_for_testing(

            [sys.executable, "-c",

             "import matplotlib;"

             "matplotlib.use('tkagg');"

             "import matplotlib.pyplot;"

             "matplotlib.pyplot.plot(42);"

             ],

            env=env, check=True, stderr=subprocess.DEVNULL)





@pytest.mark.skipif(sys.platform != "linux", reason="Linux only")

def test_backend_fallback_headless_auto_backend(tmp_path):

                                                                              

    env = {**os.environ,

           "DISPLAY": "", "WAYLAND_DISPLAY": "",

           "MPLBACKEND": "TkAgg", "MPLCONFIGDIR": str(tmp_path)}



                                                                                    

    rc_path = tmp_path / "matplotlibrc"

    rc_path.write_text("backend_fallback: true")



                                                                             

    backend = subprocess_run_for_testing(

        [sys.executable, "-c",

         "import matplotlib.pyplot;"

         "matplotlib.pyplot.plot(42);"

         "print(matplotlib.get_backend());"

         ],

        env=env, text=True, check=True, capture_output=True).stdout

    assert backend.strip().lower() == "agg"





@pytest.mark.skipif(

    sys.platform == "linux" and not _c_internal_utils.xdisplay_is_valid(),

    reason="headless")

def test_backend_fallback_headful(tmp_path):

    if parse_version(pytest.__version__) >= parse_version('8.2.0'):

        pytest_kwargs = dict(exc_type=ImportError)

    else:

        pytest_kwargs = {}



    pytest.importorskip("tkinter", **pytest_kwargs)

    env = {**os.environ, "MPLBACKEND": "", "MPLCONFIGDIR": str(tmp_path)}

    backend = subprocess_run_for_testing(

        [sys.executable, "-c",

         "import matplotlib as mpl; "

         "sentinel = mpl.rcsetup._auto_backend_sentinel; "

                                                                               

         "assert mpl.RcParams({'backend': sentinel})['backend'] == sentinel; "

         "assert mpl.rcParams._get('backend') == sentinel; "

         "assert mpl.get_backend(auto_select=False) is None; "

         "import matplotlib.pyplot; "

         "print(matplotlib.get_backend())"],

        env=env, text=True, check=True, capture_output=True).stdout

                                                                               

              

    assert backend.strip().lower() != "agg"





def test_deprecation(monkeypatch):

    mpl.rcParams.update(mpl.rcParams.copy())                 

                                                                

                                                            

                                                                              





@pytest.mark.parametrize("value", [

    "best",

    1,

    "1",

    (0.9, .7),

    (-0.9, .7),

    "(0.9, .7)"

])

def test_rcparams_legend_loc(value):

                                                                       

                                                                  

                              

    mpl.rcParams["legend.loc"] = value





@pytest.mark.parametrize("value", [

    "best",

    1,

    (0.9, .7),

    (-0.9, .7),

])

def test_rcparams_legend_loc_from_file(tmp_path, value):

                                                                  

                                                                   

                              

    rc_path = tmp_path / "matplotlibrc"

    rc_path.write_text(f"legend.loc: {value}")



    with mpl.rc_context(fname=rc_path):

        assert mpl.rcParams["legend.loc"] == value





@pytest.mark.parametrize("value", [(1, 2, 3), '1, 2, 3', '(1, 2, 3)'])

def test_validate_sketch(value):

    mpl.rcParams["path.sketch"] = value

    assert mpl.rcParams["path.sketch"] == (1, 2, 3)

    assert validate_sketch(value) == (1, 2, 3)





@pytest.mark.parametrize("value", [1, '1', '1 2 3'])

def test_validate_sketch_error(value):

    with pytest.raises(ValueError, match="scale, length, randomness"):

        validate_sketch(value)

    with pytest.raises(ValueError, match="scale, length, randomness"):

        mpl.rcParams["path.sketch"] = value





@pytest.mark.parametrize("value", ['1, 2, 3', '(1,2,3)'])

def test_rcparams_path_sketch_from_file(tmp_path, value):

    rc_path = tmp_path / "matplotlibrc"

    rc_path.write_text(f"path.sketch: {value}")

    with mpl.rc_context(fname=rc_path):

        assert mpl.rcParams["path.sketch"] == (1, 2, 3)





@pytest.mark.parametrize('group, option, alias, value', [

    ('lines',  'linewidth',        'lw', 3),

    ('lines',  'linestyle',        'ls', 'dashed'),

    ('lines',  'color',             'c', 'white'),

    ('axes',   'facecolor',        'fc', 'black'),

    ('figure', 'edgecolor',        'ec', 'magenta'),

    ('lines',  'markeredgewidth', 'mew', 1.5),

    ('patch',  'antialiased',      'aa', False),

    ('font',   'sans-serif',     'sans', ["Verdana"])

])

def test_rc_aliases(group, option, alias, value):

    rc_kwargs = {alias: value,}

    mpl.rc(group, **rc_kwargs)



    rcParams_key = f"{group}.{option}"

    assert mpl.rcParams[rcParams_key] == value


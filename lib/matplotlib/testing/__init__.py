

import itertools

import locale

import logging

import os

from pathlib import Path

import string

import subprocess

import sys

from tempfile import TemporaryDirectory



import matplotlib as mpl

from matplotlib import _api



_log = logging.getLogger(__name__)





def set_font_settings_for_testing():

    mpl.rcParams['font.family'] = 'DejaVu Sans'

    mpl.rcParams['text.hinting'] = 'none'

    mpl.rcParams['text.hinting_factor'] = 8





def set_reproducibility_for_testing():

    mpl.rcParams['svg.hashsalt'] = 'matplotlib'





def setup():

                                                                      

                                 



    try:

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    except locale.Error:

        try:

            locale.setlocale(locale.LC_ALL, 'English_United States.1252')

        except locale.Error:

            _log.warning(

                "Could not set locale to English/United States. "

                "Some date-related tests may fail.")



    mpl.use('Agg')



    with _api.suppress_matplotlib_deprecation_warning():

        mpl.rcdefaults()                           



                                                                             

                                                                        

    set_font_settings_for_testing()

    set_reproducibility_for_testing()





def subprocess_run_for_testing(command, env=None, timeout=60, stdout=None,

                               stderr=None, check=False, text=True,

                               capture_output=False):

    

    if capture_output:

        stdout = stderr = subprocess.PIPE

    try:

        proc = subprocess.run(

            command, env=env,

            timeout=timeout, check=check,

            stdout=stdout, stderr=stderr,

            text=text

        )

    except BlockingIOError:

        if sys.platform == "cygwin":

                                                   

            import pytest

            pytest.xfail("Fork failure")

        raise

    except subprocess.CalledProcessError as e:

        if e.stdout:

            _log.error(f"Subprocess output:\n{e.stdout}")

        if e.stderr:

            _log.error(f"Subprocess error:\n{e.stderr}")

        raise e

    if proc.stdout:

        _log.debug(f"Subprocess output:\n{proc.stdout}")

    if proc.stderr:

        _log.debug(f"Subprocess error:\n{proc.stderr}")

    return proc





def subprocess_run_helper(func, *args, timeout, extra_env=None):

    

    target = func.__name__

    module = func.__module__

    file = func.__code__.co_filename

    proc = subprocess_run_for_testing(

        [

            sys.executable,

            "-c",

            f"import importlib.util;"

            f"_spec = importlib.util.spec_from_file_location({module!r}, {file!r});"

            f"_module = importlib.util.module_from_spec(_spec);"

            f"_spec.loader.exec_module(_module);"

            f"_module.{target}()",

            *args

        ],

        env={**os.environ, "SOURCE_DATE_EPOCH": "0", **(extra_env or {})},

        timeout=timeout, check=True,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )

    return proc





def _check_for_pgf(texsystem):

    

    with TemporaryDirectory() as tmpdir:

        tex_path = Path(tmpdir, "test.tex")

        tex_path.write_text(r"""
            \documentclass{article}
            \usepackage{pgf}
            \begin{document}
            \typeout{pgfversion=\pgfversion}
            \makeatletter
            \@@end
        """, encoding="utf-8")

        try:

            subprocess.check_call(

                [texsystem, "-halt-on-error", str(tex_path)], cwd=tmpdir,

                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        except (OSError, subprocess.CalledProcessError):

            return False

        return True





def _has_tex_package(package):

    try:

        mpl.dviread.find_tex_file(f"{package}.sty")

        return True

    except FileNotFoundError:

        return False





def ipython_in_subprocess(requested_backend_or_gui_framework, all_expected_backends):

    import pytest

    IPython = pytest.importorskip("IPython")



    if sys.platform == "win32":

        pytest.skip("Cannot change backend running IPython in subprocess on Windows")



    if (IPython.version_info[:3] == (8, 24, 0) and

            requested_backend_or_gui_framework == "osx"):

        pytest.skip("Bug using macosx backend in IPython 8.24.0 fixed in 8.24.1")



                                                                             

                                                          

    for min_version, backend in all_expected_backends.items():

        if IPython.version_info[:2] >= min_version:

            expected_backend = backend

            break



    code = ("import matplotlib as mpl, matplotlib.pyplot as plt;"

            "fig, ax=plt.subplots(); ax.plot([1, 3, 2]); mpl.get_backend()")

    proc = subprocess_run_for_testing(

        [

            "ipython",

            "--no-simple-prompt",

            f"--matplotlib={requested_backend_or_gui_framework}",

            "-c", code,

        ],

        check=True,

        capture_output=True,

    )



    assert proc.stdout.strip().endswith(f"'{expected_backend}'")





def is_ci_environment():

                         

    ci_environment_variables = [

        'CI',                                         

        'CONTINUOUS_INTEGRATION',                                   

        'TRAVIS',               

        'CIRCLECI',            

        'JENKINS',            

        'GITLAB_CI',             

        'GITHUB_ACTIONS',                  

        'TEAMCITY_VERSION'            

                                                      

    ]



    for env_var in ci_environment_variables:

        if os.getenv(env_var):

            return True



    return False





def _gen_multi_font_text():

    

                                                                                        

                                                                  

    fonts = ['cmr10', 'DejaVu Sans']

                                                                                    

                                                                                      

                                                                                     

                     

    start = 0xC5

    latin1_supplement = [chr(x) for x in range(start, 0xFF+1)]

    latin_extended_A = [chr(x) for x in range(0x100, 0x17F+1)]

    latin_extended_B = [chr(x) for x in range(0x180, 0x24F+1)]

    count = itertools.count(start - 0xA0)

    non_basic_characters = '\n'.join(

        ''.join(line)

        for _, line in itertools.groupby(                                               

            [*latin1_supplement, *latin_extended_A, *latin_extended_B],

            key=lambda x: next(count) // 32)                           

    )

    test_str = f"""There are basic characters
{string.ascii_uppercase} {string.ascii_lowercase}
{string.digits} {string.punctuation}
and accented characters
{non_basic_characters}
in between!"""

                                                                                      

                                                                        

    return fonts, test_str


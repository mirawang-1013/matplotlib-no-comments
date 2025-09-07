import copy

import importlib

import os

import signal

import sys



from datetime import date, datetime

from unittest import mock



import pytest



import matplotlib

from matplotlib import pyplot as plt

from matplotlib._pylab_helpers import Gcf

from matplotlib import _c_internal_utils



try:

    from matplotlib.backends.qt_compat import QtCore                              

    from matplotlib.backends.qt_compat import QtGui                                                  

    from matplotlib.backends.qt_compat import QtWidgets                              

    from matplotlib.backends.qt_editor import _formlayout

except ImportError:

    pytestmark = pytest.mark.skip('No usable Qt bindings')





_test_timeout = 60                                                     





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_fig_close():



                                

    init_figs = copy.copy(Gcf.figs)



                                          

    fig = plt.figure()



                                                            

                                                   

    fig.canvas.manager.window.close()



                                                                    

                                    

    assert init_figs == Gcf.figs





@pytest.mark.parametrize(

    "qt_key, qt_mods, answer",

    [

        ("Key_A", ["ShiftModifier"], "A"),

        ("Key_A", [], "a"),

        ("Key_A", ["ControlModifier"], ("ctrl+a")),

        (

            "Key_Aacute",

            ["ShiftModifier"],

            "\N{LATIN CAPITAL LETTER A WITH ACUTE}",

        ),

        ("Key_Aacute", [], "\N{LATIN SMALL LETTER A WITH ACUTE}"),

        ("Key_Control", ["AltModifier"], ("alt+control")),

        ("Key_Alt", ["ControlModifier"], "ctrl+alt"),

        (

            "Key_Aacute",

            ["ControlModifier", "AltModifier", "MetaModifier"],

            ("ctrl+alt+meta+\N{LATIN SMALL LETTER A WITH ACUTE}"),

        ),

                                                                        

                                                          

        ("Key_Play", [], None),

        ("Key_Backspace", [], "backspace"),

        (

            "Key_Backspace",

            ["ControlModifier"],

            "ctrl+backspace",

        ),

    ],

    ids=[

        'shift',

        'lower',

        'control',

        'unicode_upper',

        'unicode_lower',

        'alt_control',

        'control_alt',

        'modifier_order',

        'non_unicode_key',

        'backspace',

        'backspace_mod',

    ]

)

@pytest.mark.parametrize('backend', [

                                                                      

    pytest.param(

        'Qt5Agg',

        marks=pytest.mark.backend('Qt5Agg', skip_on_importerror=True)),

    pytest.param(

        'QtAgg',

        marks=pytest.mark.backend('QtAgg', skip_on_importerror=True)),

])

def test_correct_key(backend, qt_key, qt_mods, answer, monkeypatch):

    

    from matplotlib.backends.qt_compat import _to_int, QtCore



    if sys.platform == "darwin" and answer is not None:

        answer = answer.replace("ctrl", "cmd")

        answer = answer.replace("control", "cmd")

        answer = answer.replace("meta", "ctrl")

    result = None

    qt_mod = QtCore.Qt.KeyboardModifier.NoModifier

    for mod in qt_mods:

        qt_mod |= getattr(QtCore.Qt.KeyboardModifier, mod)



    class _Event:

        def isAutoRepeat(self): return False

        def key(self): return _to_int(getattr(QtCore.Qt.Key, qt_key))



    monkeypatch.setattr(QtWidgets.QApplication, "keyboardModifiers",

                        lambda self: qt_mod)



    def on_key_press(event):

        nonlocal result

        result = event.key



    qt_canvas = plt.figure().canvas

    qt_canvas.mpl_connect('key_press_event', on_key_press)

    qt_canvas.keyPressEvent(_Event())

    assert result == answer





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_device_pixel_ratio_change():

    



    prop = 'matplotlib.backends.backend_qt.FigureCanvasQT.devicePixelRatioF'

    with mock.patch(prop) as p:

        p.return_value = 3



        fig = plt.figure(figsize=(5, 2), dpi=120)

        qt_canvas = fig.canvas

        qt_canvas.show()



        def set_device_pixel_ratio(ratio):

            p.return_value = ratio



            window = qt_canvas.window().windowHandle()

            current_version = tuple(int(x) for x in QtCore.qVersion().split('.', 2)[:2])

            if current_version >= (6, 6):

                QtCore.QCoreApplication.sendEvent(

                    window,

                    QtCore.QEvent(QtCore.QEvent.Type.DevicePixelRatioChange))

            else:

                                                                                 

                                                                            

                                                                                 

                                                                                

                window.screen().logicalDotsPerInchChanged.emit(96)



            qt_canvas.draw()

            qt_canvas.flush_events()



                                          

            assert qt_canvas.device_pixel_ratio == ratio



        qt_canvas.manager.show()

        qt_canvas.draw()

        qt_canvas.flush_events()

        size = qt_canvas.size()



        options = [

            (None, 360, 1800, 720),                              

            (3, 360, 1800, 720),                         

            (2, 240, 1200, 480),                              

            (1.5, 180, 900, 360),                     

        ]

        for ratio, dpi, width, height in options:

            if ratio is not None:

                set_device_pixel_ratio(ratio)



                                                          

            assert fig.dpi == dpi

            assert qt_canvas.renderer.width == width

            assert qt_canvas.renderer.height == height



                                                                          

            assert size.width() == 600

            assert size.height() == 240

            assert qt_canvas.get_width_height() == (600, 240)

            assert (fig.get_size_inches() == (5, 2)).all()





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_subplottool():

    fig, ax = plt.subplots()

    with mock.patch("matplotlib.backends.qt_compat._exec", lambda obj: None):

        tool = fig.canvas.manager.toolbar.configure_subplots()

        assert tool is not None

        assert tool == fig.canvas.manager.toolbar.configure_subplots()





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_figureoptions():

    fig, ax = plt.subplots()

    ax.plot([1, 2])

    ax.imshow([[1]])

    ax.scatter(range(3), range(3), c=range(3))

    with mock.patch("matplotlib.backends.qt_compat._exec", lambda obj: None):

        fig.canvas.manager.toolbar.edit_parameters()





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_save_figure_return():

    fig, ax = plt.subplots()

    ax.imshow([[1]])

    prop = "matplotlib.backends.qt_compat.QtWidgets.QFileDialog.getSaveFileName"

    with mock.patch(prop, return_value=("foobar.png", None)):

        fname = fig.canvas.manager.toolbar.save_figure()

        os.remove("foobar.png")

        assert fname == "foobar.png"

    with mock.patch(prop, return_value=(None, None)):

        fname = fig.canvas.manager.toolbar.save_figure()

        assert fname is None





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_figureoptions_with_datetime_axes():

    fig, ax = plt.subplots()

    xydata = [

        datetime(year=2021, month=1, day=1),

        datetime(year=2021, month=2, day=1)

    ]

    ax.plot(xydata, xydata)

    with mock.patch("matplotlib.backends.qt_compat._exec", lambda obj: None):

        fig.canvas.manager.toolbar.edit_parameters()





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_double_resize():

                                                                   

    fig, ax = plt.subplots()

    fig.canvas.draw()

    window = fig.canvas.manager.window



    w, h = 3, 2

    fig.set_size_inches(w, h)

    assert fig.canvas.width() == w * matplotlib.rcParams['figure.dpi']

    assert fig.canvas.height() == h * matplotlib.rcParams['figure.dpi']



    old_width = window.width()

    old_height = window.height()



    fig.set_size_inches(w, h)

    assert window.width() == old_width

    assert window.height() == old_height





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_canvas_reinit():

    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg



    called = False



    def crashing_callback(fig, stale):

        nonlocal called

        fig.canvas.draw_idle()

        called = True



    fig, ax = plt.subplots()

    fig.stale_callback = crashing_callback

                           

    canvas = FigureCanvasQTAgg(fig)

    fig.stale = True

    assert called





@pytest.mark.backend('Qt5Agg', skip_on_importerror=True)

def test_form_widget_get_with_datetime_and_date_fields():

    from matplotlib.backends.backend_qt import _create_qApp

    _create_qApp()



    form = [

        ("Datetime field", datetime(year=2021, month=3, day=11)),

        ("Date field", date(year=2021, month=3, day=11))

    ]

    widget = _formlayout.FormWidget(form)

    widget.setup()

    values = widget.get()

    assert values == [

        datetime(year=2021, month=3, day=11),

        date(year=2021, month=3, day=11)

    ]





def _get_testable_qt_backends():

    envs = []

    for deps, env in [

            ([qt_api], {"MPLBACKEND": "qtagg", "QT_API": qt_api})

            for qt_api in ["PyQt6", "PySide6", "PyQt5", "PySide2"]

    ]:

        reason = None

        missing = [dep for dep in deps if not importlib.util.find_spec(dep)]

        if (sys.platform == "linux" and

                not _c_internal_utils.display_is_valid()):

            reason = "$DISPLAY and $WAYLAND_DISPLAY are unset"

        elif missing:

            reason = "{} cannot be imported".format(", ".join(missing))

        elif env["MPLBACKEND"] == 'macosx' and os.environ.get('TF_BUILD'):

            reason = "macosx backend fails on Azure"

        marks = []

        if reason:

            marks.append(pytest.mark.skip(

                reason=f"Skipping {env} because {reason}"))

        envs.append(pytest.param(env, marks=marks, id=str(env)))

    return envs





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_fig_sigint_override():

    from matplotlib.backends.backend_qt5 import _BackendQT5

                     

    plt.figure()



                                                                      

    event_loop_handler = None



                                                                        

    def fire_signal_and_quit():

                                

        nonlocal event_loop_handler

        event_loop_handler = signal.getsignal(signal.SIGINT)



                                 

        QtCore.QCoreApplication.exit()



                              

    QtCore.QTimer.singleShot(0, fire_signal_and_quit)



                                  

    original_handler = signal.getsignal(signal.SIGINT)



                                                                

    def custom_handler(signum, frame):

        pass



    signal.signal(signal.SIGINT, custom_handler)



    try:

                                                                            

                                                      

        matplotlib.backends.backend_qt._BackendQT.mainloop()



                                                                 

                                         

        assert event_loop_handler != custom_handler



                                                                             

        assert signal.getsignal(signal.SIGINT) == custom_handler



                                                                              

        for custom_handler in (signal.SIG_DFL, signal.SIG_IGN):

            QtCore.QTimer.singleShot(0, fire_signal_and_quit)

            signal.signal(signal.SIGINT, custom_handler)



            _BackendQT5.mainloop()



            assert event_loop_handler == custom_handler

            assert signal.getsignal(signal.SIGINT) == custom_handler



    finally:

                                                             

        signal.signal(signal.SIGINT, original_handler)





@pytest.mark.backend('QtAgg', skip_on_importerror=True)

def test_ipython():

    from matplotlib.testing import ipython_in_subprocess

    ipython_in_subprocess("qt", {(8, 24): "qtagg", (8, 15): "QtAgg", (7, 0): "Qt5Agg"})


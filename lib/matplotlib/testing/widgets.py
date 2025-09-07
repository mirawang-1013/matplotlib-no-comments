



from unittest import mock



from matplotlib import _api

from matplotlib.backend_bases import MouseEvent, KeyEvent

import matplotlib.pyplot as plt





def get_ax():

    

    fig, ax = plt.subplots(1, 1)

    ax.plot([0, 200], [0, 200])

    ax.set_aspect(1.0)

    fig.canvas.draw()

    return ax





def noop(*args, **kwargs):

    pass





@_api.deprecated("3.11", alternative="MouseEvent or KeyEvent")

def mock_event(ax, button=1, xdata=0, ydata=0, key=None, step=1):

    

    event = mock.Mock()

    event.button = button

    event.x, event.y = ax.transData.transform([(xdata, ydata),

                                               (xdata, ydata)])[0]

    event.xdata, event.ydata = xdata, ydata

    event.inaxes = ax

    event.canvas = ax.get_figure(root=True).canvas

    event.key = key

    event.step = step

    event.guiEvent = None

    event.name = 'Custom'

    return event





@_api.deprecated("3.11", alternative="callbacks.process(event)")

def do_event(tool, etype, button=1, xdata=0, ydata=0, key=None, step=1):

    

    event = mock_event(tool.ax, button, xdata, ydata, key, step)

    func = getattr(tool, etype)

    func(event)





def click_and_drag(tool, start, end, key=None):

    

    ax = tool.ax

    if key is not None:             

        KeyEvent._from_ax_coords("key_press_event", ax, start, key)._process()

                                    

    MouseEvent._from_ax_coords("button_press_event", ax, start, 1)._process()

    MouseEvent._from_ax_coords("motion_notify_event", ax, end, 1)._process()

    MouseEvent._from_ax_coords("button_release_event", ax, end, 1)._process()

    if key is not None:               

        KeyEvent._from_ax_coords("key_release_event", ax, end, key)._process()


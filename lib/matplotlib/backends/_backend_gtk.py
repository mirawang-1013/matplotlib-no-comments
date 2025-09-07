



import logging

import sys



import matplotlib as mpl

from matplotlib import _api, backend_tools, cbook

from matplotlib._pylab_helpers import Gcf

from matplotlib.backend_bases import (

    _Backend, FigureCanvasBase, FigureManagerBase, NavigationToolbar2,

    TimerBase)

from matplotlib.backend_tools import Cursors



import gi

                                                                             

                  

from gi.repository import Gdk, Gio, GLib, Gtk





try:

    gi.require_foreign("cairo")

except ImportError as e:

    raise ImportError("Gtk-based backends require cairo") from e



_log = logging.getLogger(__name__)

_application = None               





def _shutdown_application(app):

                                                                             

                           

    for win in app.get_windows():

        win.close()

                                                                              

                      

                                       

                                                                            

    app._created_by_matplotlib = True

    global _application

    _application = None





def _create_application():

    global _application



    if _application is None:

        app = Gio.Application.get_default()

        if app is None or getattr(app, '_created_by_matplotlib', False):

                                                                             

                                                

            if not mpl._c_internal_utils.display_is_valid():

                raise RuntimeError('Invalid DISPLAY variable')

            _application = Gtk.Application.new('org.matplotlib.Matplotlib3',

                                               Gio.ApplicationFlags.NON_UNIQUE)

                                                                          

                                                                   

            _application.connect('activate', lambda *args, **kwargs: None)

            _application.connect('shutdown', _shutdown_application)

            _application.register()

            cbook._setup_new_guiapp()

        else:

            _application = app



    return _application





def mpl_to_gtk_cursor_name(mpl_cursor):

    return _api.check_getitem({

        Cursors.MOVE: "move",

        Cursors.HAND: "pointer",

        Cursors.POINTER: "default",

        Cursors.SELECT_REGION: "crosshair",

        Cursors.WAIT: "wait",

        Cursors.RESIZE_HORIZONTAL: "ew-resize",

        Cursors.RESIZE_VERTICAL: "ns-resize",

    }, cursor=mpl_cursor)





class TimerGTK(TimerBase):

    



    def __init__(self, *args, **kwargs):

        self._timer = None

        super().__init__(*args, **kwargs)



    def _timer_start(self):

                                                                             

                           

        self._timer_stop()

        self._timer = GLib.timeout_add(self._interval, self._on_timer)



    def _timer_stop(self):

        if self._timer is not None:

            GLib.source_remove(self._timer)

            self._timer = None



    def _timer_set_interval(self):

                                                                         

        if self._timer is not None:

            self._timer_stop()

            self._timer_start()



    def _on_timer(self):

        super()._on_timer()



                                                                         

                                

        if self.callbacks and not self._single:

            return True

        else:

            self._timer = None

            return False





class _FigureCanvasGTK(FigureCanvasBase):

    _timer_cls = TimerGTK





class _FigureManagerGTK(FigureManagerBase):

    



    def __init__(self, canvas, num):

        self._gtk_ver = gtk_ver = Gtk.get_major_version()



        app = _create_application()

        self.window = Gtk.Window()

        app.add_window(self.window)

        super().__init__(canvas, num)



        if gtk_ver == 3:

            icon_ext = "png" if sys.platform == "win32" else "svg"

            self.window.set_icon_from_file(

                str(cbook._get_data_path(f"images/matplotlib.{icon_ext}")))



        self.vbox = Gtk.Box()

        self.vbox.set_property("orientation", Gtk.Orientation.VERTICAL)



        if gtk_ver == 3:

            self.window.add(self.vbox)

            self.vbox.show()

            self.canvas.show()

            self.vbox.pack_start(self.canvas, True, True, 0)

        elif gtk_ver == 4:

            self.window.set_child(self.vbox)

            self.vbox.prepend(self.canvas)



                                   

        w, h = self.canvas.get_width_height()



        if self.toolbar is not None:

            if gtk_ver == 3:

                self.toolbar.show()

                self.vbox.pack_end(self.toolbar, False, False, 0)

            elif gtk_ver == 4:

                sw = Gtk.ScrolledWindow(vscrollbar_policy=Gtk.PolicyType.NEVER)

                sw.set_child(self.toolbar)

                self.vbox.append(sw)

            min_size, nat_size = self.toolbar.get_preferred_size()

            h += nat_size.height



        self.window.set_default_size(w, h)



        self._destroying = False

        self.window.connect("destroy", lambda *args: Gcf.destroy(self))

        self.window.connect({3: "delete_event", 4: "close-request"}[gtk_ver],

                            lambda *args: Gcf.destroy(self))

        if mpl.is_interactive():

            self.window.show()

            self.canvas.draw_idle()



        self.canvas.grab_focus()



    def destroy(self, *args):

        if self._destroying:

                                                                            

                                                                               

                                              

                                                                    

            return

        self._destroying = True

        self.window.destroy()

        self.canvas.destroy()



    @classmethod

    def start_main_loop(cls):

        global _application

        if _application is None:

            return



        try:

            _application.run()                                       

        except KeyboardInterrupt:

                                                                   

                                    

            context = GLib.MainContext.default()

            while context.pending():

                context.iteration(True)

            raise

        finally:

                                                                             

            _application = None



    def show(self):

                                

        self.window.show()

        self.canvas.draw()

        if mpl.rcParams["figure.raise_window"]:

            meth_name = {3: "get_window", 4: "get_surface"}[self._gtk_ver]

            if getattr(self.window, meth_name)():

                self.window.present()

            else:

                                                                    

                                                                      

                                                                            

                                            

                _api.warn_external("Cannot raise window yet to be setup")



    def full_screen_toggle(self):

        is_fullscreen = {

            3: lambda w: (w.get_window().get_state()

                          & Gdk.WindowState.FULLSCREEN),

            4: lambda w: w.is_fullscreen(),

        }[self._gtk_ver]

        if is_fullscreen(self.window):

            self.window.unfullscreen()

        else:

            self.window.fullscreen()



    def get_window_title(self):

        return self.window.get_title()



    def set_window_title(self, title):

        self.window.set_title(title)



    def resize(self, width, height):

        width = int(width / self.canvas.device_pixel_ratio)

        height = int(height / self.canvas.device_pixel_ratio)

        if self.toolbar:

            min_size, nat_size = self.toolbar.get_preferred_size()

            height += nat_size.height

        canvas_size = self.canvas.get_allocation()

        if self._gtk_ver >= 4 or canvas_size.width == canvas_size.height == 1:

                                                                         

                                                                             

                                                                             

                                                               

            self.window.set_default_size(width, height)

        else:

            self.window.resize(width, height)





class _NavigationToolbar2GTK(NavigationToolbar2):

                                                

                

                   



    def set_message(self, s):

        escaped = GLib.markup_escape_text(s)

        self.message.set_markup(f'<small>{escaped}</small>')



    def draw_rubberband(self, event, x0, y0, x1, y1):

        height = self.canvas.figure.bbox.height

        y1 = height - y1

        y0 = height - y0

        rect = [int(val) for val in (x0, y0, x1 - x0, y1 - y0)]

        self.canvas._draw_rubberband(rect)



    def remove_rubberband(self):

        self.canvas._draw_rubberband(None)



    def _update_buttons_checked(self):

        for name, active in [("Pan", "PAN"), ("Zoom", "ZOOM")]:

            button = self._gtk_ids.get(name)

            if button:

                with button.handler_block(button._signal_handler):

                    button.set_active(self.mode.name == active)



    def pan(self, *args):

        super().pan(*args)

        self._update_buttons_checked()



    def zoom(self, *args):

        super().zoom(*args)

        self._update_buttons_checked()



    def set_history_buttons(self):

        can_backward = self._nav_stack._pos > 0

        can_forward = self._nav_stack._pos < len(self._nav_stack) - 1

        if 'Back' in self._gtk_ids:

            self._gtk_ids['Back'].set_sensitive(can_backward)

        if 'Forward' in self._gtk_ids:

            self._gtk_ids['Forward'].set_sensitive(can_forward)





class RubberbandGTK(backend_tools.RubberbandBase):

    def draw_rubberband(self, x0, y0, x1, y1):

        _NavigationToolbar2GTK.draw_rubberband(

            self._make_classic_style_pseudo_toolbar(), None, x0, y0, x1, y1)



    def remove_rubberband(self):

        _NavigationToolbar2GTK.remove_rubberband(

            self._make_classic_style_pseudo_toolbar())





class ConfigureSubplotsGTK(backend_tools.ConfigureSubplotsBase):

    def trigger(self, *args):

        _NavigationToolbar2GTK.configure_subplots(self, None)





class _BackendGTK(_Backend):

    backend_version = "{}.{}.{}".format(

        Gtk.get_major_version(),

        Gtk.get_minor_version(),

        Gtk.get_micro_version(),

    )

    mainloop = _FigureManagerGTK.start_main_loop


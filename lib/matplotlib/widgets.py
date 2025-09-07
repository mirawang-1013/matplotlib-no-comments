



from contextlib import ExitStack

import copy

import itertools

from numbers import Integral, Number



from cycler import cycler

import numpy as np



import matplotlib as mpl

from . import (_api, _docstring, backend_tools, cbook, collections, colors,

               text as mtext, ticker, transforms)

from .lines import Line2D

from .patches import Rectangle, Ellipse, Polygon

from .transforms import TransformedPatchPath, Affine2D





class LockDraw:

    



    def __init__(self):

        self._owner = None



    def __call__(self, o):

        

        if not self.available(o):

            raise ValueError('already locked')

        self._owner = o



    def release(self, o):

        

        if not self.available(o):

            raise ValueError('you do not own this lock')

        self._owner = None



    def available(self, o):

        

        return not self.locked() or self.isowner(o)



    def isowner(self, o):

        

        return self._owner is o



    def locked(self):

        

        return self._owner is not None





class Widget:

    

    drawon = True

    eventson = True

    _active = True



    def set_active(self, active):

        

        self._active = active



    def get_active(self):

        

        return self._active



                                                  

    active = property(get_active, set_active, doc="Is the widget active?")



    def ignore(self, event):

        

        return not self.active





class AxesWidget(Widget):

    



    def __init__(self, ax):

        self.ax = ax

        self._cids = []



    canvas = property(

        lambda self: getattr(self.ax.get_figure(root=True), 'canvas', None)

    )



    def connect_event(self, event, callback):

        

        cid = self.canvas.mpl_connect(event, callback)

        self._cids.append(cid)



    def disconnect_events(self):

        

        for c in self._cids:

            self.canvas.mpl_disconnect(c)



    def _get_data_coords(self, event):

        

                                                                                     

                                                                                     

                                                                          

                                                                                  

                                                                                

        return ((event.xdata, event.ydata) if event.inaxes is self.ax

                else self.ax.transData.inverted().transform((event.x, event.y)))



    def ignore(self, event):

                             

        return super().ignore(event) or self.canvas is None





class Button(AxesWidget):

    



    def __init__(self, ax, label, image=None,

                 color='0.85', hovercolor='0.95', *, useblit=True):

        

        super().__init__(ax)



        if image is not None:

            ax.imshow(image)

        self.label = ax.text(0.5, 0.5, label,

                             verticalalignment='center',

                             horizontalalignment='center',

                             transform=ax.transAxes)



        self._useblit = useblit and self.canvas.supports_blit



        self._observers = cbook.CallbackRegistry(signals=["clicked"])



        self.connect_event('button_press_event', self._click)

        self.connect_event('button_release_event', self._release)

        self.connect_event('motion_notify_event', self._motion)

        ax.set_navigate(False)

        ax.set_facecolor(color)

        ax.set_xticks([])

        ax.set_yticks([])

        self.color = color

        self.hovercolor = hovercolor



    def _click(self, event):

        if not self.eventson or self.ignore(event) or not self.ax.contains(event)[0]:

            return

        if event.canvas.mouse_grabber != self.ax:

            event.canvas.grab_mouse(self.ax)



    def _release(self, event):

        if self.ignore(event) or event.canvas.mouse_grabber != self.ax:

            return

        event.canvas.release_mouse(self.ax)

        if self.eventson and self.ax.contains(event)[0]:

            self._observers.process('clicked', event)



    def _motion(self, event):

        if self.ignore(event):

            return

        c = self.hovercolor if self.ax.contains(event)[0] else self.color

        if not colors.same_color(c, self.ax.get_facecolor()):

            self.ax.set_facecolor(c)

            if self.drawon:

                if self._useblit:

                    self.ax.draw_artist(self.ax)

                    self.canvas.blit(self.ax.bbox)

                else:

                    self.canvas.draw()



    def on_clicked(self, func):

        

        return self._observers.connect('clicked', lambda event: func(event))



    def disconnect(self, cid):

        

        self._observers.disconnect(cid)





class SliderBase(AxesWidget):

    

    def __init__(self, ax, orientation, closedmin, closedmax,

                 valmin, valmax, valfmt, dragging, valstep):

        if ax.name == '3d':

            raise ValueError('Sliders cannot be added to 3D Axes')



        super().__init__(ax)

        _api.check_in_list(['horizontal', 'vertical'], orientation=orientation)



        self.orientation = orientation

        self.closedmin = closedmin

        self.closedmax = closedmax

        self.valmin = valmin

        self.valmax = valmax

        self.valstep = valstep

        self.drag_active = False

        self.valfmt = valfmt



        if orientation == "vertical":

            ax.set_ylim(valmin, valmax)

            axis = ax.yaxis

        else:

            ax.set_xlim(valmin, valmax)

            axis = ax.xaxis



        self._fmt = axis.get_major_formatter()

        if not isinstance(self._fmt, ticker.ScalarFormatter):

            self._fmt = ticker.ScalarFormatter()

            self._fmt.set_axis(axis)

        self._fmt.set_useOffset(False)                       

        self._fmt.set_useMathText(True)                                        



        ax.set_axis_off()

        ax.set_navigate(False)



        self.connect_event("button_press_event", self._update)

        self.connect_event("button_release_event", self._update)

        if dragging:

            self.connect_event("motion_notify_event", self._update)

        self._observers = cbook.CallbackRegistry(signals=["changed"])



    def _stepped_value(self, val):

        

        if isinstance(self.valstep, Number):

            val = (self.valmin

                   + round((val - self.valmin) / self.valstep) * self.valstep)

        elif self.valstep is not None:

            valstep = np.asanyarray(self.valstep)

            if valstep.ndim != 1:

                raise ValueError(

                    f"valstep must have 1 dimension but has {valstep.ndim}"

                )

            val = valstep[np.argmin(np.abs(valstep - val))]

        return val



    def disconnect(self, cid):

        

        self._observers.disconnect(cid)



    def reset(self):

        

        if np.any(self.val != self.valinit):

            self.set_val(self.valinit)





class Slider(SliderBase):

    



    def __init__(self, ax, label, valmin, valmax, *, valinit=0.5, valfmt=None,

                 closedmin=True, closedmax=True, slidermin=None,

                 slidermax=None, dragging=True, valstep=None,

                 orientation='horizontal', initcolor='r',

                 track_color='lightgrey', handle_style=None, **kwargs):

        

        super().__init__(ax, orientation, closedmin, closedmax,

                         valmin, valmax, valfmt, dragging, valstep)



        if slidermin is not None and not hasattr(slidermin, 'val'):

            raise ValueError(

                f"Argument slidermin ({type(slidermin)}) has no 'val'")

        if slidermax is not None and not hasattr(slidermax, 'val'):

            raise ValueError(

                f"Argument slidermax ({type(slidermax)}) has no 'val'")

        self.slidermin = slidermin

        self.slidermax = slidermax

        valinit = self._value_in_bounds(valinit)

        if valinit is None:

            valinit = valmin

        self.val = valinit

        self.valinit = valinit



        defaults = {'facecolor': 'white', 'edgecolor': '.75', 'size': 10}

        handle_style = {} if handle_style is None else handle_style

        marker_props = {

            f'marker{k}': v for k, v in {**defaults, **handle_style}.items()

        }



        if orientation == 'vertical':

            self.track = Rectangle(

                (.25, 0), .5, 1,

                transform=ax.transAxes,

                facecolor=track_color

            )

            ax.add_patch(self.track)

            self.poly = ax.axhspan(valmin, valinit, .25, .75, **kwargs)

                                                                       

                                             

            self.hline = ax.axhline(valinit, 0, 1, color=initcolor, lw=1,

                                    clip_path=TransformedPatchPath(self.track))

            handleXY = [[0.5], [valinit]]

        else:

            self.track = Rectangle(

                (0, .25), 1, .5,

                transform=ax.transAxes,

                facecolor=track_color

            )

            ax.add_patch(self.track)

            self.poly = ax.axvspan(valmin, valinit, .25, .75, **kwargs)

            self.vline = ax.axvline(valinit, 0, 1, color=initcolor, lw=1,

                                    clip_path=TransformedPatchPath(self.track))

            handleXY = [[valinit], [0.5]]

        self._handle, = ax.plot(

            *handleXY,

            "o",

            **marker_props,

            clip_on=False

        )



        if orientation == 'vertical':

            self.label = ax.text(0.5, 1.02, label, transform=ax.transAxes,

                                 verticalalignment='bottom',

                                 horizontalalignment='center')



            self.valtext = ax.text(0.5, -0.02, self._format(valinit),

                                   transform=ax.transAxes,

                                   verticalalignment='top',

                                   horizontalalignment='center')

        else:

            self.label = ax.text(-0.02, 0.5, label, transform=ax.transAxes,

                                 verticalalignment='center',

                                 horizontalalignment='right')



            self.valtext = ax.text(1.02, 0.5, self._format(valinit),

                                   transform=ax.transAxes,

                                   verticalalignment='center',

                                   horizontalalignment='left')



        self.set_val(valinit)



    def _value_in_bounds(self, val):

        

        val = self._stepped_value(val)



        if val <= self.valmin:

            if not self.closedmin:

                return

            val = self.valmin

        elif val >= self.valmax:

            if not self.closedmax:

                return

            val = self.valmax



        if self.slidermin is not None and val <= self.slidermin.val:

            if not self.closedmin:

                return

            val = self.slidermin.val



        if self.slidermax is not None and val >= self.slidermax.val:

            if not self.closedmax:

                return

            val = self.slidermax.val

        return val



    def _update(self, event):

        

        if self.ignore(event) or event.button != 1:

            return



        if event.name == 'button_press_event' and self.ax.contains(event)[0]:

            self.drag_active = True

            event.canvas.grab_mouse(self.ax)



        if not self.drag_active:

            return



        if (event.name == 'button_release_event'

              or event.name == 'button_press_event' and not self.ax.contains(event)[0]):

            self.drag_active = False

            event.canvas.release_mouse(self.ax)

            return



        xdata, ydata = self._get_data_coords(event)

        val = self._value_in_bounds(

            xdata if self.orientation == 'horizontal' else ydata)

        if val not in [None, self.val]:

            self.set_val(val)



    def _format(self, val):

        

        if self.valfmt is not None:

            if callable(self.valfmt):

                return self.valfmt(val)

            else:

                return self.valfmt % val

        else:

            _, s, _ = self._fmt.format_ticks([self.valmin, val, self.valmax])

                                                                           

            return s + self._fmt.get_offset()



    def set_val(self, val):

        

        if self.orientation == 'vertical':

            self.poly.set_height(val - self.poly.get_y())

            self._handle.set_ydata([val])

        else:

            self.poly.set_width(val - self.poly.get_x())

            self._handle.set_xdata([val])

        self.valtext.set_text(self._format(val))

        if self.drawon:

            self.ax.get_figure(root=True).canvas.draw_idle()

        self.val = val

        if self.eventson:

            self._observers.process('changed', val)



    def on_changed(self, func):

        

        return self._observers.connect('changed', lambda val: func(val))





class RangeSlider(SliderBase):

    



    def __init__(

        self,

        ax,

        label,

        valmin,

        valmax,

        *,

        valinit=None,

        valfmt=None,

        closedmin=True,

        closedmax=True,

        dragging=True,

        valstep=None,

        orientation="horizontal",

        track_color='lightgrey',

        handle_style=None,

        **kwargs,

    ):

        

        super().__init__(ax, orientation, closedmin, closedmax,

                         valmin, valmax, valfmt, dragging, valstep)



                                                          

        self.val = (valmin, valmax)

        if valinit is None:

                                                    

            extent = valmax - valmin

            valinit = np.array([valmin + extent * 0.25,

                                valmin + extent * 0.75])

        else:

            valinit = self._value_in_bounds(valinit)

        self.val = valinit

        self.valinit = valinit



        defaults = {'facecolor': 'white', 'edgecolor': '.75', 'size': 10}

        handle_style = {} if handle_style is None else handle_style

        marker_props = {

            f'marker{k}': v for k, v in {**defaults, **handle_style}.items()

        }



        if orientation == "vertical":

            self.track = Rectangle(

                (.25, 0), .5, 2,

                transform=ax.transAxes,

                facecolor=track_color

            )

            ax.add_patch(self.track)

            poly_transform = self.ax.get_yaxis_transform(which="grid")

            handleXY_1 = [.5, valinit[0]]

            handleXY_2 = [.5, valinit[1]]

        else:

            self.track = Rectangle(

                (0, .25), 1, .5,

                transform=ax.transAxes,

                facecolor=track_color

            )

            ax.add_patch(self.track)

            poly_transform = self.ax.get_xaxis_transform(which="grid")

            handleXY_1 = [valinit[0], .5]

            handleXY_2 = [valinit[1], .5]

        self.poly = Polygon(np.zeros([5, 2]), **kwargs)

        self._update_selection_poly(*valinit)

        self.poly.set_transform(poly_transform)

        self.poly.get_path()._interpolation_steps = 100

        self.ax.add_patch(self.poly)

        self.ax._request_autoscale_view()

        self._handles = [

            ax.plot(

                *handleXY_1,

                "o",

                **marker_props,

                clip_on=False

            )[0],

            ax.plot(

                *handleXY_2,

                "o",

                **marker_props,

                clip_on=False

            )[0]

        ]



        if orientation == "vertical":

            self.label = ax.text(

                0.5,

                1.02,

                label,

                transform=ax.transAxes,

                verticalalignment="bottom",

                horizontalalignment="center",

            )



            self.valtext = ax.text(

                0.5,

                -0.02,

                self._format(valinit),

                transform=ax.transAxes,

                verticalalignment="top",

                horizontalalignment="center",

            )

        else:

            self.label = ax.text(

                -0.02,

                0.5,

                label,

                transform=ax.transAxes,

                verticalalignment="center",

                horizontalalignment="right",

            )



            self.valtext = ax.text(

                1.02,

                0.5,

                self._format(valinit),

                transform=ax.transAxes,

                verticalalignment="center",

                horizontalalignment="left",

            )



        self._active_handle = None

        self.set_val(valinit)



    def _update_selection_poly(self, vmin, vmax):

        

                                     

                     

                     

                     

        verts = self.poly.xy

        if self.orientation == "vertical":

            verts[0] = verts[4] = .25, vmin

            verts[1] = .25, vmax

            verts[2] = .75, vmax

            verts[3] = .75, vmin

        else:

            verts[0] = verts[4] = vmin, .25

            verts[1] = vmin, .75

            verts[2] = vmax, .75

            verts[3] = vmax, .25



    def _min_in_bounds(self, min):

        

        if min <= self.valmin:

            if not self.closedmin:

                return self.val[0]

            min = self.valmin



        if min > self.val[1]:

            min = self.val[1]

        return self._stepped_value(min)



    def _max_in_bounds(self, max):

        

        if max >= self.valmax:

            if not self.closedmax:

                return self.val[1]

            max = self.valmax



        if max <= self.val[0]:

            max = self.val[0]

        return self._stepped_value(max)



    def _value_in_bounds(self, vals):

        

        return (self._min_in_bounds(vals[0]), self._max_in_bounds(vals[1]))



    def _update_val_from_pos(self, pos):

        

        idx = np.argmin(np.abs(self.val - pos))

        if idx == 0:

            val = self._min_in_bounds(pos)

            self.set_min(val)

        else:

            val = self._max_in_bounds(pos)

            self.set_max(val)

        if self._active_handle:

            if self.orientation == "vertical":

                self._active_handle.set_ydata([val])

            else:

                self._active_handle.set_xdata([val])



    def _update(self, event):

        

        if self.ignore(event) or event.button != 1:

            return



        if event.name == "button_press_event" and self.ax.contains(event)[0]:

            self.drag_active = True

            event.canvas.grab_mouse(self.ax)



        if not self.drag_active:

            return



        if (event.name == "button_release_event"

              or event.name == "button_press_event" and not self.ax.contains(event)[0]):

            self.drag_active = False

            event.canvas.release_mouse(self.ax)

            self._active_handle = None

            return



                                            

        xdata, ydata = self._get_data_coords(event)

        handle_index = np.argmin(np.abs(

            [h.get_xdata()[0] - xdata for h in self._handles]

            if self.orientation == "horizontal" else

            [h.get_ydata()[0] - ydata for h in self._handles]))

        handle = self._handles[handle_index]



                                                                           

                                                                             

        if handle is not self._active_handle:

            self._active_handle = handle



        self._update_val_from_pos(xdata if self.orientation == "horizontal" else ydata)



    def _format(self, val):

        

        if self.valfmt is not None:

            if callable(self.valfmt):

                return f"({self.valfmt(val[0])}, {self.valfmt(val[1])})"

            else:

                return f"({self.valfmt % val[0]}, {self.valfmt % val[1]})"

        else:

            _, s1, s2, _ = self._fmt.format_ticks(

                [self.valmin, *val, self.valmax]

            )

                                                                           

            s1 += self._fmt.get_offset()

            s2 += self._fmt.get_offset()

                                                                              

            return f"({s1}, {s2})"



    def set_min(self, min):

        

        self.set_val((min, self.val[1]))



    def set_max(self, max):

        

        self.set_val((self.val[0], max))



    def set_val(self, val):

        

        val = np.sort(val)

        _api.check_shape((2,), val=val)

                                                          

        self.val = (self.valmin, self.valmax)

        vmin, vmax = self._value_in_bounds(val)

        self._update_selection_poly(vmin, vmax)

        if self.orientation == "vertical":

            self._handles[0].set_ydata([vmin])

            self._handles[1].set_ydata([vmax])

        else:

            self._handles[0].set_xdata([vmin])

            self._handles[1].set_xdata([vmax])



        self.valtext.set_text(self._format((vmin, vmax)))



        if self.drawon:

            self.ax.get_figure(root=True).canvas.draw_idle()

        self.val = (vmin, vmax)

        if self.eventson:

            self._observers.process("changed", (vmin, vmax))



    def on_changed(self, func):

        

        return self._observers.connect('changed', lambda val: func(val))





def _expand_text_props(props):

    props = cbook.normalize_kwargs(props, mtext.Text)

    return cycler(**props)() if props else itertools.repeat({})





class CheckButtons(AxesWidget):

    



    def __init__(self, ax, labels, actives=None, *, useblit=True,

                 label_props=None, frame_props=None, check_props=None):

        

        super().__init__(ax)



        _api.check_isinstance((dict, None), label_props=label_props,

                              frame_props=frame_props, check_props=check_props)



        ax.set_xticks([])

        ax.set_yticks([])

        ax.set_navigate(False)



        if actives is None:

            actives = [False] * len(labels)



        self._useblit = useblit and self.canvas.supports_blit

        self._background = None



        ys = np.linspace(1, 0, len(labels)+2)[1:-1]



        label_props = _expand_text_props(label_props)

        self.labels = [

            ax.text(0.25, y, label, transform=ax.transAxes,

                    horizontalalignment="left", verticalalignment="center",

                    **props)

            for y, label, props in zip(ys, labels, label_props)]

        text_size = np.array([text.get_fontsize() for text in self.labels]) / 2



        frame_props = {

            's': text_size**2,

            'linewidth': 1,

            **cbook.normalize_kwargs(frame_props, collections.PathCollection),

            'marker': 's',

            'transform': ax.transAxes,

        }

        frame_props.setdefault('facecolor', frame_props.get('color', 'none'))

        frame_props.setdefault('edgecolor', frame_props.pop('color', 'black'))

        self._frames = ax.scatter([0.15] * len(ys), ys, **frame_props)

        check_props = {

            'linewidth': 1,

            's': text_size**2,

            **cbook.normalize_kwargs(check_props, collections.PathCollection),

            'marker': 'x',

            'transform': ax.transAxes,

            'animated': self._useblit,

        }

        check_props.setdefault('facecolor', check_props.pop('color', 'black'))

        self._checks = ax.scatter([0.15] * len(ys), ys, **check_props)

                                                                               

                                                                            

                                

        self._init_status(actives)



        self.connect_event('button_press_event', self._clicked)

        if self._useblit:

            self.connect_event('draw_event', self._clear)



        self._observers = cbook.CallbackRegistry(signals=["clicked"])



    def _clear(self, event):

        

        if self.ignore(event) or self.canvas.is_saving():

            return

        self._background = self.canvas.copy_from_bbox(self.ax.bbox)

        self.ax.draw_artist(self._checks)



    def _clicked(self, event):

        if self.ignore(event) or event.button != 1 or not self.ax.contains(event)[0]:

            return

        idxs = [                                                          

            *self._frames.contains(event)[1]["ind"],

            *[i for i, text in enumerate(self.labels) if text.contains(event)[0]]]

        if idxs:

            coords = self._frames.get_offset_transform().transform(

                self._frames.get_offsets())

            self.set_active(                                        

                idxs[(((event.x, event.y) - coords[idxs]) ** 2).sum(-1).argmin()])



    def set_label_props(self, props):

        

        _api.check_isinstance(dict, props=props)

        props = _expand_text_props(props)

        for text, prop in zip(self.labels, props):

            text.update(prop)



    def set_frame_props(self, props):

        

        _api.check_isinstance(dict, props=props)

        if 's' in props:                                         

            props['sizes'] = np.broadcast_to(props.pop('s'), len(self.labels))

        self._frames.update(props)



    def set_check_props(self, props):

        

        _api.check_isinstance(dict, props=props)

        if 's' in props:                                         

            props['sizes'] = np.broadcast_to(props.pop('s'), len(self.labels))

        actives = self.get_status()

        self._checks.update(props)

                                                                        

        self._init_status(actives)



    def set_active(self, index, state=None):

        

        if index not in range(len(self.labels)):

            raise ValueError(f'Invalid CheckButton index: {index}')

        _api.check_isinstance((bool, None), state=state)



        invisible = colors.to_rgba('none')



        facecolors = self._checks.get_facecolor()

        if state is None:

            state = colors.same_color(facecolors[index], invisible)

        facecolors[index] = self._active_check_colors[index] if state else invisible

        self._checks.set_facecolor(facecolors)



        if self.drawon:

            if self._useblit:

                if self._background is not None:

                    self.canvas.restore_region(self._background)

                self.ax.draw_artist(self._checks)

                self.canvas.blit(self.ax.bbox)

            else:

                self.canvas.draw()



        if self.eventson:

            self._observers.process('clicked', self.labels[index].get_text())



    def _init_status(self, actives):

        

        self._active_check_colors = self._checks.get_facecolor()

        if len(self._active_check_colors) == 1:

            self._active_check_colors = np.repeat(self._active_check_colors,

                                                  len(actives), axis=0)

        self._checks.set_facecolor(

            [ec if active else "none"

             for ec, active in zip(self._active_check_colors, actives)])



    def clear(self):

        



        self._checks.set_facecolor(['none'] * len(self._active_check_colors))



        if hasattr(self, '_lines'):

            for l1, l2 in self._lines:

                l1.set_visible(False)

                l2.set_visible(False)



        if self.drawon:

            self.canvas.draw()



        if self.eventson:

                                                                      

            self._observers.process('clicked', None)



    def get_status(self):

        

        return [not colors.same_color(color, colors.to_rgba("none"))

                for color in self._checks.get_facecolors()]



    def get_checked_labels(self):

        



        return [l.get_text() for l, box_checked in

                zip(self.labels, self.get_status())

                if box_checked]



    def on_clicked(self, func):

        

        return self._observers.connect('clicked', lambda text: func(text))



    def disconnect(self, cid):

        

        self._observers.disconnect(cid)





class TextBox(AxesWidget):

    



    def __init__(self, ax, label, initial='', *,

                 color='.95', hovercolor='1', label_pad=.01,

                 textalignment="left"):

        

        super().__init__(ax)



        self._text_position = _api.check_getitem(

            {"left": 0.05, "center": 0.5, "right": 0.95},

            textalignment=textalignment)



        self.label = ax.text(

            -label_pad, 0.5, label, transform=ax.transAxes,

            verticalalignment='center', horizontalalignment='right')



                                                                 

        self.text_disp = self.ax.text(

            self._text_position, 0.5, initial, transform=self.ax.transAxes,

            verticalalignment='center', horizontalalignment=textalignment,

            parse_math=False)



        self._observers = cbook.CallbackRegistry(signals=["change", "submit"])



        ax.set(

            xlim=(0, 1), ylim=(0, 1),                                         

            navigate=False, facecolor=color,

            xticks=[], yticks=[])



        self.cursor_index = 0



        self.cursor = ax.vlines(0, 0, 0, visible=False, color="k", lw=1,

                                transform=mpl.transforms.IdentityTransform())



        self.connect_event('button_press_event', self._click)

        self.connect_event('button_release_event', self._release)

        self.connect_event('motion_notify_event', self._motion)

        self.connect_event('key_press_event', self._keypress)

        self.connect_event('resize_event', self._resize)



        self.color = color

        self.hovercolor = hovercolor



        self.capturekeystrokes = False



    @property

    def text(self):

        return self.text_disp.get_text()



    def _rendercursor(self):

                                                                  

                                                                    

                                                                          

                                 



                                                                               

                                                                              

                               

        fig = self.ax.get_figure(root=True)

        if fig._get_renderer() is None:

            fig.canvas.draw()



        text = self.text_disp.get_text()                                     

        widthtext = text[:self.cursor_index]



        bb_text = self.text_disp.get_window_extent()

        self.text_disp.set_text(widthtext or ",")

        bb_widthtext = self.text_disp.get_window_extent()



        if bb_text.y0 == bb_text.y1:                                    

            bb_text.y0 -= bb_widthtext.height / 2

            bb_text.y1 += bb_widthtext.height / 2

        elif not widthtext:                    

            bb_text.x1 = bb_text.x0

        else:                                                

            bb_text.x1 = bb_text.x0 + bb_widthtext.width



        self.cursor.set(

            segments=[[(bb_text.x1, bb_text.y0), (bb_text.x1, bb_text.y1)]],

            visible=True)

        self.text_disp.set_text(text)



        fig.canvas.draw()



    def _release(self, event):

        if self.ignore(event):

            return

        if event.canvas.mouse_grabber != self.ax:

            return

        event.canvas.release_mouse(self.ax)



    def _keypress(self, event):

        if self.ignore(event):

            return

        if self.capturekeystrokes:

            key = event.key

            text = self.text

            if len(key) == 1:

                text = (text[:self.cursor_index] + key +

                        text[self.cursor_index:])

                self.cursor_index += 1

            elif key == "right":

                if self.cursor_index != len(text):

                    self.cursor_index += 1

            elif key == "left":

                if self.cursor_index != 0:

                    self.cursor_index -= 1

            elif key == "home":

                self.cursor_index = 0

            elif key == "end":

                self.cursor_index = len(text)

            elif key == "backspace":

                if self.cursor_index != 0:

                    text = (text[:self.cursor_index - 1] +

                            text[self.cursor_index:])

                    self.cursor_index -= 1

            elif key == "delete":

                if self.cursor_index != len(self.text):

                    text = (text[:self.cursor_index] +

                            text[self.cursor_index + 1:])

            self.text_disp.set_text(text)

            self._rendercursor()

            if self.eventson:

                self._observers.process('change', self.text)

                if key in ["enter", "return"]:

                    self._observers.process('submit', self.text)



    def set_val(self, val):

        newval = str(val)

        if self.text == newval:

            return

        self.text_disp.set_text(newval)

        self._rendercursor()

        if self.eventson:

            self._observers.process('change', self.text)

            self._observers.process('submit', self.text)



    def begin_typing(self):

        self.capturekeystrokes = True

                                                                             

                                                                          

                                                                

        stack = ExitStack()                                                    

        self._on_stop_typing = stack.close

        toolmanager = getattr(

            self.ax.get_figure(root=True).canvas.manager, "toolmanager", None)

        if toolmanager is not None:

                                                                            

                                     

            toolmanager.keypresslock(self)

            stack.callback(toolmanager.keypresslock.release, self)

        else:

                                                                              

                                                                        

            with _api.suppress_matplotlib_deprecation_warning():

                stack.enter_context(mpl.rc_context(

                    {k: [] for k in mpl.rcParams if k.startswith("keymap.")}))



    def stop_typing(self):

        if self.capturekeystrokes:

            self._on_stop_typing()

            self._on_stop_typing = None

            notifysubmit = True

        else:

            notifysubmit = False

        self.capturekeystrokes = False

        self.cursor.set_visible(False)

        self.ax.get_figure(root=True).canvas.draw()

        if notifysubmit and self.eventson:

                                                                             

                                                          

            self._observers.process('submit', self.text)



    def _click(self, event):

        if self.ignore(event):

            return

        if not self.ax.contains(event)[0]:

            self.stop_typing()

            return

        if not self.eventson:

            return

        if event.canvas.mouse_grabber != self.ax:

            event.canvas.grab_mouse(self.ax)

        if not self.capturekeystrokes:

            self.begin_typing()

        self.cursor_index = self.text_disp._char_index_at(event.x)

        self._rendercursor()



    def _resize(self, event):

        self.stop_typing()



    def _motion(self, event):

        if self.ignore(event):

            return

        c = self.hovercolor if self.ax.contains(event)[0] else self.color

        if not colors.same_color(c, self.ax.get_facecolor()):

            self.ax.set_facecolor(c)

            if self.drawon:

                self.ax.get_figure(root=True).canvas.draw()



    def on_text_change(self, func):

        

        return self._observers.connect('change', lambda text: func(text))



    def on_submit(self, func):

        

        return self._observers.connect('submit', lambda text: func(text))



    def disconnect(self, cid):

        

        self._observers.disconnect(cid)





class RadioButtons(AxesWidget):

    



    def __init__(self, ax, labels, active=0, activecolor=None, *,

                 useblit=True, label_props=None, radio_props=None):

        

        super().__init__(ax)



        _api.check_isinstance((dict, None), label_props=label_props,

                              radio_props=radio_props)



        radio_props = cbook.normalize_kwargs(radio_props,

                                             collections.PathCollection)

        if activecolor is not None:

            if 'facecolor' in radio_props:

                _api.warn_external(

                    'Both the *activecolor* parameter and the *facecolor* '

                    'key in the *radio_props* parameter has been specified. '

                    '*activecolor* will be ignored.')

        else:

            activecolor = 'blue'            



        self._activecolor = activecolor

        self._initial_active = active

        self.value_selected = labels[active]

        self.index_selected = active



        ax.set_xticks([])

        ax.set_yticks([])

        ax.set_navigate(False)



        ys = np.linspace(1, 0, len(labels) + 2)[1:-1]



        self._useblit = useblit and self.canvas.supports_blit

        self._background = None



        label_props = _expand_text_props(label_props)

        self.labels = [

            ax.text(0.25, y, label, transform=ax.transAxes,

                    horizontalalignment="left", verticalalignment="center",

                    **props)

            for y, label, props in zip(ys, labels, label_props)]

        text_size = np.array([text.get_fontsize() for text in self.labels]) / 2



        radio_props = {

            's': text_size**2,

            **radio_props,

            'marker': 'o',

            'transform': ax.transAxes,

            'animated': self._useblit,

        }

        radio_props.setdefault('edgecolor', radio_props.get('color', 'black'))

        radio_props.setdefault('facecolor',

                               radio_props.pop('color', activecolor))

        self._buttons = ax.scatter([.15] * len(ys), ys, **radio_props)

                                                                               

                                                                             

                       

        self._active_colors = self._buttons.get_facecolor()

        if len(self._active_colors) == 1:

            self._active_colors = np.repeat(self._active_colors, len(labels),

                                            axis=0)

        self._buttons.set_facecolor(

            [activecolor if i == active else "none"

             for i, activecolor in enumerate(self._active_colors)])



        self.connect_event('button_press_event', self._clicked)

        if self._useblit:

            self.connect_event('draw_event', self._clear)



        self._observers = cbook.CallbackRegistry(signals=["clicked"])



    def _clear(self, event):

        

        if self.ignore(event) or self.canvas.is_saving():

            return

        self._background = self.canvas.copy_from_bbox(self.ax.bbox)

        self.ax.draw_artist(self._buttons)



    def _clicked(self, event):

        if self.ignore(event) or event.button != 1 or not self.ax.contains(event)[0]:

            return

        idxs = [                                                           

            *self._buttons.contains(event)[1]["ind"],

            *[i for i, text in enumerate(self.labels) if text.contains(event)[0]]]

        if idxs:

            coords = self._buttons.get_offset_transform().transform(

                self._buttons.get_offsets())

            self.set_active(                                        

                idxs[(((event.x, event.y) - coords[idxs]) ** 2).sum(-1).argmin()])



    def set_label_props(self, props):

        

        _api.check_isinstance(dict, props=props)

        props = _expand_text_props(props)

        for text, prop in zip(self.labels, props):

            text.update(prop)



    def set_radio_props(self, props):

        

        _api.check_isinstance(dict, props=props)

        if 's' in props:                                         

            props['sizes'] = np.broadcast_to(props.pop('s'), len(self.labels))

        self._buttons.update(props)

        self._active_colors = self._buttons.get_facecolor()

        if len(self._active_colors) == 1:

            self._active_colors = np.repeat(self._active_colors,

                                            len(self.labels), axis=0)

        self._buttons.set_facecolor(

            [activecolor if text.get_text() == self.value_selected else "none"

             for text, activecolor in zip(self.labels, self._active_colors)])



    @property

    def activecolor(self):

        return self._activecolor



    @activecolor.setter

    def activecolor(self, activecolor):

        colors._check_color_like(activecolor=activecolor)

        self._activecolor = activecolor

        self.set_radio_props({'facecolor': activecolor})



    def set_active(self, index):

        

        if index not in range(len(self.labels)):

            raise ValueError(f'Invalid RadioButton index: {index}')

        self.value_selected = self.labels[index].get_text()

        self.index_selected = index

        button_facecolors = self._buttons.get_facecolor()

        button_facecolors[:] = colors.to_rgba("none")

        button_facecolors[index] = colors.to_rgba(self._active_colors[index])

        self._buttons.set_facecolor(button_facecolors)



        if self.drawon:

            if self._useblit:

                if self._background is not None:

                    self.canvas.restore_region(self._background)

                self.ax.draw_artist(self._buttons)

                self.canvas.blit(self.ax.bbox)

            else:

                self.canvas.draw()



        if self.eventson:

            self._observers.process('clicked', self.labels[index].get_text())



    def clear(self):

        

        self.set_active(self._initial_active)



    def on_clicked(self, func):

        

        return self._observers.connect('clicked', func)



    def disconnect(self, cid):

        

        self._observers.disconnect(cid)





class SubplotTool(Widget):

    



    def __init__(self, targetfig, toolfig):

        



        self.figure = toolfig

        self.targetfig = targetfig

        toolfig.subplots_adjust(left=0.2, right=0.9)

        toolfig.suptitle("Click on slider to adjust subplot param")



        self._sliders = []

        names = ["left", "bottom", "right", "top", "wspace", "hspace"]

                                                                              

        for name, ax in zip(names, toolfig.subplots(len(names) + 1)):

            ax.set_navigate(False)

            slider = Slider(ax, name, 0, 1,

                            valinit=getattr(targetfig.subplotpars, name))

            slider.on_changed(self._on_slider_changed)

            self._sliders.append(slider)

        toolfig.axes[-1].remove()

        (self.sliderleft, self.sliderbottom, self.sliderright, self.slidertop,

         self.sliderwspace, self.sliderhspace) = self._sliders

        for slider in [self.sliderleft, self.sliderbottom,

                       self.sliderwspace, self.sliderhspace]:

            slider.closedmax = False

        for slider in [self.sliderright, self.slidertop]:

            slider.closedmin = False



                     

        self.sliderleft.slidermax = self.sliderright

        self.sliderright.slidermin = self.sliderleft

        self.sliderbottom.slidermax = self.slidertop

        self.slidertop.slidermin = self.sliderbottom



        bax = toolfig.add_axes((0.8, 0.05, 0.15, 0.075))

        self.buttonreset = Button(bax, 'Reset')

        self.buttonreset.on_clicked(self._on_reset)



    def _on_slider_changed(self, _):

        self.targetfig.subplots_adjust(

            **{slider.label.get_text(): slider.val

               for slider in self._sliders})

        if self.drawon:

            self.targetfig.canvas.draw()



    def _on_reset(self, event):

        with ExitStack() as stack:

                                                                         

                                                                               

                                                                          

            stack.enter_context(cbook._setattr_cm(self, drawon=False))

            for slider in self._sliders:

                stack.enter_context(

                    cbook._setattr_cm(slider, drawon=False, eventson=False))

                                                       

            for slider in self._sliders:

                slider.reset()

        if self.drawon:

            event.canvas.draw()                                  

        self._on_slider_changed(None)                                       





class Cursor(AxesWidget):

    

    def __init__(self, ax, *, horizOn=True, vertOn=True, useblit=False,

                 **lineprops):

        super().__init__(ax)



        self.connect_event('motion_notify_event', self.onmove)

        self.connect_event('draw_event', self.clear)



        self.visible = True

        self.horizOn = horizOn

        self.vertOn = vertOn

        self.useblit = useblit and self.canvas.supports_blit



        if self.useblit:

            lineprops['animated'] = True

        self.lineh = ax.axhline(ax.get_ybound()[0], visible=False, **lineprops)

        self.linev = ax.axvline(ax.get_xbound()[0], visible=False, **lineprops)



        self.background = None

        self.needclear = False



    def clear(self, event):

        

        if self.ignore(event) or self.canvas.is_saving():

            return

        if self.useblit:

            self.background = self.canvas.copy_from_bbox(self.ax.bbox)



    def onmove(self, event):

        

        if self.ignore(event):

            return

        if not self.canvas.widgetlock.available(self):

            return

        if not self.ax.contains(event)[0]:

            self.linev.set_visible(False)

            self.lineh.set_visible(False)

            if self.needclear:

                self.canvas.draw()

                self.needclear = False

            return

        self.needclear = True

        xdata, ydata = self._get_data_coords(event)

        self.linev.set_xdata((xdata, xdata))

        self.linev.set_visible(self.visible and self.vertOn)

        self.lineh.set_ydata((ydata, ydata))

        self.lineh.set_visible(self.visible and self.horizOn)

        if not (self.visible and (self.vertOn or self.horizOn)):

            return

                 

        if self.useblit:

            if self.background is not None:

                self.canvas.restore_region(self.background)

            self.ax.draw_artist(self.linev)

            self.ax.draw_artist(self.lineh)

            self.canvas.blit(self.ax.bbox)

        else:

            self.canvas.draw_idle()





class MultiCursor(Widget):

    



    def __init__(self, canvas, axes, *, useblit=True, horizOn=False, vertOn=True,

                 **lineprops):

                                                                            

                                                                               

        self._canvas = canvas



        self.axes = axes

        self.horizOn = horizOn

        self.vertOn = vertOn



        self._canvas_infos = {

            ax.get_figure(root=True).canvas:

                {"cids": [], "background": None} for ax in axes}



        xmin, xmax = axes[-1].get_xlim()

        ymin, ymax = axes[-1].get_ylim()

        xmid = 0.5 * (xmin + xmax)

        ymid = 0.5 * (ymin + ymax)



        self.visible = True

        self.useblit = (

            useblit

            and all(canvas.supports_blit for canvas in self._canvas_infos))



        if self.useblit:

            lineprops['animated'] = True



        self.vlines = [ax.axvline(xmid, visible=False, **lineprops)

                       for ax in axes]

        self.hlines = [ax.axhline(ymid, visible=False, **lineprops)

                       for ax in axes]



        self.connect()



    def connect(self):

        

        for canvas, info in self._canvas_infos.items():

            info["cids"] = [

                canvas.mpl_connect('motion_notify_event', self.onmove),

                canvas.mpl_connect('draw_event', self.clear),

            ]



    def disconnect(self):

        

        for canvas, info in self._canvas_infos.items():

            for cid in info["cids"]:

                canvas.mpl_disconnect(cid)

            info["cids"].clear()



    def clear(self, event):

        

        if self.ignore(event):

            return

        if self.useblit:

            for canvas, info in self._canvas_infos.items():

                                                                         

                                                                              

                                                                              

                                            

                if canvas is not canvas.figure.canvas:

                    continue

                info["background"] = canvas.copy_from_bbox(canvas.figure.bbox)



    def onmove(self, event):

        axs = [ax for ax in self.axes if ax.contains(event)[0]]

        if self.ignore(event) or not axs or not event.canvas.widgetlock.available(self):

            return

        ax = cbook._topmost_artist(axs)

        xdata, ydata = ((event.xdata, event.ydata) if event.inaxes is ax

                        else ax.transData.inverted().transform((event.x, event.y)))

        for line in self.vlines:

            line.set_xdata((xdata, xdata))

            line.set_visible(self.visible and self.vertOn)

        for line in self.hlines:

            line.set_ydata((ydata, ydata))

            line.set_visible(self.visible and self.horizOn)

        if not (self.visible and (self.vertOn or self.horizOn)):

            return

                 

        if self.useblit:

            for canvas, info in self._canvas_infos.items():

                if info["background"]:

                    canvas.restore_region(info["background"])

            if self.vertOn:

                for ax, line in zip(self.axes, self.vlines):

                    ax.draw_artist(line)

            if self.horizOn:

                for ax, line in zip(self.axes, self.hlines):

                    ax.draw_artist(line)

            for canvas in self._canvas_infos:

                canvas.blit()

        else:

            for canvas in self._canvas_infos:

                canvas.draw_idle()





class _SelectorWidget(AxesWidget):



    def __init__(self, ax, onselect=None, useblit=False, button=None,

                 state_modifier_keys=None, use_data_coordinates=False):

        super().__init__(ax)



        self._visible = True

        if onselect is None:

            self.onselect = lambda *args: None

        else:

            self.onselect = onselect

        self.useblit = useblit and self.canvas.supports_blit

        self.connect_default_events()



        self._state_modifier_keys = dict(move=' ', clear='escape',

                                         square='shift', center='control',

                                         rotate='r')

        self._state_modifier_keys.update(state_modifier_keys or {})

        self._use_data_coordinates = use_data_coordinates



        self.background = None



        if isinstance(button, Integral):

            self.validButtons = [button]

        else:

            self.validButtons = button



                                                                       

        self._selection_completed = False



                                                     

        self._eventpress = None

                                                   

        self._eventrelease = None

        self._prev_event = None

        self._state = set()



    def set_active(self, active):

        super().set_active(active)

        if active:

            self.update_background(None)



    def _get_animated_artists(self):

        

        return tuple(a for ax_ in self.ax.get_figure().get_axes()

                     for a in ax_.get_children()

                     if a.get_animated() and a not in self.artists)



    def update_background(self, event):

        

                                                                             

                                                                     

        if not self.useblit:

            return

                                                                              

                                                                        

                                                                      

                                                                         

                                                                              

                                                                          

                                                     

        artists = sorted(self.artists + self._get_animated_artists(),

                         key=lambda a: a.get_zorder())

        needs_redraw = any(artist.get_visible() for artist in artists)

        with ExitStack() as stack:

            if needs_redraw:

                for artist in artists:

                    stack.enter_context(artist._cm_set(visible=False))

                self.canvas.draw()

            self.background = self.canvas.copy_from_bbox(self.ax.bbox)

        if needs_redraw:

            for artist in artists:

                self.ax.draw_artist(artist)



    def connect_default_events(self):

        

        self.connect_event('motion_notify_event', self.onmove)

        self.connect_event('button_press_event', self.press)

        self.connect_event('button_release_event', self.release)

        self.connect_event('draw_event', self.update_background)

        self.connect_event('key_press_event', self.on_key_press)

        self.connect_event('key_release_event', self.on_key_release)

        self.connect_event('scroll_event', self.on_scroll)



    def ignore(self, event):

                             

        if super().ignore(event):

            return True

        if not self.ax.get_visible():

            return True

                              

        if not self.canvas.widgetlock.available(self):

            return True

        if not hasattr(event, 'button'):

            event.button = None

                                                            

                               

        if (self.validButtons is not None

                and event.button not in self.validButtons):

            return True

                                                                                  

        if self._eventpress is None:

            return not self.ax.contains(event)[0]

                                                                           

        if event.button == self._eventpress.button:

            return False

                                                                           

        return (not self.ax.contains(event)[0] or

                event.button != self._eventpress.button)



    def update(self):

        

        if (not self.ax.get_visible() or

                self.ax.get_figure(root=True)._get_renderer() is None):

            return

        if self.useblit:

            if self.background is not None:

                self.canvas.restore_region(self.background)

            else:

                self.update_background(None)

                                                                        

                                                                             

                                                      

            artists = sorted(self.artists + self._get_animated_artists(),

                             key=lambda a: a.get_zorder())

            for artist in artists:

                self.ax.draw_artist(artist)

            self.canvas.blit(self.ax.bbox)

        else:

            self.canvas.draw_idle()



    def _get_data(self, event):

        

        if event.xdata is None:

            return None, None

        xdata, ydata = self._get_data_coords(event)

        xdata = np.clip(xdata, *self.ax.get_xbound())

        ydata = np.clip(ydata, *self.ax.get_ybound())

        return xdata, ydata



    def _clean_event(self, event):

        

        if event.xdata is None:

            event = self._prev_event

        else:

            event = copy.copy(event)

        event.xdata, event.ydata = self._get_data(event)

        self._prev_event = event

        return event



    def press(self, event):

        

        if not self.ignore(event):

            event = self._clean_event(event)

            self._eventpress = event

            self._prev_event = event

            key = event.key or ''

            key = key.replace('ctrl', 'control')

                                                       

            if key == self._state_modifier_keys['move']:

                self._state.add('move')

            self._press(event)

            return True

        return False



    def _press(self, event):

        



    def release(self, event):

        

        if not self.ignore(event) and self._eventpress:

            event = self._clean_event(event)

            self._eventrelease = event

            self._release(event)

            self._eventpress = None

            self._eventrelease = None

            self._state.discard('move')

            return True

        return False



    def _release(self, event):

        



    def onmove(self, event):

        

        if not self.ignore(event) and self._eventpress:

            event = self._clean_event(event)

            self._onmove(event)

            return True

        return False



    def _onmove(self, event):

        



    def on_scroll(self, event):

        

        if not self.ignore(event):

            self._on_scroll(event)



    def _on_scroll(self, event):

        



    def on_key_press(self, event):

        

        if self.active:

            key = event.key or ''

            key = key.replace('ctrl', 'control')

            if key == self._state_modifier_keys['clear']:

                self.clear()

                return

            for (state, modifier) in self._state_modifier_keys.items():

                if modifier in key.split('+'):

                                                                             

                                                

                    if state == 'rotate':

                        if state in self._state:

                            self._state.discard(state)

                        else:

                            self._state.add(state)

                    else:

                        self._state.add(state)

            self._on_key_press(event)



    def _on_key_press(self, event):

        



    def on_key_release(self, event):

        

        if self.active:

            key = event.key or ''

            for (state, modifier) in self._state_modifier_keys.items():

                                                                         

                                            

                if modifier in key.split('+') and state != 'rotate':

                    self._state.discard(state)

            self._on_key_release(event)



    def _on_key_release(self, event):

        



    def set_visible(self, visible):

        

        self._visible = visible

        for artist in self.artists:

            artist.set_visible(visible)



    def get_visible(self):

        

        return self._visible



    def clear(self):

        

        self._clear_without_update()

        self.update()



    def _clear_without_update(self):

        self._selection_completed = False

        self.set_visible(False)



    @property

    def artists(self):

        

        handles_artists = getattr(self, '_handles_artists', ())

        return (self._selection_artist,) + handles_artists



    def set_props(self, **props):

        

        artist = self._selection_artist

        props = cbook.normalize_kwargs(props, artist)

        artist.set(**props)

        if self.useblit:

            self.update()



    def set_handle_props(self, **handle_props):

        

        if not hasattr(self, '_handles_artists'):

            raise NotImplementedError("This selector doesn't have handles.")



        artist = self._handles_artists[0]

        handle_props = cbook.normalize_kwargs(handle_props, artist)

        for handle in self._handles_artists:

            handle.set(**handle_props)

        if self.useblit:

            self.update()

        self._handle_props.update(handle_props)



    def _validate_state(self, state):

        supported_state = [

            key for key, value in self._state_modifier_keys.items()

            if key != 'clear' and value != 'not-applicable'

            ]

        _api.check_in_list(supported_state, state=state)



    def add_state(self, state):

        

        self._validate_state(state)

        self._state.add(state)



    def remove_state(self, state):

        

        self._validate_state(state)

        self._state.remove(state)





class SpanSelector(_SelectorWidget):

    



    def __init__(self, ax, onselect, direction, *, minspan=0, useblit=False,

                 props=None, onmove_callback=None, interactive=False,

                 button=None, handle_props=None, grab_range=10,

                 state_modifier_keys=None, drag_from_anywhere=False,

                 ignore_event_outside=False, snap_values=None):



        if state_modifier_keys is None:

            state_modifier_keys = dict(clear='escape',

                                       square='not-applicable',

                                       center='not-applicable',

                                       rotate='not-applicable')

        super().__init__(ax, onselect, useblit=useblit, button=button,

                         state_modifier_keys=state_modifier_keys)



        if props is None:

            props = dict(facecolor='red', alpha=0.5)



        props['animated'] = self.useblit



        self.direction = direction

        self._extents_on_press = None

        self.snap_values = snap_values



        self.onmove_callback = onmove_callback

        self.minspan = minspan



        self.grab_range = grab_range

        self._interactive = interactive

        self._edge_handles = None

        self.drag_from_anywhere = drag_from_anywhere

        self.ignore_event_outside = ignore_event_outside



        self.new_axes(ax, _props=props, _init=True)



                       

        self._handle_props = {

            'color': props.get('facecolor', 'r'),

            **cbook.normalize_kwargs(handle_props, Line2D)}



        if self._interactive:

            self._edge_order = ['min', 'max']

            self._setup_edge_handles(self._handle_props)



        self._active_handle = None



    def new_axes(self, ax, *, _props=None, _init=False):

        

        reconnect = False

        if _init or self.canvas is not ax.get_figure(root=True).canvas:

            if self.canvas is not None:

                self.disconnect_events()

            reconnect = True

        self.ax = ax

        if reconnect:

            self.connect_default_events()



               

        self._selection_completed = False



        if self.direction == 'horizontal':

            trans = ax.get_xaxis_transform()

            w, h = 0, 1

        else:

            trans = ax.get_yaxis_transform()

            w, h = 1, 0

        rect_artist = Rectangle((0, 0), w, h, transform=trans, visible=False)

        if _props is not None:

            rect_artist.update(_props)

        elif self._selection_artist is not None:

            rect_artist.update_from(self._selection_artist)



        self.ax.add_patch(rect_artist)

        self._selection_artist = rect_artist



    def _setup_edge_handles(self, props):

                                                                               

        if self.direction == 'horizontal':

            positions = self.ax.get_xbound()

        else:

            positions = self.ax.get_ybound()

        self._edge_handles = ToolLineHandles(self.ax, positions,

                                             direction=self.direction,

                                             line_props=props,

                                             useblit=self.useblit)



    @property

    def _handles_artists(self):

        if self._edge_handles is not None:

            return self._edge_handles.artists

        else:

            return ()



    def _set_cursor(self, enabled):

        

        if enabled:

            cursor = (backend_tools.Cursors.RESIZE_HORIZONTAL

                      if self.direction == 'horizontal' else

                      backend_tools.Cursors.RESIZE_VERTICAL)

        else:

            cursor = backend_tools.Cursors.POINTER



        self.ax.get_figure(root=True).canvas.set_cursor(cursor)



    def connect_default_events(self):

                             

        super().connect_default_events()

        if getattr(self, '_interactive', False):

            self.connect_event('motion_notify_event', self._hover)



    def _press(self, event):

        

        self._set_cursor(True)

        if self._interactive and self._selection_artist.get_visible():

            self._set_active_handle(event)

        else:

            self._active_handle = None



        if self._active_handle is None or not self._interactive:

                                                                    

            self.update()



        xdata, ydata = self._get_data_coords(event)

        v = xdata if self.direction == 'horizontal' else ydata



        if self._active_handle is None and not self.ignore_event_outside:

                                                                         

                                                       

                                                            

            self._visible = False

            self._set_extents((v, v))

                                                                              

                                                   

            self._visible = True

        else:

            self.set_visible(True)



        return False



    @property

    def direction(self):

        

        return self._direction



    @direction.setter

    def direction(self, direction):

        

        _api.check_in_list(['horizontal', 'vertical'], direction=direction)

        if hasattr(self, '_direction') and direction != self._direction:

                                     

            self._selection_artist.remove()

            if self._interactive:

                self._edge_handles.remove()

            self._direction = direction

            self.new_axes(self.ax)

            if self._interactive:

                self._setup_edge_handles(self._handle_props)

        else:

            self._direction = direction



    def _release(self, event):

        

        self._set_cursor(False)



        if not self._interactive:

            self._selection_artist.set_visible(False)



        if (self._active_handle is None and self._selection_completed and

                self.ignore_event_outside):

            return



        vmin, vmax = self.extents

        span = vmax - vmin



        if span <= self.minspan:

                                                                   

            self.set_visible(False)

            if self._selection_completed:

                                                                       

                self.onselect(vmin, vmax)

            self._selection_completed = False

        else:

            self.onselect(vmin, vmax)

            self._selection_completed = True



        self.update()



        self._active_handle = None



        return False



    def _hover(self, event):

        

        if self.ignore(event):

            return



        if self._active_handle is not None or not self._selection_completed:

                                                                               

                                                 

                                                                         

                                         

            return



        _, e_dist = self._edge_handles.closest(event.x, event.y)

        self._set_cursor(e_dist <= self.grab_range)



    def _onmove(self, event):

        



        xdata, ydata = self._get_data_coords(event)

        if self.direction == 'horizontal':

            v = xdata

            vpress = self._eventpress.xdata

        else:

            v = ydata

            vpress = self._eventpress.ydata



                            

                                                                            

                                                        

        if self._active_handle == 'C' and self._extents_on_press is not None:

            vmin, vmax = self._extents_on_press

            dv = v - vpress

            vmin += dv

            vmax += dv



                                  

        elif self._active_handle and self._active_handle != 'C':

            vmin, vmax = self._extents_on_press

            if self._active_handle == 'min':

                vmin = v

            else:

                vmax = v

                   

        else:

                                                                  

                                       

            if self.ignore_event_outside and self._selection_completed:

                return

            vmin, vmax = vpress, v

            if vmin > vmax:

                vmin, vmax = vmax, vmin



        self._set_extents((vmin, vmax))



        if self.onmove_callback is not None:

            self.onmove_callback(vmin, vmax)



        return False



    def _draw_shape(self, vmin, vmax):

        if vmin > vmax:

            vmin, vmax = vmax, vmin

        if self.direction == 'horizontal':

            self._selection_artist.set_x(vmin)

            self._selection_artist.set_width(vmax - vmin)

        else:

            self._selection_artist.set_y(vmin)

            self._selection_artist.set_height(vmax - vmin)



    def _set_active_handle(self, event):

        

                                                                          

        e_idx, e_dist = self._edge_handles.closest(event.x, event.y)



                                                     

                                                                     

        if 'move' in self._state:

            self._active_handle = 'C'

        elif e_dist > self.grab_range:

                                      

            self._active_handle = None

            if self.drag_from_anywhere and self._contains(event):

                                                          

                self._active_handle = 'C'

                self._extents_on_press = self.extents

            else:

                self._active_handle = None

                return

        else:

                                       

            self._active_handle = self._edge_order[e_idx]



                                                                        

        self._extents_on_press = self.extents



    def _contains(self, event):

        

        return self._selection_artist.contains(event, radius=0)[0]



    @staticmethod

    def _snap(values, snap_values):

        

                                             

        eps = np.min(np.abs(np.diff(snap_values))) * 1e-12

        return tuple(

            snap_values[np.abs(snap_values - v + np.sign(v) * eps).argmin()]

            for v in values)



    @property

    def extents(self):

        

        if self.direction == 'horizontal':

            vmin = self._selection_artist.get_x()

            vmax = vmin + self._selection_artist.get_width()

        else:

            vmin = self._selection_artist.get_y()

            vmax = vmin + self._selection_artist.get_height()

        return vmin, vmax



    @extents.setter

    def extents(self, extents):

        self._set_extents(extents)

        self._selection_completed = True



    def _set_extents(self, extents):

                                

        if self.snap_values is not None:

            extents = tuple(self._snap(extents, self.snap_values))

        self._draw_shape(*extents)

        if self._interactive:

                                      

            self._edge_handles.set_data(self.extents)

        self.set_visible(self._visible)

        self.update()





class ToolLineHandles:

    



    def __init__(self, ax, positions, direction, *, line_props=None,

                 useblit=True):

        self.ax = ax



        _api.check_in_list(['horizontal', 'vertical'], direction=direction)

        self._direction = direction



        line_props = {

            **(line_props if line_props is not None else {}),

            'visible': False,

            'animated': useblit,

        }



        line_fun = ax.axvline if self.direction == 'horizontal' else ax.axhline



        self._artists = [line_fun(p, **line_props) for p in positions]



    @property

    def artists(self):

        return tuple(self._artists)



    @property

    def positions(self):

        

        method = 'get_xdata' if self.direction == 'horizontal' else 'get_ydata'

        return [getattr(line, method)()[0] for line in self.artists]



    @property

    def direction(self):

        

        return self._direction



    def set_data(self, positions):

        

        method = 'set_xdata' if self.direction == 'horizontal' else 'set_ydata'

        for line, p in zip(self.artists, positions):

            getattr(line, method)([p, p])



    def set_visible(self, value):

        

        for artist in self.artists:

            artist.set_visible(value)



    def set_animated(self, value):

        

        for artist in self.artists:

            artist.set_animated(value)



    def remove(self):

        

        for artist in self._artists:

            artist.remove()



    def closest(self, x, y):

        

        if self.direction == 'horizontal':

            p_pts = np.array([

                self.ax.transData.transform((p, 0))[0] for p in self.positions

                ])

            dist = abs(p_pts - x)

        else:

            p_pts = np.array([

                self.ax.transData.transform((0, p))[1] for p in self.positions

                ])

            dist = abs(p_pts - y)

        index = np.argmin(dist)

        return index, dist[index]





class ToolHandles:

    



    def __init__(self, ax, x, y, *, marker='o', marker_props=None, useblit=True):

        self.ax = ax

        props = {'marker': marker, 'markersize': 7, 'markerfacecolor': 'w',

                 'linestyle': 'none', 'alpha': 0.5, 'visible': False,

                 'label': '_nolegend_',

                 **cbook.normalize_kwargs(marker_props, Line2D._alias_map)}

        self._markers = Line2D(x, y, animated=useblit, **props)

        self.ax.add_line(self._markers)



    @property

    def x(self):

        return self._markers.get_xdata()



    @property

    def y(self):

        return self._markers.get_ydata()



    @property

    def artists(self):

        return (self._markers, )



    def set_data(self, pts, y=None):

        

        if y is not None:

            x = pts

            pts = np.array([x, y])

        self._markers.set_data(pts)



    def set_visible(self, val):

        self._markers.set_visible(val)



    def set_animated(self, val):

        self._markers.set_animated(val)



    def closest(self, x, y):

        

        pts = np.column_stack([self.x, self.y])

                                                          

        pts = self.ax.transData.transform(pts)

        diff = pts - [x, y]

        dist = np.hypot(*diff.T)

        min_index = np.argmin(dist)

        return min_index, dist[min_index]





_RECTANGLESELECTOR_PARAMETERS_DOCSTRING =
    r"""
    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        The parent Axes for the widget.

    onselect : function, optional
        A callback function that is called after a release event and the
        selection is created, changed or removed.
        It must have the signature::

            def onselect(eclick: MouseEvent, erelease: MouseEvent)

        where *eclick* and *erelease* are the mouse click and release
        `.MouseEvent`\s that start and complete the selection.

    minspanx : float, default: 0
        Selections with an x-span less than or equal to *minspanx* are removed
        (when already existing) or cancelled.

    minspany : float, default: 0
        Selections with an y-span less than or equal to *minspanx* are removed
        (when already existing) or cancelled.

    useblit : bool, default: False
        Whether to use blitting for faster drawing (if supported by the
        backend). See the tutorial :ref:`blitting`
        for details.

    props : dict, optional
        Properties with which the __ARTIST_NAME__ is drawn. See
        `.Patch` for valid properties.
        Default:

        ``dict(facecolor='red', edgecolor='black', alpha=0.2, fill=True)``

    spancoords : {"data", "pixels"}, default: "data"
        Whether to interpret *minspanx* and *minspany* in data or in pixel
        coordinates.

    button : `.MouseButton`, list of `.MouseButton`, default: all buttons
        Button(s) that trigger rectangle selection.

    grab_range : float, default: 10
        Distance in pixels within which the interactive tool handles can be
        activated.

    handle_props : dict, optional
        Properties with which the interactive handles (marker artists) are
        drawn. See the marker arguments in `.Line2D` for valid
        properties.  Default values are defined in ``mpl.rcParams`` except for
        the default value of ``markeredgecolor`` which will be the same as the
        ``edgecolor`` property in *props*.

    interactive : bool, default: False
        Whether to draw a set of handles that allow interaction with the
        widget after it is drawn.

    state_modifier_keys : dict, optional
        Keyboard modifiers which affect the widget's behavior.  Values
        amend the defaults, which are:

        - "move": Move the existing shape, default: no modifier.
        - "clear": Clear the current shape, default: "escape".
        - "square": Make the shape square, default: "shift".
        - "center": change the shape around its center, default: "ctrl".
        - "rotate": Rotate the shape around its center between -45° and 45°,
          default: "r".

        "square" and "center" can be combined. The square shape can be defined
        in data or display coordinates as determined by the
        ``use_data_coordinates`` argument specified when creating the selector.

    drag_from_anywhere : bool, default: False
        If `True`, the widget can be moved by clicking anywhere within
        its bounds.

    ignore_event_outside : bool, default: False
        If `True`, the event triggered outside the span selector will be
        ignored.

    use_data_coordinates : bool, default: False
        If `True`, the "square" shape of the selector is defined in
        data coordinates instead of display coordinates.
    """





@_docstring.Substitution(_RECTANGLESELECTOR_PARAMETERS_DOCSTRING.replace(

    '__ARTIST_NAME__', 'rectangle'))

class RectangleSelector(_SelectorWidget):

    



    def __init__(self, ax, onselect=None, *, minspanx=0,

                 minspany=0, useblit=False,

                 props=None, spancoords='data', button=None, grab_range=10,

                 handle_props=None, interactive=False,

                 state_modifier_keys=None, drag_from_anywhere=False,

                 ignore_event_outside=False, use_data_coordinates=False):

        super().__init__(ax, onselect, useblit=useblit, button=button,

                         state_modifier_keys=state_modifier_keys,

                         use_data_coordinates=use_data_coordinates)



        self._interactive = interactive

        self.drag_from_anywhere = drag_from_anywhere

        self.ignore_event_outside = ignore_event_outside

        self._rotation = 0.0

        self._aspect_ratio_correction = 1.0



                                                                            

                                                                    

                                                                            

        self._allow_creation = True



        if props is None:

            props = dict(facecolor='red', edgecolor='black',

                         alpha=0.2, fill=True)

        props = {**props, 'animated': self.useblit}

        self._visible = props.pop('visible', self._visible)

        to_draw = self._init_shape(**props)

        self.ax.add_patch(to_draw)



        self._selection_artist = to_draw

        self._set_aspect_ratio_correction()



        self.minspanx = minspanx

        self.minspany = minspany



        _api.check_in_list(['data', 'pixels'], spancoords=spancoords)

        self.spancoords = spancoords



        self.grab_range = grab_range



        if self._interactive:

            self._handle_props = {

                'markeredgecolor': (props or {}).get('edgecolor', 'black'),

                **cbook.normalize_kwargs(handle_props, Line2D)}



            self._corner_order = ['SW', 'SE', 'NE', 'NW']

            xc, yc = self.corners

            self._corner_handles = ToolHandles(self.ax, xc, yc,

                                               marker_props=self._handle_props,

                                               useblit=self.useblit)



            self._edge_order = ['W', 'S', 'E', 'N']

            xe, ye = self.edge_centers

            self._edge_handles = ToolHandles(self.ax, xe, ye, marker='s',

                                             marker_props=self._handle_props,

                                             useblit=self.useblit)



            xc, yc = self.center

            self._center_handle = ToolHandles(self.ax, [xc], [yc], marker='s',

                                              marker_props=self._handle_props,

                                              useblit=self.useblit)



            self._active_handle = None



        self._extents_on_press = None



    @property

    def _handles_artists(self):

        return (*self._center_handle.artists, *self._corner_handles.artists,

                *self._edge_handles.artists)



    def _init_shape(self, **props):

        return Rectangle((0, 0), 0, 1, visible=False,

                         rotation_point='center', **props)



    def _press(self, event):

        

                                                                                

        if self._interactive and self._selection_artist.get_visible():

            self._set_active_handle(event)

        else:

            self._active_handle = None



        if ((self._active_handle is None or not self._interactive) and

                self._allow_creation):

                                                                    

            self.update()



        if (self._active_handle is None and not self.ignore_event_outside and

                self._allow_creation):

            x, y = self._get_data_coords(event)

            self._visible = False

            self.extents = x, x, y, y

            self._visible = True

        else:

            self.set_visible(True)



        self._extents_on_press = self.extents

        self._rotation_on_press = self._rotation

        self._set_aspect_ratio_correction()



        return False



    def _release(self, event):

        

        if not self._interactive:

            self._selection_artist.set_visible(False)



        if (self._active_handle is None and self._selection_completed and

                self.ignore_event_outside):

            return



                                                                           

        x0, x1, y0, y1 = self.extents

        self._eventpress.xdata = x0

        self._eventpress.ydata = y0

        xy0 = self.ax.transData.transform([x0, y0])

        self._eventpress.x, self._eventpress.y = xy0



        self._eventrelease.xdata = x1

        self._eventrelease.ydata = y1

        xy1 = self.ax.transData.transform([x1, y1])

        self._eventrelease.x, self._eventrelease.y = xy1



                                             

        if self.spancoords == 'data':

            spanx = abs(self._eventpress.xdata - self._eventrelease.xdata)

            spany = abs(self._eventpress.ydata - self._eventrelease.ydata)

        elif self.spancoords == 'pixels':

            spanx = abs(self._eventpress.x - self._eventrelease.x)

            spany = abs(self._eventpress.y - self._eventrelease.y)

        else:

            _api.check_in_list(['data', 'pixels'],

                               spancoords=self.spancoords)

                                                                    

                                 

        if spanx <= self.minspanx or spany <= self.minspany:

            if self._selection_completed:

                                                                            

                self.onselect(self._eventpress, self._eventrelease)

            self._clear_without_update()

        else:

            self.onselect(self._eventpress, self._eventrelease)

            self._selection_completed = True



        self.update()

        self._active_handle = None

        self._extents_on_press = None



        return False



    def _onmove(self, event):

        

        eventpress = self._eventpress

                                                                          

                                                                 

        state = self._state

        rotate = 'rotate' in state and self._active_handle in self._corner_order

        move = self._active_handle == 'C'

        resize = self._active_handle and not move



        xdata, ydata = self._get_data_coords(event)

        if resize:

            inv_tr = self._get_rotation_transform().inverted()

            xdata, ydata = inv_tr.transform([xdata, ydata])

            eventpress.xdata, eventpress.ydata = inv_tr.transform(

                (eventpress.xdata, eventpress.ydata))



        dx = xdata - eventpress.xdata

        dy = ydata - eventpress.ydata

                                                                            

                                                  

        refmax = None

        if self._use_data_coordinates:

            refx, refy = dx, dy

        else:

                                              

            refx = event.x - eventpress.x

            refy = event.y - eventpress.y



        x0, x1, y0, y1 = self._extents_on_press

                                  

        if rotate:

                                 

            a = (eventpress.xdata, eventpress.ydata)

            b = self.center

            c = (xdata, ydata)

            angle = (np.arctan2(c[1]-b[1], c[0]-b[0]) -

                     np.arctan2(a[1]-b[1], a[0]-b[0]))

            self.rotation = np.rad2deg(self._rotation_on_press + angle)



        elif resize:

            size_on_press = [x1 - x0, y1 - y0]

            center = (x0 + size_on_press[0] / 2, y0 + size_on_press[1] / 2)



                                      

            if 'center' in state:

                                                       

                if 'square' in state:

                                                                      

                    if self._active_handle in self._corner_order:

                        refmax = max(refx, refy, key=abs)

                    if self._active_handle in ['E', 'W'] or refmax == refx:

                        hw = xdata - center[0]

                        hh = hw / self._aspect_ratio_correction

                    else:

                        hh = ydata - center[1]

                        hw = hh * self._aspect_ratio_correction

                else:

                    hw = size_on_press[0] / 2

                    hh = size_on_press[1] / 2

                                                               

                    if self._active_handle in ['E', 'W'] + self._corner_order:

                        hw = abs(xdata - center[0])

                    if self._active_handle in ['N', 'S'] + self._corner_order:

                        hh = abs(ydata - center[1])



                x0, x1, y0, y1 = (center[0] - hw, center[0] + hw,

                                  center[1] - hh, center[1] + hh)



            else:

                                                                         

                                                                           

                if 'W' in self._active_handle:

                    x0 = x1

                if 'S' in self._active_handle:

                    y0 = y1

                if self._active_handle in ['E', 'W'] + self._corner_order:

                    x1 = xdata

                if self._active_handle in ['N', 'S'] + self._corner_order:

                    y1 = ydata

                if 'square' in state:

                                                                      

                    if self._active_handle in self._corner_order:

                        refmax = max(refx, refy, key=abs)

                    if self._active_handle in ['E', 'W'] or refmax == refx:

                        sign = np.sign(ydata - y0)

                        y1 = y0 + sign * abs(x1 - x0) / self._aspect_ratio_correction

                    else:

                        sign = np.sign(xdata - x0)

                        x1 = x0 + sign * abs(y1 - y0) * self._aspect_ratio_correction



        elif move:

            x0, x1, y0, y1 = self._extents_on_press

            dx = xdata - eventpress.xdata

            dy = ydata - eventpress.ydata

            x0 += dx

            x1 += dx

            y0 += dy

            y1 += dy



        else:

                                

            self._rotation = 0

                                                                       

                                       

            if ((self.ignore_event_outside and self._selection_completed) or

                    not self._allow_creation):

                return

            center = [eventpress.xdata, eventpress.ydata]

            dx = (xdata - center[0]) / 2

            dy = (ydata - center[1]) / 2



                          

            if 'square' in state:

                refmax = max(refx, refy, key=abs)

                if refmax == refx:

                    dy = np.sign(dy) * abs(dx) / self._aspect_ratio_correction

                else:

                    dx = np.sign(dx) * abs(dy) * self._aspect_ratio_correction



                         

            if 'center' in state:

                dx *= 2

                dy *= 2



                         

            else:

                center[0] += dx

                center[1] += dy



            x0, x1, y0, y1 = (center[0] - dx, center[0] + dx,

                              center[1] - dy, center[1] + dy)



        self.extents = x0, x1, y0, y1



    @property

    def _rect_bbox(self):

        return self._selection_artist.get_bbox().bounds



    def _set_aspect_ratio_correction(self):

        aspect_ratio = self.ax._get_aspect_ratio()

        self._selection_artist._aspect_ratio_correction = aspect_ratio

        if self._use_data_coordinates:

            self._aspect_ratio_correction = 1

        else:

            self._aspect_ratio_correction = aspect_ratio



    def _get_rotation_transform(self):

        aspect_ratio = self.ax._get_aspect_ratio()

        return Affine2D().translate(-self.center[0], -self.center[1])
                .scale(1, aspect_ratio)
                .rotate(self._rotation)
                .scale(1, 1 / aspect_ratio)
                .translate(*self.center)



    @property

    def corners(self):

        

        x0, y0, width, height = self._rect_bbox

        xc = x0, x0 + width, x0 + width, x0

        yc = y0, y0, y0 + height, y0 + height

        transform = self._get_rotation_transform()

        coords = transform.transform(np.array([xc, yc]).T).T

        return coords[0], coords[1]



    @property

    def edge_centers(self):

        

        x0, y0, width, height = self._rect_bbox

        w = width / 2.

        h = height / 2.

        xe = x0, x0 + w, x0 + width, x0 + w

        ye = y0 + h, y0, y0 + h, y0 + height

        transform = self._get_rotation_transform()

        coords = transform.transform(np.array([xe, ye]).T).T

        return coords[0], coords[1]



    @property

    def center(self):

        

        x0, y0, width, height = self._rect_bbox

        return x0 + width / 2., y0 + height / 2.



    @property

    def extents(self):

        

        x0, y0, width, height = self._rect_bbox

        xmin, xmax = sorted([x0, x0 + width])

        ymin, ymax = sorted([y0, y0 + height])

        return xmin, xmax, ymin, ymax



    @extents.setter

    def extents(self, extents):

                                

        self._draw_shape(extents)

        if self._interactive:

                                      

            self._corner_handles.set_data(*self.corners)

            self._edge_handles.set_data(*self.edge_centers)

            x, y = self.center

            self._center_handle.set_data([x], [y])

        self.set_visible(self._visible)

        self.update()



    @property

    def rotation(self):

        

        return np.rad2deg(self._rotation)



    @rotation.setter

    def rotation(self, value):

                                                                               

                          

        if -45 <= value and value <= 45:

            self._rotation = np.deg2rad(value)

                                                                            

            self.extents = self.extents



    def _draw_shape(self, extents):

        x0, x1, y0, y1 = extents

        xmin, xmax = sorted([x0, x1])

        ymin, ymax = sorted([y0, y1])

        xlim = sorted(self.ax.get_xlim())

        ylim = sorted(self.ax.get_ylim())



        xmin = max(xlim[0], xmin)

        ymin = max(ylim[0], ymin)

        xmax = min(xmax, xlim[1])

        ymax = min(ymax, ylim[1])



        self._selection_artist.set_x(xmin)

        self._selection_artist.set_y(ymin)

        self._selection_artist.set_width(xmax - xmin)

        self._selection_artist.set_height(ymax - ymin)

        self._selection_artist.set_angle(self.rotation)



    def _set_active_handle(self, event):

        

                                                                          

        c_idx, c_dist = self._corner_handles.closest(event.x, event.y)

        e_idx, e_dist = self._edge_handles.closest(event.x, event.y)

        m_idx, m_dist = self._center_handle.closest(event.x, event.y)



        if 'move' in self._state:

            self._active_handle = 'C'

                                                                              

        elif m_dist < self.grab_range * 2:

                                                         

            self._active_handle = 'C'

        elif c_dist > self.grab_range and e_dist > self.grab_range:

                                      

            if self.drag_from_anywhere and self._contains(event):

                                                          

                self._active_handle = 'C'

            else:

                self._active_handle = None

                return

        elif c_dist < e_dist:

                                        

            self._active_handle = self._corner_order[c_idx]

        else:

                                       

            self._active_handle = self._edge_order[e_idx]



    def _contains(self, event):

        

        return self._selection_artist.contains(event, radius=0)[0]



    @property

    def geometry(self):

        

        if hasattr(self._selection_artist, 'get_verts'):

            xfm = self.ax.transData.inverted()

            y, x = xfm.transform(self._selection_artist.get_verts()).T

            return np.array([x, y])

        else:

            return np.array(self._selection_artist.get_data())





@_docstring.Substitution(_RECTANGLESELECTOR_PARAMETERS_DOCSTRING.replace(

    '__ARTIST_NAME__', 'ellipse'))

class EllipseSelector(RectangleSelector):

    

    def _init_shape(self, **props):

        return Ellipse((0, 0), 0, 1, visible=False, **props)



    def _draw_shape(self, extents):

        x0, x1, y0, y1 = extents

        xmin, xmax = sorted([x0, x1])

        ymin, ymax = sorted([y0, y1])

        center = [x0 + (x1 - x0) / 2., y0 + (y1 - y0) / 2.]

        a = (xmax - xmin) / 2.

        b = (ymax - ymin) / 2.



        self._selection_artist.center = center

        self._selection_artist.width = 2 * a

        self._selection_artist.height = 2 * b

        self._selection_artist.angle = self.rotation



    @property

    def _rect_bbox(self):

        x, y = self._selection_artist.center

        width = self._selection_artist.width

        height = self._selection_artist.height

        return x - width / 2., y - height / 2., width, height





class LassoSelector(_SelectorWidget):

    



    def __init__(self, ax, onselect=None, *, useblit=True, props=None, button=None):

        super().__init__(ax, onselect, useblit=useblit, button=button)

        self.verts = None

        props = {

            **(props if props is not None else {}),

                                                                             

                               

            'animated': self.useblit, 'visible': False,

        }

        line = Line2D([], [], **props)

        self.ax.add_line(line)

        self._selection_artist = line



    def _press(self, event):

        self.verts = [self._get_data(event)]

        self._selection_artist.set_visible(True)



    def _release(self, event):

        if self.verts is not None:

            self.verts.append(self._get_data(event))

            self.onselect(self.verts)

        self._selection_artist.set_data([[], []])

        self._selection_artist.set_visible(False)

        self.verts = None



    def _onmove(self, event):

        if self.verts is None:

            return

        self.verts.append(self._get_data(event))

        self._selection_artist.set_data(list(zip(*self.verts)))



        self.update()





class PolygonSelector(_SelectorWidget):

    



    def __init__(self, ax, onselect=None, *, useblit=False,

                 props=None, handle_props=None, grab_range=10,

                 draw_bounding_box=False, box_handle_props=None,

                 box_props=None):

                                                                            

                                                                  

                                                                            

                                                                          

                                           

        state_modifier_keys = dict(clear='escape', move_vertex='control',

                                   move_all='shift', move='not-applicable',

                                   square='not-applicable',

                                   center='not-applicable',

                                   rotate='not-applicable')

        super().__init__(ax, onselect, useblit=useblit,

                         state_modifier_keys=state_modifier_keys)



        self._xys = [(0, 0)]



        if props is None:

            props = dict(color='k', linestyle='-', linewidth=2, alpha=0.5)

        props = {**props, 'animated': self.useblit}

        self._selection_artist = line = Line2D([], [], **props)

        self.ax.add_line(line)



        if handle_props is None:

            handle_props = dict(markeredgecolor='k',

                                markerfacecolor=props.get('color', 'k'))

        self._handle_props = handle_props

        self._polygon_handles = ToolHandles(self.ax, [], [],

                                            useblit=self.useblit,

                                            marker_props=self._handle_props)



        self._active_handle_idx = -1

        self.grab_range = grab_range



        self.set_visible(True)

        self._draw_box = draw_bounding_box

        self._box = None



        if box_handle_props is None:

            box_handle_props = {}

        self._box_handle_props = self._handle_props.update(box_handle_props)

        self._box_props = box_props



    def _get_bbox(self):

        return self._selection_artist.get_bbox()



    def _add_box(self):

        self._box = RectangleSelector(self.ax,

                                      useblit=self.useblit,

                                      grab_range=self.grab_range,

                                      handle_props=self._box_handle_props,

                                      props=self._box_props,

                                      interactive=True)

        self._box._state_modifier_keys.pop('rotate')

        self._box.connect_event('motion_notify_event', self._scale_polygon)

        self._update_box()

                                                                          

                     

        self._box._allow_creation = False

        self._box._selection_completed = True

        self._draw_polygon()



    def _remove_box(self):

        if self._box is not None:

            self._box.set_visible(False)

            self._box = None



    def _update_box(self):

                                                                    

        if self._box is not None:

            bbox = self._get_bbox()

            self._box.extents = [bbox.x0, bbox.x1, bbox.y0, bbox.y1]

                         

            self._old_box_extents = self._box.extents



    def _scale_polygon(self, event):

        

        if not self._selection_completed:

            return



        if self._old_box_extents == self._box.extents:

            return



                                                  

        x1, y1, w1, h1 = self._box._rect_bbox

        old_bbox = self._get_bbox()

        t = (transforms.Affine2D()

             .translate(-old_bbox.x0, -old_bbox.y0)

             .scale(1 / old_bbox.width, 1 / old_bbox.height)

             .scale(w1, h1)

             .translate(x1, y1))



                                                                          

        new_verts = [(x, y) for x, y in t.transform(np.array(self.verts))]

        self._xys = [*new_verts, new_verts[0]]

        self._draw_polygon()

        self._old_box_extents = self._box.extents



    @property

    def _handles_artists(self):

        return self._polygon_handles.artists



    def _remove_vertex(self, i):

        

        if (len(self._xys) > 2 and

                self._selection_completed and

                i in (0, len(self._xys) - 1)):

                                                                           

                                                                   

            self._xys.pop(0)

            self._xys.pop(-1)

                                                                              

                 

            self._xys.append(self._xys[0])

        else:

            self._xys.pop(i)

        if len(self._xys) <= 2:

                                                                            

                                 

            self._selection_completed = False

            self._remove_box()



    def _press(self, event):

        

                                               

        if ((self._selection_completed or 'move_vertex' in self._state)

                and len(self._xys) > 0):

            h_idx, h_dist = self._polygon_handles.closest(event.x, event.y)

            if h_dist < self.grab_range:

                self._active_handle_idx = h_idx

                                                                             

                                                 

        self._xys_at_press = self._xys.copy()



    def _release(self, event):

        

                                     

        if self._active_handle_idx >= 0:

            if event.button == 3:

                self._remove_vertex(self._active_handle_idx)

                self._draw_polygon()

            self._active_handle_idx = -1



                               

        elif len(self._xys) > 3 and self._xys[-1] == self._xys[0]:

            self._selection_completed = True

            if self._draw_box and self._box is None:

                self._add_box()



                           

        elif (not self._selection_completed

              and 'move_all' not in self._state

              and 'move_vertex' not in self._state):

            self._xys.insert(-1, self._get_data_coords(event))



        if self._selection_completed:

            self.onselect(self.verts)



    def onmove(self, event):

        

                                                                              

                                                                              

                                                                      

                              

        if self.ignore(event):

                                                                 

            if not self.canvas.widgetlock.available(self) and self._xys:

                self._xys[-1] = (np.nan, np.nan)

                self._draw_polygon()

            return False



        else:

            event = self._clean_event(event)

            self._onmove(event)

            return True



    def _onmove(self, event):

        

                                              

        if self._active_handle_idx >= 0:

            idx = self._active_handle_idx

            self._xys[idx] = self._get_data_coords(event)

                                                                            

                                                             

            if idx == 0 and self._selection_completed:

                self._xys[-1] = self._get_data_coords(event)



                            

        elif 'move_all' in self._state and self._eventpress:

            xdata, ydata = self._get_data_coords(event)

            dx = xdata - self._eventpress.xdata

            dy = ydata - self._eventpress.ydata

            for k in range(len(self._xys)):

                x_at_press, y_at_press = self._xys_at_press[k]

                self._xys[k] = x_at_press + dx, y_at_press + dy



                                                        

        elif (self._selection_completed

              or 'move_vertex' in self._state or 'move_all' in self._state):

            return



                                  

        else:

                                                     

            x0, y0 =
                self._selection_artist.get_transform().transform(self._xys[0])

            v0_dist = np.hypot(x0 - event.x, y0 - event.y)

                                                                           

            if len(self._xys) > 3 and v0_dist < self.grab_range:

                self._xys[-1] = self._xys[0]

            else:

                self._xys[-1] = self._get_data_coords(event)



        self._draw_polygon()



    def _on_key_press(self, event):

        

                                                                    

                         

        if (not self._selection_completed

                and ('move_vertex' in self._state or

                     'move_all' in self._state)):

            self._xys.pop()

            self._draw_polygon()



    def _on_key_release(self, event):

        

                                                                     

                                                        

        if (not self._selection_completed

                and

                (event.key == self._state_modifier_keys.get('move_vertex')

                 or event.key == self._state_modifier_keys.get('move_all'))):

            self._xys.append(self._get_data_coords(event))

            self._draw_polygon()

                                                                   

        elif event.key == self._state_modifier_keys.get('clear'):

            event = self._clean_event(event)

            self._xys = [self._get_data_coords(event)]

            self._selection_completed = False

            self._remove_box()

            self.set_visible(True)



    def _draw_polygon_without_update(self):

        

        xs, ys = zip(*self._xys) if self._xys else ([], [])

        self._selection_artist.set_data(xs, ys)

        self._update_box()

                                                                              

                                                                           

                 

        if (self._selection_completed

                or (len(self._xys) > 3

                    and self._xys[-1] == self._xys[0])):

            self._polygon_handles.set_data(xs[:-1], ys[:-1])

        else:

            self._polygon_handles.set_data(xs, ys)



    def _draw_polygon(self):

        

        self._draw_polygon_without_update()

        self.update()



    @property

    def verts(self):

        

        return self._xys[:-1]



    @verts.setter

    def verts(self, xys):

        

        self._xys = [*xys, xys[0]]

        self._selection_completed = True

        self.set_visible(True)

        if self._draw_box and self._box is None:

            self._add_box()

        self._draw_polygon()



    def _clear_without_update(self):

        self._selection_completed = False

        self._xys = [(0, 0)]

        self._draw_polygon_without_update()





class Lasso(AxesWidget):

    

    def __init__(self, ax, xy, callback, *, useblit=True, props=None):

        super().__init__(ax)



        self.useblit = useblit and self.canvas.supports_blit

        if self.useblit:

            self.background = self.canvas.copy_from_bbox(self.ax.bbox)



        style = {'linestyle': '-', 'color': 'black', 'lw': 2}



        if props is not None:

            style.update(props)



        x, y = xy

        self.verts = [(x, y)]

        self.line = Line2D([x], [y], **style)

        self.ax.add_line(self.line)

        self.callback = callback

        self.connect_event('button_release_event', self.onrelease)

        self.connect_event('motion_notify_event', self.onmove)



    def onrelease(self, event):

        if self.ignore(event):

            return

        if self.verts is not None:

            self.verts.append(self._get_data_coords(event))

            if len(self.verts) > 2:

                self.callback(self.verts)

            self.line.remove()

        self.verts = None

        self.disconnect_events()



    def onmove(self, event):

        if (self.ignore(event)

                or self.verts is None

                or event.button != 1

                or not self.ax.contains(event)[0]):

            return

        self.verts.append(self._get_data_coords(event))

        self.line.set_data(list(zip(*self.verts)))



        if self.useblit:

            self.canvas.restore_region(self.background)

            self.ax.draw_artist(self.line)

            self.canvas.blit(self.ax.bbox)

        else:

            self.canvas.draw_idle()






import matplotlib.pyplot as plt

import numpy as np



from matplotlib.backend_bases import MouseEvent





class Cursor:

    

    def __init__(self, ax):

        self.ax = ax

        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')

        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')

                                           

        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)



    def set_cross_hair_visible(self, visible):

        need_redraw = self.horizontal_line.get_visible() != visible

        self.horizontal_line.set_visible(visible)

        self.vertical_line.set_visible(visible)

        self.text.set_visible(visible)

        return need_redraw



    def on_mouse_move(self, event):

        if not event.inaxes:

            need_redraw = self.set_cross_hair_visible(False)

            if need_redraw:

                self.ax.figure.canvas.draw()

        else:

            self.set_cross_hair_visible(True)

            x, y = event.xdata, event.ydata

                                       

            self.horizontal_line.set_ydata([y])

            self.vertical_line.set_xdata([x])

            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')

            self.ax.figure.canvas.draw()





x = np.arange(0, 1, 0.01)

y = np.sin(2 * 2 * np.pi * x)



fig, ax = plt.subplots()

ax.set_title('Simple cursor')

ax.plot(x, y, 'o')

cursor = Cursor(ax)

fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)



                                                             

t = ax.transData

MouseEvent(

    "motion_notify_event", ax.figure.canvas, *t.transform((0.5, 0.5))

)._process()



    

                                 

                                 

                                                                         

                                                                         

                                              

 

                                                                              

                                                                   

                                                                        

                                                                            

                   





class BlittedCursor:

    

    def __init__(self, ax):

        self.ax = ax

        self.background = None

        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')

        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')

                                           

        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)

        self._creating_background = False

        ax.figure.canvas.mpl_connect('draw_event', self.on_draw)



    def on_draw(self, event):

        self.create_new_background()



    def set_cross_hair_visible(self, visible):

        need_redraw = self.horizontal_line.get_visible() != visible

        self.horizontal_line.set_visible(visible)

        self.vertical_line.set_visible(visible)

        self.text.set_visible(visible)

        return need_redraw



    def create_new_background(self):

        if self._creating_background:

                                                               

            return

        self._creating_background = True

        self.set_cross_hair_visible(False)

        self.ax.figure.canvas.draw()

        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)

        self.set_cross_hair_visible(True)

        self._creating_background = False



    def on_mouse_move(self, event):

        if self.background is None:

            self.create_new_background()

        if not event.inaxes:

            need_redraw = self.set_cross_hair_visible(False)

            if need_redraw:

                self.ax.figure.canvas.restore_region(self.background)

                self.ax.figure.canvas.blit(self.ax.bbox)

        else:

            self.set_cross_hair_visible(True)

                                       

            x, y = event.xdata, event.ydata

            self.horizontal_line.set_ydata([y])

            self.vertical_line.set_xdata([x])

            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')



            self.ax.figure.canvas.restore_region(self.background)

            self.ax.draw_artist(self.horizontal_line)

            self.ax.draw_artist(self.vertical_line)

            self.ax.draw_artist(self.text)

            self.ax.figure.canvas.blit(self.ax.bbox)





x = np.arange(0, 1, 0.01)

y = np.sin(2 * 2 * np.pi * x)



fig, ax = plt.subplots()

ax.set_title('Blitted cursor')

ax.plot(x, y, 'o')

blitted_cursor = BlittedCursor(ax)

fig.canvas.mpl_connect('motion_notify_event', blitted_cursor.on_mouse_move)



                                                             

t = ax.transData

MouseEvent(

    "motion_notify_event", ax.figure.canvas, *t.transform((0.5, 0.5))

)._process()



    

                         

                         

                                                                           

         

 

                                                                            

                                                                          

                                                                            

                                                                              

                         





class SnappingCursor:

    

    def __init__(self, ax, line):

        self.ax = ax

        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')

        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')

        self.x, self.y = line.get_data()

        self._last_index = None

                                      

        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)



    def set_cross_hair_visible(self, visible):

        need_redraw = self.horizontal_line.get_visible() != visible

        self.horizontal_line.set_visible(visible)

        self.vertical_line.set_visible(visible)

        self.text.set_visible(visible)

        return need_redraw



    def on_mouse_move(self, event):

        if not event.inaxes:

            self._last_index = None

            need_redraw = self.set_cross_hair_visible(False)

            if need_redraw:

                self.ax.figure.canvas.draw()

        else:

            self.set_cross_hair_visible(True)

            x, y = event.xdata, event.ydata

            index = min(np.searchsorted(self.x, x), len(self.x) - 1)

            if index == self._last_index:

                return                                                

            self._last_index = index

            x = self.x[index]

            y = self.y[index]

                                       

            self.horizontal_line.set_ydata([y])

            self.vertical_line.set_xdata([x])

            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')

            self.ax.figure.canvas.draw()





x = np.arange(0, 1, 0.01)

y = np.sin(2 * 2 * np.pi * x)



fig, ax = plt.subplots()

ax.set_title('Snapping cursor')

line, = ax.plot(x, y, 'o')

snap_cursor = SnappingCursor(ax, line)

fig.canvas.mpl_connect('motion_notify_event', snap_cursor.on_mouse_move)



                                                             

t = ax.transData

MouseEvent(

    "motion_notify_event", ax.figure.canvas, *t.transform((0.5, 0.5))

)._process()



plt.show()


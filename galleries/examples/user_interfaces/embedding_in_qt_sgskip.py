



import sys

import time



import numpy as np



from matplotlib.backends.backend_qtagg import FigureCanvas

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.backends.qt_compat import QtWidgets

from matplotlib.figure import Figure





class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()

        self._main = QtWidgets.QWidget()

        self.setCentralWidget(self._main)

        layout = QtWidgets.QVBoxLayout(self._main)



        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))

                                                                        

                                                                           

                                            

        layout.addWidget(NavigationToolbar(static_canvas, self))

        layout.addWidget(static_canvas)



        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))

        layout.addWidget(dynamic_canvas)

        layout.addWidget(NavigationToolbar(dynamic_canvas, self))



        self._static_ax = static_canvas.figure.subplots()

        t = np.linspace(0, 10, 501)

        self._static_ax.plot(t, np.tan(t), ".")



        self._dynamic_ax = dynamic_canvas.figure.subplots()

                          

        self.xdata = np.linspace(0, 10, 101)

        self._update_ydata()

        self._line, = self._dynamic_ax.plot(self.xdata, self.ydata)

                                                                              

                                                                     



                                                                              

                       

        self.data_timer = dynamic_canvas.new_timer(1)

        self.data_timer.add_callback(self._update_ydata)

        self.data_timer.start()

                                                                               

                                                                               

                                                     

        self.drawing_timer = dynamic_canvas.new_timer(20)

        self.drawing_timer.add_callback(self._update_canvas)

        self.drawing_timer.start()



    def _update_ydata(self):

                                                   

        self.ydata = np.sin(self.xdata + time.time())



    def _update_canvas(self):

        self._line.set_data(self.xdata, self.ydata)

                                                                                 

                                                          

        self._line.figure.canvas.draw_idle()





if __name__ == "__main__":

                                                                             

                   

    qapp = QtWidgets.QApplication.instance()

    if not qapp:

        qapp = QtWidgets.QApplication(sys.argv)



    app = ApplicationWindow()

    app.show()

    app.activateWindow()

    app.raise_()

    qapp.exec()


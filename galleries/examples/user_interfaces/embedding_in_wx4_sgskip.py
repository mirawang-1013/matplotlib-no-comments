



import wx



import numpy as np



from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.backends.backend_wxagg import
    NavigationToolbar2WxAgg as NavigationToolbar

from matplotlib.figure import Figure





class MyNavigationToolbar(NavigationToolbar):

    



    def __init__(self, canvas):

        super().__init__(canvas)

                                                                               

        bmp = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_TOOLBAR)

        tool = self.AddTool(wx.ID_ANY, 'Click me', bmp,

                            'Activate custom control')

        self.Bind(wx.EVT_TOOL, self._on_custom, id=tool.GetId())



    def _on_custom(self, event):

                                                                              

                      

        ax = self.canvas.figure.axes[0]

        x, y = np.random.rand(2)                              

        rgb = np.random.rand(3)                           

        ax.text(x, y, 'You clicked me', transform=ax.transAxes, color=rgb)

        self.canvas.draw()

        event.Skip()





class CanvasFrame(wx.Frame):

    def __init__(self):

        super().__init__(None, -1, 'CanvasFrame', size=(550, 350))



        self.figure = Figure(figsize=(5, 4), dpi=100)

        self.axes = self.figure.add_subplot()

        t = np.arange(0.0, 3.0, 0.01)

        s = np.sin(2 * np.pi * t)



        self.axes.plot(t, s)



        self.canvas = FigureCanvas(self, -1, self.figure)



        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)



        self.toolbar = MyNavigationToolbar(self.canvas)

        self.toolbar.Realize()

                                                                         

                                                                

        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)



                                             

        self.toolbar.update()

        self.SetSizer(self.sizer)

        self.Fit()





class App(wx.App):

    def OnInit(self):

        

        frame = CanvasFrame()

        frame.Show(True)

        return True





if __name__ == "__main__":

    app = App()

    app.MainLoop()


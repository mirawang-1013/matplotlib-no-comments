



from enum import Enum

from matplotlib import _docstring





class JoinStyle(str, Enum):

    



    miter = "miter"

    round = "round"

    bevel = "bevel"



    @staticmethod

    def demo():

        

        import numpy as np

        import matplotlib.pyplot as plt



        def plot_angle(ax, x, y, angle, style):

            phi = np.radians(angle)

            xx = [x + .5, x, x + .5*np.cos(phi)]

            yy = [y, y, y + .5*np.sin(phi)]

            ax.plot(xx, yy, lw=12, color='tab:blue', solid_joinstyle=style)

            ax.plot(xx, yy, lw=1, color='black')

            ax.plot(xx[1], yy[1], 'o', color='tab:red', markersize=3)



        fig, ax = plt.subplots(figsize=(5, 4), constrained_layout=True)

        ax.set_title('Join style')

        for x, style in enumerate(['miter', 'round', 'bevel']):

            ax.text(x, 5, style)

            for y, angle in enumerate([20, 45, 60, 90, 120]):

                plot_angle(ax, x, y, angle, style)

                if x == 0:

                    ax.text(-1.3, y, f'{angle} degrees')

        ax.set_xlim(-1.5, 2.75)

        ax.set_ylim(-.5, 5.5)

        ax.set_axis_off()

        fig.show()





JoinStyle.input_description = "{"
        + ", ".join([f"'{js.name}'" for js in JoinStyle])
        + "}"





class CapStyle(str, Enum):

    

    butt = "butt"

    projecting = "projecting"

    round = "round"



    @staticmethod

    def demo():

        

        import matplotlib.pyplot as plt



        fig = plt.figure(figsize=(4, 1.2))

        ax = fig.add_axes((0, 0, 1, 0.8))

        ax.set_title('Cap style')



        for x, style in enumerate(['butt', 'round', 'projecting']):

            ax.text(x+0.25, 0.85, style, ha='center')

            xx = [x, x+0.5]

            yy = [0, 0]

            ax.plot(xx, yy, lw=12, color='tab:blue', solid_capstyle=style)

            ax.plot(xx, yy, lw=1, color='black')

            ax.plot(xx, yy, 'o', color='tab:red', markersize=3)



        ax.set_ylim(-.5, 1.5)

        ax.set_axis_off()

        fig.show()





CapStyle.input_description = "{"
        + ", ".join([f"'{cs.name}'" for cs in CapStyle])
        + "}"



_docstring.interpd.register(

    JoinStyle=JoinStyle.input_description,

    CapStyle=CapStyle.input_description,

)


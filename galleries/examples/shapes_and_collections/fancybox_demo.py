



import inspect



import matplotlib.pyplot as plt



import matplotlib.patches as mpatch

from matplotlib.patches import FancyBboxPatch

import matplotlib.transforms as mtransforms



    

            

            

                                                                             

                                                                                   

                                                                                 

          



styles = mpatch.BoxStyle.get_styles()

ncol = 2

nrow = (len(styles) + 1) // ncol

axs = (plt.figure(figsize=(3 * ncol, 1 + nrow))

       .add_gridspec(1 + nrow, ncol, wspace=.5).subplots())

for ax in axs.flat:

    ax.set_axis_off()

for ax in axs[0, :]:

    ax.text(.2, .5, "boxstyle",

            transform=ax.transAxes, size="large", color="tab:blue",

            horizontalalignment="right", verticalalignment="center")

    ax.text(.4, .5, "default parameters",

            transform=ax.transAxes,

            horizontalalignment="left", verticalalignment="center")

for ax, (stylename, stylecls) in zip(axs[1:, :].T.flat, styles.items()):

    ax.text(.2, .5, stylename, bbox=dict(boxstyle=stylename, fc="w", ec="k"),

            transform=ax.transAxes, size="large", color="tab:blue",

            horizontalalignment="right", verticalalignment="center")

    ax.text(.4, .5, str(inspect.signature(stylecls))[1:-1].replace(", ", "\n"),

            transform=ax.transAxes,

            horizontalalignment="left", verticalalignment="center")





    

                                  

                                  

                                                                         

                                                               

 

                                                                       

                                               



def add_fancy_patch_around(ax, bb, **kwargs):

    kwargs = {

        'facecolor': (1, 0.8, 1, 0.5),

        'edgecolor': (1, 0.5, 1, 0.5),

        **kwargs

    }

    fancy = FancyBboxPatch(bb.p0, bb.width, bb.height, **kwargs)

    ax.add_patch(fancy)

    return fancy





def draw_control_points_for_patches(ax):

    for patch in ax.patches:

        patch.axes.plot(*patch.get_path().vertices.T, ".",

                        c=patch.get_edgecolor())





fig, axs = plt.subplots(2, 2, figsize=(8, 8))



                                                       

bb = mtransforms.Bbox([[0.3, 0.4], [0.7, 0.6]])



ax = axs[0, 0]

                                         

add_fancy_patch_around(ax, bb, boxstyle="round,pad=0.1")

ax.set(xlim=(0, 1), ylim=(0, 1), aspect=1,

       title='boxstyle="round,pad=0.1"')



ax = axs[0, 1]

                                                               

                                            

fancy = add_fancy_patch_around(ax, bb, boxstyle="round,pad=0.1")

                                                                          

                                                                             

          

fancy.set_boxstyle("round,pad=0.1,rounding_size=0.2")

                                                             

ax.set(xlim=(0, 1), ylim=(0, 1), aspect=1,

       title='boxstyle="round,pad=0.1,rounding_size=0.2"')



ax = axs[1, 0]

                                                                            

                                                      

add_fancy_patch_around(ax, bb, boxstyle="round,pad=0.1", mutation_scale=2)

ax.set(xlim=(0, 1), ylim=(0, 1), aspect=1,

       title='boxstyle="round,pad=0.1"\n mutation_scale=2')



ax = axs[1, 1]

                                                                               

                                                                                     

                                                                          

                                                                          

add_fancy_patch_around(ax, bb, boxstyle="round,pad=0.1", mutation_aspect=0.5)

ax.set(xlim=(0, 1), ylim=(0, 1),

       title='boxstyle="round,pad=0.1"\nmutation_aspect=0.5')



for ax in axs.flat:

    draw_control_points_for_patches(ax)

                                                                

    add_fancy_patch_around(ax, bb, boxstyle="square,pad=0",

                           edgecolor="black", facecolor="none", zorder=10)



fig.tight_layout()





plt.show()



    

                                                             

                                                             

                                                                     

                                                              

                       

                                                                

                                                                

                                     



fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 5))



                

bb = mtransforms.Bbox([[-0.5, -0.5], [0.5, 0.5]])

add_fancy_patch_around(ax1, bb, boxstyle="square,pad=0",

                       edgecolor="black", facecolor="none", zorder=10)

add_fancy_patch_around(ax2, bb, boxstyle="square,pad=0",

                       edgecolor="black", facecolor="none", zorder=10)

ax1.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5), aspect=2)

ax2.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5), aspect=2)





fancy = add_fancy_patch_around(

    ax1, bb, boxstyle="round,pad=0.5")

ax1.set_title("aspect=2\nmutation_aspect=1")



fancy = add_fancy_patch_around(

    ax2, bb, boxstyle="round,pad=0.5", mutation_aspect=0.5)

ax2.set_title("aspect=2\nmutation_aspect=0.5")





    

 

                            

 

                                                                              

                     

 

                           

                                          

                                    

                                                 

                                   

                                      

                                  


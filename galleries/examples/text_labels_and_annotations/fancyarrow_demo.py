



import inspect

import itertools

import re



import matplotlib.pyplot as plt



from matplotlib.patches import ArrowStyle



styles = ArrowStyle.get_styles()

ncol = 2

nrow = (len(styles) + 1) // ncol

gridspec_kw = dict(wspace=0, hspace=0.05, left=0, right=1, bottom=0, top=1)

fig, axs = plt.subplots(1 + nrow, ncol,

                        figsize=(4 * ncol, 1 + nrow), gridspec_kw=gridspec_kw)

for ax in axs.flat:

    ax.set_xlim(-0.1, 4)

    ax.set_axis_off()

for ax in axs[0, :]:

    ax.text(0, 0.5, "arrowstyle", size="large", color="tab:blue")

    ax.text(1.4, .5, "default parameters", size="large")

for ax, (stylename, stylecls) in zip(axs[1:, :].T.flat, styles.items()):

                                             

    l, = ax.plot(1.25, 0, "o", color="darkgrey")

    ax.annotate(stylename, (1.25, 0), (0, 0),

                size="large", color="tab:blue", va="center", family="monospace",

                arrowprops=dict(

                    arrowstyle=stylename, connectionstyle="arc3,rad=0",

                    color="black", shrinkA=5, shrinkB=5, patchB=l,

                ),

                bbox=dict(boxstyle="square", fc="w", ec="darkgrey"))

                             

                                                                    

    s = str(inspect.signature(stylecls))[1:-1]

    n = 2 if s.count(',') > 3 else 1

    ax.text(1.4, 0,

            re.sub(', ', lambda m, c=itertools.count(1): m.group()

                   if next(c) % n else '\n', s),

            verticalalignment="center", color="0.3")



plt.show()



    

 

                            

 

                                                                              

                     

 

                           

                                      

                                                   

                                      


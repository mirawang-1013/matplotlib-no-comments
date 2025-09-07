



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.patches import Rectangle



fig, ax = plt.subplots(figsize=(6.5, 1.65), layout='constrained')

ax.add_patch(Rectangle((-0.2, -0.35), 11.2, 0.7, color='C1', alpha=0.8))

for i, alpha in enumerate(np.linspace(0, 1, 11)):

    ax.add_patch(Rectangle((i, 0.05), 0.8, 0.6, alpha=alpha, zorder=0))

    ax.text(i+0.4, 0.85, f"{alpha:.1f}", ha='center')

    ax.add_patch(Rectangle((i, -0.05), 0.8, -0.6, alpha=alpha, zorder=2))

ax.set_xlim(-0.2, 13)

ax.set_ylim(-1, 1)

ax.set_title('alpha values')

ax.text(11.3, 0.6, 'zorder=1', va='center', color='C0')

ax.text(11.3, 0, 'zorder=2\nalpha=0.8', va='center', color='C1')

ax.text(11.3, -0.6, 'zorder=3', va='center', color='C0')

ax.axis('off')





    

 

                                                                              

                                                                            

                              

 

                                                                               

 

 

                      

                      

 

                                                                   

                                                

                                                            





import matplotlib.pyplot as plt

import numpy as np



import matplotlib as mpl



th = np.linspace(0, 2*np.pi, 128)





def demo(sty):

    mpl.style.use(sty)

    fig, ax = plt.subplots(figsize=(3, 3))



    ax.set_title(f'style: {sty!r}', color='C0')



    ax.plot(th, np.cos(th), 'C1', label='C1')

    ax.plot(th, np.sin(th), 'C2', label='C2')

    ax.legend()





demo('default')

demo('seaborn-v0_8')



    

                                                                            

                                                                               

               

 

                  

 

                                             

                                             

 

                                                                         

                                                              

 

                                                                              

                                                                         

                                                                   

 

                                                                               

                                                                        

                     

 

                                                                              

              



import matplotlib.colors as mcolors

import matplotlib.patches as mpatch



overlap = {name for name in mcolors.CSS4_COLORS

           if f'xkcd:{name}' in mcolors.XKCD_COLORS}



fig = plt.figure(figsize=[9, 5])

ax = fig.add_axes((0, 0, 1, 1))



n_groups = 3

n_rows = len(overlap) // n_groups + 1



for j, color_name in enumerate(sorted(overlap)):

    css4 = mcolors.CSS4_COLORS[color_name]

    xkcd = mcolors.XKCD_COLORS[f'xkcd:{color_name}'].upper()



                                                    

    rgba = mcolors.to_rgba_array([css4, xkcd])

    luma = 0.299 * rgba[:, 0] + 0.587 * rgba[:, 1] + 0.114 * rgba[:, 2]

    css4_text_color = 'k' if luma[0] > 0.5 else 'w'

    xkcd_text_color = 'k' if luma[1] > 0.5 else 'w'



    col_shift = (j // n_rows) * 3

    y_pos = j % n_rows

    text_args = dict(fontsize=10, weight='bold' if css4 == xkcd else None)

    ax.add_patch(mpatch.Rectangle((0 + col_shift, y_pos), 1, 1, color=css4))

    ax.add_patch(mpatch.Rectangle((1 + col_shift, y_pos), 1, 1, color=xkcd))

    ax.text(0.5 + col_shift, y_pos + .7, css4,

            color=css4_text_color, ha='center', **text_args)

    ax.text(1.5 + col_shift, y_pos + .7, xkcd,

            color=xkcd_text_color, ha='center', **text_args)

    ax.text(2 + col_shift, y_pos + .7, f'  {color_name}', **text_args)



for g in range(n_groups):

    ax.hlines(range(n_rows), 3*g, 3*g + 2.8, color='0.7', linewidth=1)

    ax.text(0.5 + 3*g, -0.3, 'X11/CSS4', ha='center')

    ax.text(1.5 + 3*g, -0.3, 'xkcd', ha='center')



ax.set_xlim(0, 3 * n_groups)

ax.set_ylim(n_rows, -1)

ax.axis('off')



plt.show()


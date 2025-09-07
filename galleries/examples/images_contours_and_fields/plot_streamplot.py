

import time



import matplotlib.pyplot as plt

import numpy as np



w = 3

Y, X = np.mgrid[-w:w:100j, -w:w:100j]

U = -1 - X**2 + Y

V = 1 + X - Y**2

speed = np.sqrt(U**2 + V**2)



fig, axs = plt.subplots(4, 2, figsize=(7, 12), height_ratios=[1, 1, 1, 2])

axs = axs.flat



                                     

axs[0].streamplot(X, Y, U, V, density=[0.5, 1])

axs[0].set_title('Varying Density')



                                  

strm = axs[1].streamplot(X, Y, U, V, color=U, linewidth=2, cmap='autumn')

fig.colorbar(strm.lines)

axs[1].set_title('Varying Color')



                                        

lw = 5*speed / speed.max()

axs[2].streamplot(X, Y, U, V, density=0.6, color='k', linewidth=lw, num_arrows=5)

axs[2].set_title('Varying Line Width')



                                                    

seed_points = np.array([[-2, -1, 0, 1, 2, -1], [-2, -1,  0, 1, 2, 2]])



strm = axs[3].streamplot(X, Y, U, V, color=U, linewidth=2,

                         cmap='autumn', start_points=seed_points.T)

fig.colorbar(strm.lines)

axs[3].set_title('Controlling Starting Points')



                                                   

axs[3].plot(seed_points[0], seed_points[1], 'bo')

axs[3].set(xlim=(-w, w), ylim=(-w, w))



                                               

axs[4].streamplot(X, Y, U, V, num_arrows=3)

axs[4].set_title('Multiple arrows')



axs[5].axis("off")



               

mask = np.zeros(U.shape, dtype=bool)

mask[40:60, 40:60] = True

U[:20, :20] = np.nan

U = np.ma.array(U, mask=mask)



axs[6].streamplot(X, Y, U, V, color='r')

axs[6].set_title('Streamplot with Masking')



axs[6].imshow(~mask, extent=(-w, w, -w, w), alpha=0.5, cmap='gray',

              aspect='auto')

axs[6].set_aspect('equal')



axs[7].streamplot(X, Y, U, V, broken_streamlines=False)

axs[7].set_title('Streamplot with unbroken streamlines')



plt.tight_layout()

            



    

                        

                        

 

                                                                             

                                                                            

                                                                                 

                                                                                 

                                                                              

          

 

                                                                              

                                                                              

                                                                        

                                                    



                                               

n = 50

x, y = np.meshgrid(np.linspace(-2, 2, n), np.linspace(-3, 3, n))

th = np.arctan2(y, x)

r = np.sqrt(x**2 + y**2)

vr = -np.cos(th) / r**2

vt = -np.sin(th) / r**2 - 1 / r

vx = vr * np.cos(th) - vt * np.sin(th) + 1.0

vy = vr * np.sin(th) + vt * np.cos(th)



             

n_seed = 50

seed_pts = np.column_stack((np.full(n_seed, -1.75), np.linspace(-2, 2, n_seed)))



_, axs = plt.subplots(3, 1, figsize=(6, 14))

th_circ = np.linspace(0, 2 * np.pi, 100)

for ax, max_val in zip(axs, [0.05, 1, 5]):

    ax_ins = ax.inset_axes([0.0, 0.7, 0.3, 0.35])

    for ax_curr, is_inset in zip([ax, ax_ins], [False, True]):

        t_start = time.time()

        ax_curr.streamplot(

            x,

            y,

            vx,

            vy,

            start_points=seed_pts,

            broken_streamlines=False,

            arrowsize=1e-10,

            linewidth=2 if is_inset else 0.6,

            color="k",

            integration_max_step_scale=max_val,

            integration_max_error_scale=max_val,

        )

        if is_inset:

            t_total = time.time() - t_start



                           

        ax_curr.fill(

            np.cos(th_circ),

            np.sin(th_circ),

            color="w",

            ec="k",

            lw=6 if is_inset else 2,

        )



                             

        ax_curr.set_aspect("equal")



                                     

    text = f"integration_max_step_scale: {max_val}\n"
        f"integration_max_error_scale: {max_val}\n"
        f"streamplot time: {t_total:.2f} sec"

    if max_val == 1:

        text += "\n(default)"

    ax.text(0.0, 0.0, text, ha="center", va="center")



                                            

    ax_ins.set_xlim(-1.2, -0.7)

    ax_ins.set_ylim(-0.8, -0.4)

    ax_ins.set_yticks(())

    ax_ins.set_xticks(())



    ax.set_ylim(-1.5, 1.5)

    ax.axis("off")

    ax.indicate_inset_zoom(ax_ins, ec="k")



plt.tight_layout()

plt.show()

    

 

                            

 

                                                                              

                     

 

                                                                         

                                     


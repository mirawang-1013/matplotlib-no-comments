





    

 

                              

                              

 

                                                                        

                                                                             

                                                                

                                                   

                                                              

                                                

                                                           

                                                     

                                                        

                                                                 

                                                                             

                                                                             

                                                  





import matplotlib.pyplot as plt

import numpy as np



import matplotlib

import matplotlib as mpl



                                     



vegetables = ["cucumber", "tomato", "lettuce", "asparagus",

              "potato", "wheat", "barley"]

farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",

           "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]



harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],

                    [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],

                    [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],

                    [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],

                    [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],

                    [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],

                    [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])





fig, ax = plt.subplots()

im = ax.imshow(harvest)



                                                                

ax.set_xticks(range(len(farmers)), labels=farmers,

              rotation=45, rotation_mode="xtick")

ax.set_yticks(range(len(vegetables)), labels=vegetables)



                                                        

for i in range(len(vegetables)):

    for j in range(len(farmers)):

        text = ax.text(j, i, harvest[i, j],

                       ha="center", va="center", color="w")



ax.set_title("Harvest of local farmers (in tons/year)")

fig.tight_layout()

plt.show()





    

                                      

                                      

 

                                                          

                                                                  

                                                    

                                                                           

                                                                 

 

                                                                      

                                                               

                                                                     

                                              

                                                             

                                              





def heatmap(data, row_labels, col_labels, ax=None,

            cbar_kw=None, cbarlabel="", **kwargs):

    



    if ax is None:

        ax = plt.gca()



    if cbar_kw is None:

        cbar_kw = {}



                      

    im = ax.imshow(data, **kwargs)



                     

    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)

    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")



                                                                     

    ax.set_xticks(range(data.shape[1]), labels=col_labels,

                  rotation=-30, rotation_mode="xtick")

    ax.set_yticks(range(data.shape[0]), labels=row_labels)



                                                     

    ax.tick_params(top=True, bottom=False,

                   labeltop=True, labelbottom=False)



                                            

    ax.spines[:].set_visible(False)



    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)

    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)

    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)

    ax.tick_params(which="minor", bottom=False, left=False)



    return im, cbar





def annotate_heatmap(im, data=None, valfmt="{x:.2f}",

                     textcolors=("black", "white"),

                     threshold=None, **textkw):

    



    if not isinstance(data, (list, np.ndarray)):

        data = im.get_array()



                                                        

    if threshold is not None:

        threshold = im.norm(threshold)

    else:

        threshold = im.norm(data.max())/2.



                                                         

                            

    kw = dict(horizontalalignment="center",

              verticalalignment="center")

    kw.update(textkw)



                                                    

    if isinstance(valfmt, str):

        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)



                                                              

                                                    

    texts = []

    for i in range(data.shape[0]):

        for j in range(data.shape[1]):

            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])

            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)

            texts.append(text)



    return texts





    

                                                                          

 



fig, ax = plt.subplots()



im, cbar = heatmap(harvest, vegetables, farmers, ax=ax,

                   cmap="YlGn", cbarlabel="harvest [t/year]")

texts = annotate_heatmap(im, valfmt="{x:.1f} t")



fig.tight_layout()

plt.show()





    

                                    

                                    

 

                                                                    

                                                                            

 



np.random.seed(19680801)



fig, ((ax, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 6))



                                                                      



im, _ = heatmap(harvest, vegetables, farmers, ax=ax,

                cmap="Wistia", cbarlabel="harvest [t/year]")

annotate_heatmap(im, valfmt="{x:.1f}", size=7)



                                                                

                                                                   



data = np.random.randint(2, 100, size=(7, 7))

y = [f"Book {i}" for i in range(1, 8)]

x = [f"Store {i}" for i in list("ABCDEFG")]

im, _ = heatmap(data, y, x, ax=ax2, vmin=0,

                cmap="magma_r", cbarlabel="weekly sold copies")

annotate_heatmap(im, valfmt="{x:d}", size=7, threshold=20,

                 textcolors=("red", "white"))



                                                              

                                                               

                                                                 

                                  



data = np.random.randn(6, 6)

y = [f"Prod. {i}" for i in range(10, 70, 10)]

x = [f"Cycle {i}" for i in range(1, 7)]



qrates = list("ABCDEFG")

norm = matplotlib.colors.BoundaryNorm(np.linspace(-3.5, 3.5, 8), 7)

fmt = matplotlib.ticker.FuncFormatter(lambda x, pos: qrates[::-1][norm(x)])



im, _ = heatmap(data, y, x, ax=ax3,

                cmap=mpl.colormaps["PiYG"].resampled(7), norm=norm,

                cbar_kw=dict(ticks=np.arange(-3, 4), format=fmt),

                cbarlabel="Quality Rating")



annotate_heatmap(im, valfmt=fmt, size=9, fontweight="bold", threshold=-1,

                 textcolors=("red", "black"))



                                                                           

                                                                          

                                                    

                                    



corr_matrix = np.corrcoef(harvest)

im, _ = heatmap(corr_matrix, vegetables, vegetables, ax=ax4,

                cmap="PuOr", vmin=-1, vmax=1,

                cbarlabel="correlation coeff.")





def func(x, pos):

    return f"{x:.2f}".replace("0.", ".").replace("1.00", "")



annotate_heatmap(im, valfmt=matplotlib.ticker.FuncFormatter(func), size=7)





plt.tight_layout()

plt.show()





    

 

                            

 

                                                                              

                     

 

                                                                 

                                                                         


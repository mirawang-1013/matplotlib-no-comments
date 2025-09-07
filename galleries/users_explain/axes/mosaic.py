

import matplotlib.pyplot as plt

import numpy as np





                                                                  

def identify_axes(ax_dict, fontsize=48):

    

    kw = dict(ha="center", va="center", fontsize=fontsize, color="darkgrey")

    for k, ax in ax_dict.items():

        ax.text(0.5, 0.5, k, transform=ax.transAxes, **kw)





    

                                                                              

                                                             

np.random.seed(19680801)

hist_data = np.random.randn(1_500)





fig = plt.figure(layout="constrained")

ax_array = fig.subplots(2, 2, squeeze=False)



ax_array[0, 0].bar(["a", "b", "c"], [5, 7, 9])

ax_array[0, 1].plot([1, 2, 3])

ax_array[1, 0].hist(hist_data, bins="auto")

ax_array[1, 1].imshow([[1, 2], [2, 1]])



identify_axes(

    {(j, k): a for j, r in enumerate(ax_array) for k, a in enumerate(r)},

)



    

                                                                            

                     



fig = plt.figure(layout="constrained")

ax_dict = fig.subplot_mosaic(

    [

        ["bar", "plot"],

        ["hist", "image"],

    ],

)

ax_dict["bar"].bar(["a", "b", "c"], [5, 7, 9])

ax_dict["plot"].plot([1, 2, 3])

ax_dict["hist"].hist(hist_data)

ax_dict["image"].imshow([[1, 2], [2, 1]])

identify_axes(ax_dict)



    

                                                 

                                                                

                                                                    

                                                          



print(ax_dict)





    

                   

                   

 

                                                            

                                                        





mosaic = """
    AB
    CD
    """



    

                                                                   

                                                                

                                                           



fig = plt.figure(layout="constrained")

ax_dict = fig.subplot_mosaic(mosaic)

identify_axes(ax_dict)



    

                                                             

mosaic = "AB;CD"



    

                                                               

                                          



fig = plt.figure(layout="constrained")

ax_dict = fig.subplot_mosaic(mosaic)

identify_axes(ax_dict)



    

                                     

                                     

 

                                                                   

                                                                    

                          





    

                                                                        

                                                                            



axd = plt.figure(layout="constrained").subplot_mosaic(

    """
    ABD
    CCD
    """

)

identify_axes(axd)



    

                                                                      

                                                    





axd = plt.figure(layout="constrained").subplot_mosaic(

    """
    A.C
    BBB
    .D.
    """

)

identify_axes(axd)





    

                                                                      

                                                                     

                   



axd = plt.figure(layout="constrained").subplot_mosaic(

    """
    aX
    Xb
    """,

    empty_sentinel="X",

)

identify_axes(axd)





    

 

                                                                    

                              



axd = plt.figure(layout="constrained").subplot_mosaic(

    """αб
       ℝ☢"""

)

identify_axes(axd)



    

                                                                  

                                                                     

                             

 

                             

                             

 

                                                                  

                                                                  

                                   

 

                                                                   

                                                                      

                                                                              

                                            





axd = plt.figure(layout="constrained").subplot_mosaic(

    """
    .a.
    bAc
    .d.
    """,

                                            

    height_ratios=[1, 3.5, 1],

                                              

    width_ratios=[1, 3.5, 1],

)

identify_axes(axd)



    

                                                                           

                                                                          

                                                                  

                     



mosaic = """AA
            BC"""

fig = plt.figure()

axd = fig.subplot_mosaic(

    mosaic,

    gridspec_kw={

        "bottom": 0.25,

        "top": 0.95,

        "left": 0.1,

        "right": 0.5,

        "wspace": 0.5,

        "hspace": 0.5,

    },

)

identify_axes(axd)



axd = fig.subplot_mosaic(

    mosaic,

    gridspec_kw={

        "bottom": 0.05,

        "top": 0.75,

        "left": 0.6,

        "right": 0.95,

        "wspace": 0.5,

        "hspace": 0.5,

    },

)

identify_axes(axd)



    

                                                          



mosaic = """AA
            BC"""

fig = plt.figure(layout="constrained")

left, right = fig.subfigures(nrows=1, ncols=2)

axd = left.subplot_mosaic(mosaic)

identify_axes(axd)



axd = right.subplot_mosaic(mosaic)

identify_axes(axd)





    

                              

                              

 

                                                                

                                                                 

                      





axd = plt.figure(layout="constrained").subplot_mosaic(

    "AB", subplot_kw={"projection": "polar"}

)

identify_axes(axd)



    

                                    

                                    

 

                                                                               

                                                                     

                                                                       

 

                       

 





fig, axd = plt.subplot_mosaic(

    "AB;CD",

    per_subplot_kw={

        "A": {"projection": "polar"},

        ("C", "D"): {"xscale": "log"}

    },

)

identify_axes(axd)



    

                                                                         

                                                                          

                                                                   

              





fig, axd = plt.subplot_mosaic(

    "AB;CD",

    per_subplot_kw={

        "AD": {"projection": "polar"},

        "BC": {"facecolor": ".9"}

    },

)

identify_axes(axd)



    

                                                                       

                                               





axd = plt.figure(layout="constrained").subplot_mosaic(

    "AB;CD",

    subplot_kw={"facecolor": "xkcd:tangerine"},

    per_subplot_kw={

        "B": {"facecolor": "xkcd:water blue"},

        "D": {"projection": "polar", "facecolor": "w"},

    }

)

identify_axes(axd)





    

                   

                   

 

                                                                    

                                                                           

                                                            



axd = plt.figure(layout="constrained").subplot_mosaic(

    [

        ["main", "zoom"],

        ["main", "BLANK"],

    ],

    empty_sentinel="BLANK",

    width_ratios=[2, 1],

)

identify_axes(axd)





    

                                                                               

                                                       



inner = [

    ["inner A"],

    ["inner B"],

]



outer_nested_mosaic = [

    ["main", inner],

    ["bottom", "bottom"],

]

axd = plt.figure(layout="constrained").subplot_mosaic(

    outer_nested_mosaic, empty_sentinel=None

)

identify_axes(axd, fontsize=36)





    

                                                        

mosaic = np.zeros((4, 4), dtype=int)

for j in range(4):

    mosaic[j, j] = j + 1

axd = plt.figure(layout="constrained").subplot_mosaic(

    mosaic,

    empty_sentinel=0,

)

identify_axes(axd)






import matplotlib.pyplot as plt



plt.rcParams["font.size"] = 20

ax = plt.figure().add_subplot(xticks=[], yticks=[])



                                      

text = ax.text(.1, .5, "Matplotlib", color="red")

                                                                              

text = ax.annotate(

    " says,", xycoords=text, xy=(1, 0), verticalalignment="bottom",

    color="gold", weight="bold")                     

text = ax.annotate(

    " hello", xycoords=text, xy=(1, 0), verticalalignment="bottom",

    color="green", style="italic")                     

text = ax.annotate(

    " world!", xycoords=text, xy=(1, 0), verticalalignment="bottom",

    color="blue", family="serif")                     



plt.show()


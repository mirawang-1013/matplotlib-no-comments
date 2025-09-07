



import matplotlib.pyplot as plt



plt.subplot(311)

plt.plot([1, 2, 3])



                                                               

plt.rcParams.update({

    "font.weight": "bold",

    "xtick.major.size": 5,

    "xtick.major.pad": 7,

    "xtick.labelsize": 15,

    "grid.color": "0.5",

    "grid.linestyle": "-",

    "grid.linewidth": 5,

    "lines.linewidth": 2,

    "lines.color": "g",

})

plt.subplot(312)

plt.plot([1, 2, 3])

plt.grid(True)



plt.rcdefaults()

plt.subplot(313)

plt.plot([1, 2, 3])

plt.grid(True)

plt.show()


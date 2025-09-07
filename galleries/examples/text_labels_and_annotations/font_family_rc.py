

import matplotlib.pyplot as plt



print(plt.rcParams["font.sans-serif"][0])

print(plt.rcParams["font.monospace"][0])





    

                                



def print_text(text):

    fig, ax = plt.subplots(figsize=(6, 1), facecolor="#eefade")

    ax.text(0.5, 0.5, text, ha='center', va='center', size=40)

    ax.axis("off")

    plt.show()





plt.rcParams["font.family"] = "sans-serif"

print_text("Hello World! 01")





    

                                                           



plt.rcParams["font.family"] = "sans-serif"

plt.rcParams["font.sans-serif"] = ["Nimbus Sans"]

print_text("Hello World! 02")





    

                               



plt.rcParams["font.family"] = "monospace"

print_text("Hello World! 03")





    

                                                       



plt.rcParams["font.family"] = "monospace"

plt.rcParams["font.monospace"] = ["FreeMono"]

print_text("Hello World! 04")


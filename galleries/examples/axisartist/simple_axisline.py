



import matplotlib.pyplot as plt



from mpl_toolkits.axisartist.axislines import AxesZero



fig = plt.figure()

fig.subplots_adjust(right=0.85)

ax = fig.add_subplot(axes_class=AxesZero)



                                   

ax.axis["right"].set_visible(False)

ax.axis["top"].set_visible(False)



                                                             

ax.axis["xzero"].set_visible(True)

ax.axis["xzero"].label.set_text("Axis Zero")



ax.set_ylim(-2, 4)

ax.set_xlabel("Label X")

ax.set_ylabel("Label Y")

     

                                             

                                           



                                                   

ax.axis["right2"] = ax.new_fixed_axis(loc="right", offset=(20, 0))

ax.axis["right2"].label.set_text("Label Y2")



ax.plot([-2, 3, 2])

plt.show()


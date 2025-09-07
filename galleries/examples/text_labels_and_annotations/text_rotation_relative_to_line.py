



import matplotlib.pyplot as plt



fig, ax = plt.subplots()



                                                     

ax.plot(range(0, 8), range(0, 8))

ax.set_xlim([-10, 10])



           

ax.text(-8, 0, 'text 45° in screen coordinates', fontsize=18,

        rotation=45, rotation_mode='anchor')

ax.text(0, 0, 'text 45° in data coordinates', fontsize=18,

        rotation=45, rotation_mode='anchor',

        transform_rotates_text=True)



plt.show()


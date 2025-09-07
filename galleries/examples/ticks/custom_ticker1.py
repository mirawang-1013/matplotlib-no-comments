



import matplotlib.pyplot as plt





def millions(x, pos):

    

    return f'${x*1e-6:1.1f}M'





fig, ax = plt.subplots()

                                                                           

ax.yaxis.set_major_formatter(millions)

money = [1.5e5, 2.5e6, 5.5e6, 2.0e7]

ax.bar(['Bill', 'Fred', 'Mary', 'Sue'], money)

plt.show()



    

 

                            

 

                                                                              

                     

 

                                                 


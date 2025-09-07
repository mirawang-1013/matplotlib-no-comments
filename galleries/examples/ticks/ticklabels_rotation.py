



import matplotlib.pyplot as plt



x = [1, 2, 3, 4]

y = [1, 4, 9, 6]

labels = ['Frogs', 'Hogs', 'Bogs', 'Slogs']



fig, ax = plt.subplots()

ax.plot(x, y)

                                                          

ax.tick_params("y", rotation=45)

                                                                            

                                        

                                                                               

                             

ax.set_xticks(x, labels, rotation='vertical')



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                           

                                                                     


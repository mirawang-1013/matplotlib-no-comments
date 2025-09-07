



    

              

              

 

                                                          

                                                         



import matplotlib.pyplot as plt



labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'

sizes = [15, 30, 45, 10]



fig, ax = plt.subplots()

ax.pie(sizes, labels=labels)



    

                                                                        

                                                                               

                                               

                                                  

 

                   

                   

 

                                                                



fig, ax = plt.subplots()

ax.pie(sizes, labels=labels, autopct='%1.1f%%')



    

                                                                               

 

              

              

 

                                                                   



fig, ax = plt.subplots()

ax.pie(sizes, labels=labels,

       colors=['olivedrab', 'rosybrown', 'gray', 'saddlebrown'])



    

              

              

 

                                                                            



fig, ax = plt.subplots()

ax.pie(sizes, labels=labels, hatch=['**O', 'oO', 'O.O', '.||.'])



    

                                       

                                       

                                                                               

                                  



fig, ax = plt.subplots()

ax.pie(sizes, labels=labels, autopct='%1.1f%%',

       pctdistance=1.25, labeldistance=.6)



    

                                                                            

                                                                            

                                                                          

 

                                   

                                   

 

                                                                              

 

                                      

                                    

                                         

 

                                                                              



explode = (0, 0.1, 0, 0)                                              



fig, ax = plt.subplots()

ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',

       shadow=True, startangle=90)

plt.show()



    

                                                                               

                                                                              

                                                                               

                         

 

                      

                      

 

                                                                               

                                          



fig, ax = plt.subplots()



ax.pie(sizes, labels=labels, autopct='%.0f%%',

       textprops={'size': 'small'}, radius=0.5)

plt.show()



    

                      

                      

 

                                                                           

                                                                     



fig, ax = plt.subplots()

ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',

       shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=90)

plt.show()



    

                            

 

                                                                              

                     

 

                                                           

 

           

 

                   

                    






                                     



import matplotlib.pyplot as plt



text_kwargs = dict(ha='center', va='center', fontsize=28, color='C1')



    

                                 

                                 

 

plt.subplots(figsize=(6, 2))

plt.text(0.5, 0.5, '6 inches x 2 inches', **text_kwargs)

plt.show()





    

                           

                           

                                                                          

                                                                            

                                                                          

                  

 

cm = 1/2.54                         

plt.subplots(figsize=(15*cm, 5*cm))

plt.text(0.5, 0.5, '15cm x 5cm', **text_kwargs)

plt.show()





    

                      

                      

                                                  

 

                                                                     

                               

 

px = 1/plt.rcParams['figure.dpi']                   

plt.subplots(figsize=(600*px, 200*px))

plt.text(0.5, 0.5, '600px x 200px', **text_kwargs)

plt.show()



    

                                                                           

                                                                         

                               

 

                                                                           

                                            

 

plt.subplots(figsize=(6, 2))

plt.text(0.5, 0.5, '600px x 200px', **text_kwargs)

plt.show()



    

                                                                             

                                                                 

                                                                           

                                   



    

 

                            

 

                                                                              

                     

 

                                 

                                   

                                         

 

           

 

                      

                  

                    


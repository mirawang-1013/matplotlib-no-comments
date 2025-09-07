



import matplotlib.pyplot as plt



import matplotlib.patheffects as path_effects



fig = plt.figure(figsize=(5, 1.5))

text = fig.text(0.5, 0.5, 'Hello path effects world!\nThis is the normal '

                          'path effect.\nPretty dull, huh?',

                ha='center', va='center', size=20)

text.set_path_effects([path_effects.Normal()])

plt.show()



    

                                                                             

                                                                           

                                                                           

           

 

                 

                 

 

                                                                               

                                                                             

                                                                              

                                         



import matplotlib.patheffects as path_effects



text = plt.text(0.5, 0.5, 'Hello path effects world!',

                path_effects=[path_effects.withSimplePatchShadow()])



plt.plot([0, 3, 2, 5], linewidth=5, color='blue',

         path_effects=[path_effects.SimpleLineShadow(),

                       path_effects.Normal()])

plt.show()



    

                                                                            

                                                                       

                                                                     

                                                  

 

                            

                            

 

                                                                            

                                                                             

                                



fig = plt.figure(figsize=(7, 1))

text = fig.text(0.5, 0.5, 'This text stands out because of\n'

                          'its black border.', color='white',

                          ha='center', va='center', size=30)

text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'),

                       path_effects.Normal()])

plt.show()



    

                                                                           

                                                                           

                            

 

                                                                            

                                                                       

                                                                              

                                                                            

                                                                            

                                                                            

                     

 

 

                                           

                                           

 

                                                                         

                                                                        

                                                                         

                                                                            

                                                                             

                                



fig = plt.figure(figsize=(8.5, 1))

t = fig.text(0.02, 0.5, 'Hatch shadow', fontsize=75, weight=1000, va='center')

t.set_path_effects([

    path_effects.PathPatchEffect(

        offset=(4, -4), hatch='xxxx', facecolor='gray'),

    path_effects.PathPatchEffect(

        edgecolor='white', linewidth=1.1, facecolor='black')])

plt.show()



    

    

                                        

 

                                       

                                       

 

                                     

                                      


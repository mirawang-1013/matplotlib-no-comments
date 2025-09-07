



import matplotlib.pyplot as plt

import numpy as np



    

                                                          



species = ('Adelie', 'Chinstrap', 'Gentoo')

sex_counts = {

    'Male': np.array([73, 34, 61]),

    'Female': np.array([73, 34, 58]),

}

width = 0.6                                                      





fig, ax = plt.subplots()

bottom = np.zeros(3)



for sex, sex_count in sex_counts.items():

    p = ax.bar(species, sex_count, width, label=sex, bottom=bottom)

    bottom += sex_count



    ax.bar_label(p, label_type='center')



ax.set_title('Number of penguins by sex')

ax.legend()



plt.show()



    

                      



                                         

np.random.seed(19680801)



              

people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')

y_pos = np.arange(len(people))

performance = 3 + 10 * np.random.rand(len(people))

error = np.random.rand(len(people))



fig, ax = plt.subplots()



hbars = ax.barh(y_pos, performance, xerr=error, align='center')

ax.set_yticks(y_pos, labels=people)

ax.invert_yaxis()                             

ax.set_xlabel('Performance')

ax.set_title('How fast do you want to go today?')



                                       

ax.bar_label(hbars, fmt='%.2f')

ax.set_xlim(right=15)                             



plt.show()



    

                                                                  



fig, ax = plt.subplots()



hbars = ax.barh(y_pos, performance, xerr=error, align='center')

ax.set_yticks(y_pos, labels=people)

ax.invert_yaxis()                             

ax.set_xlabel('Performance')

ax.set_title('How fast do you want to go today?')



                                                                

ax.bar_label(hbars, labels=[f'±{e:.2f}' for e in error],

             padding=8, color='b', fontsize=14)

ax.set_xlim(right=16)



plt.show()



    

                                         



fruit_names = ['Coffee', 'Salted Caramel', 'Pistachio']

fruit_counts = [4000, 2000, 7000]



fig, ax = plt.subplots()

bar_container = ax.bar(fruit_names, fruit_counts)

ax.set(ylabel='pints sold', title='Gelato sales by flavor', ylim=(0, 8000))

ax.bar_label(bar_container, fmt='{:,.0f}')



    

                             



animal_names = ['Lion', 'Gazelle', 'Cheetah']

mph_speed = [50, 60, 75]



fig, ax = plt.subplots()

bar_container = ax.bar(animal_names, mph_speed)

ax.set(ylabel='speed in MPH', title='Running speeds', ylim=(0, 80))

ax.bar_label(bar_container, fmt=lambda x: f'{x * 1.61:.1f} km/h')



    

 

                            

 

                                                                              

                     

 

                                                           

                                                             

                                                                       

 

           

 

                     

                   

                    


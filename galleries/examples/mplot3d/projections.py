



import matplotlib.pyplot as plt



from mpl_toolkits.mplot3d import axes3d



fig, axs = plt.subplots(1, 3, subplot_kw={'projection': '3d'})



                   

X, Y, Z = axes3d.get_test_data(0.05)



               

for ax in axs:

    ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)



                                  

axs[0].set_proj_type('ortho')               

axs[0].set_title("'ortho'\nfocal_length = ∞", fontsize=10)



                                 

axs[1].set_proj_type('persp')                

axs[1].set_title("'persp'\nfocal_length = 1 (default)", fontsize=10)



axs[2].set_proj_type('persp', focal_length=0.2)                   

axs[2].set_title("'persp'\nfocal_length = 0.2", fontsize=10)



plt.show()



    

           

                   

                              

                        

                        


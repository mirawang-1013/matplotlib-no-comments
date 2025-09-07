



import matplotlib.pyplot as plt



fig, ax = plt.subplots(figsize=(6, 5))



                                   

ax.plot(range(11), color="0.9")



                                          

msg = (r"Normal Text. $Text\ in\ math\ mode:\ "

       r"\int_{0}^{\infty } x^2 dx$")



                           

ax.text(1, 7, msg, size=12, math_fontfamily='cm')



                                     

ax.text(1, 3, msg, size=12, math_fontfamily='dejavuserif')



                                                                   

                    

ax.set_title(r"$Title\ in\ math\ mode:\ \int_{0}^{\infty } x^2 dx$",

             math_fontfamily='stixsans', size=14)



                                                                

plt.show()






import matplotlib.pyplot as plt

import numpy as np



fig, axs = plt.subplots(1, 2, figsize=(4, 2))



                                                                         

N = 450

x = np.arange(N) / N - 0.5

y = np.arange(N) / N - 0.5

aa = np.ones((N, N))

aa[::2, :] = -1



X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2)

f0 = 5

k = 100

a = np.sin(np.pi * 2 * (f0 * R + k * R**2 / 2))

                                 

a[:int(N / 2), :][R[:int(N / 2), :] < 0.4] = -1

a[:int(N / 2), :][R[:int(N / 2), :] < 0.3] = 1

aa[:, int(N / 3):] = a[:, int(N / 3):]

alarge = aa



axs[0].imshow(alarge, cmap='RdBu_r')

axs[0].set_title('(450, 450) Down-sampled', fontsize='medium')



np.random.seed(19680801+9)

asmall = np.random.rand(4, 4)

axs[1].imshow(asmall, cmap='viridis')

axs[1].set_title('(4, 4) Up-sampled', fontsize='medium')



    

                                                                                 

                                                                                 

                                                                                 

                                                                     

                                                            

                                                                                

                                                                                 

 

                                                                                   

 

                                                                                   

 

                                                                             

                                                                          

                                                                           

                  

 

                                      

                                      

 

                                                                              

                                                                                

                                                                             

                                                                              

                                                  

 

                                                                             

                                                       

                                                                           

                                                                               

                                                                           

                



fig, ax = plt.subplots(figsize=(4, 4), layout='compressed')

ax.imshow(alarge, interpolation='nearest', cmap='RdBu_r')

ax.set_xlim(100, 200)

ax.set_ylim(275, 175)

ax.set_title('Zoom')



    

                                                                         

                                 

                                                                           

                                             



fig, axs = plt.subplots(1, 2, figsize=(5, 2.7), layout='compressed')

for ax, interp, space in zip(axs.flat, ['nearest', 'nearest'],

                                       ['data', 'rgba']):

    ax.imshow(alarge, interpolation=interp, interpolation_stage=space,

              cmap='RdBu_r')

    ax.set_title(f"interpolation='{interp}'\nstage='{space}'")



    

                                                                             

                                                                             

                                                                           

                                                                                

                                



fig, axs = plt.subplots(1, 2, figsize=(5, 2.7), layout='compressed')

for ax, interp, space in zip(axs.flat, ['hanning', 'hanning'],

                                       ['data', 'rgba']):

    ax.imshow(alarge, interpolation=interp, interpolation_stage=space,

              cmap='RdBu_r')

    ax.set_title(f"interpolation='{interp}'\nstage='{space}'")

plt.show()



    

                                                                             

                                                                         

                                                                       

                                                                              

                                                                           

                                                                           

                                                                           

                                                                                      

                                                                               

                                                                               

        

 

                                                                      

                                                                               

                                                                            

                                                                  

                                                                 

                

 

                                                                               

                                                                           

                                                                              

                                                                             

                                                                       



fig, ax = plt.subplots(figsize=(6.8, 6.8))

ax.imshow(alarge, interpolation='nearest', cmap='grey')

ax.set_title("up-sampled by factor a 1.17, interpolation='nearest'")



    

                                                         

fig, ax = plt.subplots(figsize=(6.8, 6.8))

ax.imshow(alarge, interpolation='auto', cmap='grey')

ax.set_title("up-sampled by factor a 1.17, interpolation='auto'")



    

                                                                            

                                                                        

                                         

fig, axs = plt.subplots(1, 2, figsize=(7, 4), layout='constrained')

for ax, interp in zip(axs, ['hanning', 'lanczos']):

    ax.imshow(alarge, interpolation=interp, cmap='gray')

    ax.set_title(f"interpolation='{interp}'")



    

                                                                               

                                                                             

                                                                             

                                                                             

                                                                            

                                                                            

                                                                               

                                                                    

                                                                           

                                                                          

                                                                   

                                                               



a = alarge + 1

cmap = plt.get_cmap('RdBu_r')

cmap.set_under('yellow')

cmap.set_over('limegreen')



fig, axs = plt.subplots(1, 3, figsize=(7, 3), layout='constrained')

for ax, interp, space in zip(axs.flat,

                             ['hanning', 'nearest', 'hanning', ],

                             ['data', 'data', 'rgba']):

    im = ax.imshow(a, interpolation=interp, interpolation_stage=space,

                   cmap=cmap, vmin=0, vmax=2)

    title = f"interpolation='{interp}'\nstage='{space}'"

    if ax == axs[2]:

        title += '\nDefault'

    ax.set_title(title, fontsize='medium')

fig.colorbar(im, ax=axs, extend='both', shrink=0.8)



    

             

             

 

                                                                                     

                                                                         



np.random.seed(19680801+9)

a = np.random.rand(4, 4)



fig, axs = plt.subplots(1, 2, figsize=(6.5, 4), layout='compressed')

axs[0].imshow(asmall, cmap='viridis')

axs[0].set_title("interpolation='auto'\nstage='auto'")

axs[1].imshow(asmall, cmap='viridis', interpolation="nearest",

              interpolation_stage="data")

axs[1].set_title("interpolation='nearest'\nstage='data'")

plt.show()



    

                                                                                   

                                                                                     

                                                                                     

                                                                                   

                                                                                 

                                                                         

                                                     



fig, axs = plt.subplots(1, 2, figsize=(6.5, 4), layout='compressed')

im = axs[0].imshow(a, cmap='viridis', interpolation='sinc', interpolation_stage='data')

axs[0].set_title("interpolation='sinc'\nstage='data'\n(default for upsampling)")

axs[1].imshow(a, cmap='viridis', interpolation='sinc', interpolation_stage='rgba')

axs[1].set_title("interpolation='sinc'\nstage='rgba'")

fig.colorbar(im, ax=axs, shrink=0.7, extend='both')



    

                     

                     

 

                                                                              

                                                            

                                                                              

                                                               

 

                                                                            

                                                                      

                                                                                   

                                                                              

                                                                                       

                                                                       



fig = plt.figure(figsize=(2, 2))

ax = fig.add_axes((0, 0, 1, 1))

ax.imshow(aa[:400, :400], cmap='RdBu_r', interpolation='nearest')

plt.show()

    

 

                            

 

                                                                              

                     

 

                                    


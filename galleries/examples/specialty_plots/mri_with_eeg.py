



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.cbook as cbook



fig, axd = plt.subplot_mosaic(

    [["image", "density"],

     ["EEG", "EEG"]],

    layout="constrained",

                                                                         

                                                                        

    width_ratios=[1.05, 2],

)



                                             

with cbook.get_sample_data('s1045.ima.gz') as dfile:

    im = np.frombuffer(dfile.read(), np.uint16).reshape((256, 256))



                    

axd["image"].imshow(im, cmap="gray")

axd["image"].axis('off')



                                     

im = im[im.nonzero()]                         

axd["density"].hist(im, bins=np.arange(0, 2**16+1, 512))

axd["density"].set(xlabel='Intensity (a.u.)', xlim=(0, 2**16),

                   ylabel='MRI density', yticks=[])

axd["density"].minorticks_on()



                   

n_samples, n_rows = 800, 4

with cbook.get_sample_data('eeg.dat') as eegfile:

    data = np.fromfile(eegfile, dtype=float).reshape((n_samples, n_rows))

t = 10 * np.arange(n_samples) / n_samples



              

axd["EEG"].set_xlabel('Time (s)')

axd["EEG"].set_xlim(0, 10)

dy = (data.min() - data.max()) * 0.7                     

axd["EEG"].set_ylim(-dy, n_rows * dy)

axd["EEG"].set_yticks([0, dy, 2*dy, 3*dy], labels=['PG3', 'PG5', 'PG7', 'PG9'])



for i, data_col in enumerate(data.T):

    axd["EEG"].plot(t, data_col + i*dy, color="C0")



plt.show()


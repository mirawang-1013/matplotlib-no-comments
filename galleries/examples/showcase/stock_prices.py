



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.cbook import get_sample_data

import matplotlib.transforms as mtransforms



with get_sample_data('Stocks.csv') as file:

    stock_data = np.genfromtxt(

        file, delimiter=',', names=True, dtype=None,

        converters={0: lambda x: np.datetime64(x, 'D')}, skip_header=1)



fig, ax = plt.subplots(1, 1, figsize=(6, 8), layout='constrained')



                                                    

ax.set_prop_cycle(color=[

    '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a',

    '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94',

    '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d',

    '#17becf', '#9edae5'])



stocks_name = ['IBM', 'Apple', 'Microsoft', 'Xerox', 'Amazon', 'Dell',

               'Alphabet', 'Adobe', 'S&P 500', 'NASDAQ']

stocks_ticker = ['IBM', 'AAPL', 'MSFT', 'XRX', 'AMZN', 'DELL', 'GOOGL',

                 'ADBE', 'GSPC', 'IXIC']



                                                                               

y_offsets = dict.fromkeys(stocks_ticker, 0)

y_offsets['IBM'] = 5

y_offsets['AAPL'] = -5

y_offsets['AMZN'] = -6



for nn, column in enumerate(stocks_ticker):

                                                   

                                      

    good = np.nonzero(np.isfinite(stock_data[column]))

    line, = ax.plot(stock_data['Date'][good], stock_data[column][good], lw=2.5)



                                                                             

                                                                           

    y_pos = stock_data[column][-1]



                                                                              

                 

    offset = y_offsets[column] / 72

    trans = mtransforms.ScaledTranslation(0, offset, fig.dpi_scale_trans)

    trans = ax.transData + trans



                                                                         

                    

    ax.text(np.datetime64('2022-10-01'), y_pos, stocks_name[nn],

            color=line.get_color(), transform=trans)



ax.set_xlim(np.datetime64('1989-06-01'), np.datetime64('2023-01-01'))



fig.suptitle("Technology company stocks prices dollars (1990-2022)",

             ha="center")



                                                         

ax.spines[:].set_visible(False)



                                                                             

                                                                   

ax.xaxis.tick_bottom()

ax.yaxis.tick_left()

ax.set_yscale('log')



                                                                     

                                                                      

                                       

ax.grid(True, 'major', 'both', ls='--', lw=.5, c='k', alpha=.3)



                                                                         

                                                                        

                                                          

ax.tick_params(axis='both', which='both', labelsize='large',

               bottom=False, top=False, labelbottom=True,

               left=False, right=False, labelleft=True)



                                    

                                           

                                              

                                                      

plt.show()



    

 

                            

 

                                                                              

                     

 

                                   

                                  

                                          

                                        

                                             


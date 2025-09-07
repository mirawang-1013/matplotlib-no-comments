def blocking_input_loop(figure, event_names, timeout, handler):

    

    if figure.canvas.manager:

        figure.show()                                                          

                                                       

    cids = [figure.canvas.mpl_connect(name, handler) for name in event_names]

    try:

        figure.canvas.start_event_loop(timeout)                     

    finally:                                      

                                   

        for cid in cids:

            figure.canvas.mpl_disconnect(cid)






import atexit

from collections import OrderedDict





class Gcf:

    



    figs = OrderedDict()



    @classmethod

    def get_fig_manager(cls, num):

        

        manager = cls.figs.get(num, None)

        if manager is not None:

            cls.set_active(manager)

        return manager



    @classmethod

    def destroy(cls, num):

        

        if all(hasattr(num, attr) for attr in ["num", "destroy"]):

            manager = num

            if cls.figs.get(manager.num) is manager:

                cls.figs.pop(manager.num)

        else:

            try:

                manager = cls.figs.pop(num)

            except KeyError:

                return

        if hasattr(manager, "_cidgcf"):

            manager.canvas.mpl_disconnect(manager._cidgcf)

        manager.destroy()



    @classmethod

    def destroy_fig(cls, fig):

        

        manager = next((manager for manager in cls.figs.values()

                       if manager.canvas.figure == fig), None)

        if manager is not None:

            cls.destroy(manager)



    @classmethod

    def destroy_all(cls):

        

        for manager in list(cls.figs.values()):

            manager.canvas.mpl_disconnect(manager._cidgcf)

            manager.destroy()

        cls.figs.clear()



    @classmethod

    def has_fignum(cls, num):

        

        return num in cls.figs



    @classmethod

    def get_all_fig_managers(cls):

        

        return list(cls.figs.values())



    @classmethod

    def get_num_fig_managers(cls):

        

        return len(cls.figs)



    @classmethod

    def get_active(cls):

        

        return next(reversed(cls.figs.values())) if cls.figs else None



    @classmethod

    def _set_new_active_manager(cls, manager):

        

        if not hasattr(manager, "_cidgcf"):

            manager._cidgcf = manager.canvas.mpl_connect(

                "button_press_event", lambda event: cls.set_active(manager))

        fig = manager.canvas.figure

        fig._number = manager.num

        label = fig.get_label()

        if label:

            manager.set_window_title(label)

        cls.set_active(manager)



    @classmethod

    def set_active(cls, manager):

        

        cls.figs[manager.num] = manager

        cls.figs.move_to_end(manager.num)



    @classmethod

    def draw_all(cls, force=False):

        

        for manager in cls.get_all_fig_managers():

            if force or manager.canvas.figure.stale:

                manager.canvas.draw_idle()





atexit.register(Gcf.destroy_all)


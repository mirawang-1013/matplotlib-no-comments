



import itertools



import numpy as np



from matplotlib import _api



__all__ = ['stackplot']





def stackplot(axes, x, *args,

              labels=(), colors=None, hatch=None, baseline='zero',

              **kwargs):

    



    y = np.vstack(args)



    labels = iter(labels)

    if colors is not None:

        colors = itertools.cycle(colors)

    else:

        colors = (axes._get_lines.get_next_color() for _ in y)



    if hatch is None or isinstance(hatch, str):

        hatch = itertools.cycle([hatch])

    else:

        hatch = itertools.cycle(hatch)



                                                                  

                                                              

    stack = np.cumsum(y, axis=0, dtype=np.promote_types(y.dtype, np.float32))



    _api.check_in_list(['zero', 'sym', 'wiggle', 'weighted_wiggle'],

                       baseline=baseline)

    if baseline == 'zero':

        first_line = 0.



    elif baseline == 'sym':

        first_line = -np.sum(y, 0) * 0.5

        stack += first_line[None, :]



    elif baseline == 'wiggle':

        m = y.shape[0]

        first_line = (y * (m - 0.5 - np.arange(m)[:, None])).sum(0)

        first_line /= -m

        stack += first_line



    elif baseline == 'weighted_wiggle':

        total = np.sum(y, 0)

                                                                            

        inv_total = np.zeros_like(total)

        mask = total > 0

        inv_total[mask] = 1.0 / total[mask]

        increase = np.hstack((y[:, 0:1], np.diff(y)))

        below_size = total - stack

        below_size += 0.5 * y

        move_up = below_size * inv_total

        move_up[:, 0] = 0.5

        center = (move_up - 0.5) * increase

        center = np.cumsum(center.sum(0))

        first_line = center - 0.5 * total

        stack += first_line



                                              

    coll = axes.fill_between(x, first_line, stack[0, :],

                             facecolor=next(colors),

                             hatch=next(hatch),

                             label=next(labels, None),

                             **kwargs)

    coll.sticky_edges.y[:] = [0]

    r = [coll]



                                         

    for i in range(len(y) - 1):

        r.append(axes.fill_between(x, stack[i, :], stack[i + 1, :],

                                   facecolor=next(colors),

                                   hatch=next(hatch),

                                   label=next(labels, None),

                                   **kwargs))

    return r


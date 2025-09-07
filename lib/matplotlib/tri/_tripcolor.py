import numpy as np



from matplotlib import _api, _docstring

from matplotlib.collections import PolyCollection, TriMesh

from matplotlib.tri._triangulation import Triangulation





@_docstring.interpd

def tripcolor(ax, *args, alpha=1.0, norm=None, cmap=None, vmin=None,

              vmax=None, shading='flat', facecolors=None, **kwargs):

    

    _api.check_in_list(['flat', 'gouraud'], shading=shading)



    tri, args, kwargs = Triangulation.get_from_args_and_kwargs(*args, **kwargs)



                                                                        

                                                      

                                                

    if facecolors is not None:

        if args:

            _api.warn_external(

                "Positional parameter c has no effect when the keyword "

                "facecolors is given")

        point_colors = None

        if len(facecolors) != len(tri.triangles):

            raise ValueError("The length of facecolors must match the number "

                             "of triangles")

    else:

                                           

        if not args:

            raise TypeError(

                "tripcolor() missing 1 required positional argument: 'c'; or "

                "1 required keyword-only argument: 'facecolors'")

        elif len(args) > 1:

            raise TypeError(f"Unexpected positional parameters: {args[1:]!r}")

        c = np.asarray(args[0])

        if len(c) == len(tri.x):

                                                                        

                                                                         

            point_colors = c

            facecolors = None

        elif len(c) == len(tri.triangles):

            point_colors = None

            facecolors = c

        else:

            raise ValueError('The length of c must match either the number '

                             'of points or the number of triangles')



                                                                    

                    

    linewidths = (0.25,)

    if 'linewidth' in kwargs:

        kwargs['linewidths'] = kwargs.pop('linewidth')

    kwargs.setdefault('linewidths', linewidths)



    edgecolors = 'none'

    if 'edgecolor' in kwargs:

        kwargs['edgecolors'] = kwargs.pop('edgecolor')

    ec = kwargs.setdefault('edgecolors', edgecolors)



    if 'antialiased' in kwargs:

        kwargs['antialiaseds'] = kwargs.pop('antialiased')

    if 'antialiaseds' not in kwargs and ec.lower() == "none":

        kwargs['antialiaseds'] = False



    if shading == 'gouraud':

        if facecolors is not None:

            raise ValueError(

                "shading='gouraud' can only be used when the colors "

                "are specified at the points, not at the faces.")

        collection = TriMesh(tri, alpha=alpha, array=point_colors,

                             cmap=cmap, norm=norm, **kwargs)

    else:          

                                

        maskedTris = tri.get_masked_triangles()

        verts = np.stack((tri.x[maskedTris], tri.y[maskedTris]), axis=-1)



                       

        if facecolors is None:

                                                                            

            colors = point_colors[maskedTris].mean(axis=1)

        elif tri.mask is not None:

                                                      

            colors = facecolors[~tri.mask]

        else:

            colors = facecolors

        collection = PolyCollection(verts, alpha=alpha, array=colors,

                                    cmap=cmap, norm=norm, **kwargs)



    collection._scale_norm(norm, vmin, vmax)

    ax.grid(False)



    minx = tri.x.min()

    maxx = tri.x.max()

    miny = tri.y.min()

    maxy = tri.y.max()

    corners = (minx, miny), (maxx, maxy)

    ax.update_datalim(corners)

    ax.autoscale_view()

                                                                  

                              

    ax.add_collection(collection, autolim=False)

    return collection


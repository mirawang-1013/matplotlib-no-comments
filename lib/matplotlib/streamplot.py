



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cm, patches

import matplotlib.colors as mcolors

import matplotlib.collections as mcollections

import matplotlib.lines as mlines





__all__ = ['streamplot']





def streamplot(axes, x, y, u, v, density=1, linewidth=None, color=None,

               cmap=None, norm=None, arrowsize=1, arrowstyle='-|>',

               minlength=0.1, transform=None, zorder=None, start_points=None,

               maxlength=4.0, integration_direction='both',

               broken_streamlines=True, *, integration_max_step_scale=1.0,

               integration_max_error_scale=1.0, num_arrows=1):

    

    grid = Grid(x, y)

    mask = StreamMask(density)

    dmap = DomainMap(grid, mask)



    if integration_max_step_scale <= 0.0:

        raise ValueError(

            "The value of integration_max_step_scale must be > 0, " +

            f"got {integration_max_step_scale}"

        )



    if integration_max_error_scale <= 0.0:

        raise ValueError(

            "The value of integration_max_error_scale must be > 0, " +

            f"got {integration_max_error_scale}"

        )



    if num_arrows < 0:

        raise ValueError(f"The value of num_arrows must be >= 0, got {num_arrows=}")



    if zorder is None:

        zorder = mlines.Line2D.zorder



                                 

    if transform is None:

        transform = axes.transData



    if color is None:

        color = axes._get_lines.get_next_color()



    linewidth = mpl._val_or_rc(linewidth, 'lines.linewidth')



    line_kw = {}

    arrow_kw = dict(arrowstyle=arrowstyle, mutation_scale=10 * arrowsize)



    _api.check_in_list(['both', 'forward', 'backward'],

                       integration_direction=integration_direction)



    if integration_direction == 'both':

        maxlength /= 2.



    use_multicolor_lines = isinstance(color, np.ndarray)

    if use_multicolor_lines:

        if color.shape != grid.shape:

            raise ValueError("If 'color' is given, it must match the shape of "

                             "the (x, y) grid")

        line_colors = [[]]                                                    

        color = np.ma.masked_invalid(color)

    else:

        line_kw['color'] = color

        arrow_kw['color'] = color



    if isinstance(linewidth, np.ndarray):

        if linewidth.shape != grid.shape:

            raise ValueError("If 'linewidth' is given, it must match the "

                             "shape of the (x, y) grid")

        line_kw['linewidth'] = []

    else:

        line_kw['linewidth'] = linewidth

        arrow_kw['linewidth'] = linewidth



    line_kw['zorder'] = zorder

    arrow_kw['zorder'] = zorder



                    

    if u.shape != grid.shape or v.shape != grid.shape:

        raise ValueError("'u' and 'v' must match the shape of the (x, y) grid")



    u = np.ma.masked_invalid(u)

    v = np.ma.masked_invalid(v)



    integrate = _get_integrator(u, v, dmap, minlength, maxlength,

                                integration_direction)



    trajectories = []

    if start_points is None:

        for xm, ym in _gen_starting_points(mask.shape):

            if mask[ym, xm] == 0:

                xg, yg = dmap.mask2grid(xm, ym)

                t = integrate(xg, yg, broken_streamlines,

                              integration_max_step_scale,

                              integration_max_error_scale)

                if t is not None:

                    trajectories.append(t)

    else:

        sp2 = np.asanyarray(start_points, dtype=float).copy()



                                                               

        for xs, ys in sp2:

            if not (grid.x_origin <= xs <= grid.x_origin + grid.width and

                    grid.y_origin <= ys <= grid.y_origin + grid.height):

                raise ValueError(f"Starting point ({xs}, {ys}) outside of "

                                 "data boundaries")



                                                        

                                                                        

                                   

        sp2[:, 0] -= grid.x_origin

        sp2[:, 1] -= grid.y_origin



        for xs, ys in sp2:

            xg, yg = dmap.data2grid(xs, ys)

                                                                          

                                                                        

                                                                              

                                                                         

            xg = np.clip(xg, 0, grid.nx - 1)

            yg = np.clip(yg, 0, grid.ny - 1)



            t = integrate(xg, yg, broken_streamlines, integration_max_step_scale,

                          integration_max_error_scale)

            if t is not None:

                trajectories.append(t)



    if use_multicolor_lines:

        if norm is None:

            norm = mcolors.Normalize(color.min(), color.max())

        cmap = cm._ensure_cmap(cmap)



    streamlines = []

    arrows = []

    for t in trajectories:

        tgx, tgy = t.T

                                                            

        tx, ty = dmap.grid2data(tgx, tgy)

        tx += grid.x_origin

        ty += grid.y_origin



                                                                          

        if isinstance(linewidth, np.ndarray) or use_multicolor_lines:

            points = np.transpose([tx, ty]).reshape(-1, 1, 2)

            streamlines.extend(np.hstack([points[:-1], points[1:]]))

        else:

            points = np.transpose([tx, ty])

            streamlines.append(points)



                                   

        s = np.cumsum(np.hypot(np.diff(tx), np.diff(ty)))

        if isinstance(linewidth, np.ndarray):

            line_widths = interpgrid(linewidth, tgx, tgy)[:-1]

            line_kw['linewidth'].extend(line_widths)

        if use_multicolor_lines:

            color_values = interpgrid(color, tgx, tgy)[:-1]

            line_colors.append(color_values)



                                           

        for x in range(1, num_arrows+1):

                                                                   

            idx = np.searchsorted(s, s[-1] * (x/(num_arrows+1)))

            arrow_tail = (tx[idx], ty[idx])

            arrow_head = (np.mean(tx[idx:idx + 2]), np.mean(ty[idx:idx + 2]))



            if isinstance(linewidth, np.ndarray):

                arrow_kw['linewidth'] = line_widths[idx]



            if use_multicolor_lines:

                arrow_kw['color'] = cmap(norm(color_values[idx]))



            p = patches.FancyArrowPatch(

                arrow_tail, arrow_head, transform=transform, **arrow_kw)

            arrows.append(p)



    lc = mcollections.LineCollection(

        streamlines, transform=transform, **line_kw)

    lc.sticky_edges.x[:] = [grid.x_origin, grid.x_origin + grid.width]

    lc.sticky_edges.y[:] = [grid.y_origin, grid.y_origin + grid.height]

    if use_multicolor_lines:

        lc.set_array(np.ma.hstack(line_colors))

        lc.set_cmap(cmap)

        lc.set_norm(norm)

    axes.add_collection(lc)



    ac = mcollections.PatchCollection(arrows)

                                                        

    for p in arrows:

        axes.add_patch(p)



    axes.autoscale_view()

    stream_container = StreamplotSet(lc, ac)

    return stream_container





class StreamplotSet:



    def __init__(self, lines, arrows):

        self.lines = lines

        self.arrows = arrows





                        

                          



class DomainMap:

    



    def __init__(self, grid, mask):

        self.grid = grid

        self.mask = mask

                                                                     

        self.x_grid2mask = (mask.nx - 1) / (grid.nx - 1)

        self.y_grid2mask = (mask.ny - 1) / (grid.ny - 1)



        self.x_mask2grid = 1. / self.x_grid2mask

        self.y_mask2grid = 1. / self.y_grid2mask



        self.x_data2grid = 1. / grid.dx

        self.y_data2grid = 1. / grid.dy



    def grid2mask(self, xi, yi):

        

        return round(xi * self.x_grid2mask), round(yi * self.y_grid2mask)



    def mask2grid(self, xm, ym):

        return xm * self.x_mask2grid, ym * self.y_mask2grid



    def data2grid(self, xd, yd):

        return xd * self.x_data2grid, yd * self.y_data2grid



    def grid2data(self, xg, yg):

        return xg / self.x_data2grid, yg / self.y_data2grid



    def start_trajectory(self, xg, yg, broken_streamlines=True):

        xm, ym = self.grid2mask(xg, yg)

        self.mask._start_trajectory(xm, ym, broken_streamlines)



    def reset_start_point(self, xg, yg):

        xm, ym = self.grid2mask(xg, yg)

        self.mask._current_xy = (xm, ym)



    def update_trajectory(self, xg, yg, broken_streamlines=True):

        if not self.grid.within_grid(xg, yg):

            raise InvalidIndexError

        xm, ym = self.grid2mask(xg, yg)

        self.mask._update_trajectory(xm, ym, broken_streamlines)



    def undo_trajectory(self):

        self.mask._undo_trajectory()





class Grid:

    

    def __init__(self, x, y):



        if np.ndim(x) == 1:

            pass

        elif np.ndim(x) == 2:

            x_row = x[0]

            if not np.allclose(x_row, x):

                raise ValueError("The rows of 'x' must be equal")

            x = x_row

        else:

            raise ValueError("'x' can have at maximum 2 dimensions")



        if np.ndim(y) == 1:

            pass

        elif np.ndim(y) == 2:

            yt = np.transpose(y)                                

            y_col = yt[0]

            if not np.allclose(y_col, yt):

                raise ValueError("The columns of 'y' must be equal")

            y = y_col

        else:

            raise ValueError("'y' can have at maximum 2 dimensions")



        if not (np.diff(x) > 0).all():

            raise ValueError("'x' must be strictly increasing")

        if not (np.diff(y) > 0).all():

            raise ValueError("'y' must be strictly increasing")



        self.nx = len(x)

        self.ny = len(y)



        self.dx = x[1] - x[0]

        self.dy = y[1] - y[0]



        self.x_origin = x[0]

        self.y_origin = y[0]



        self.width = x[-1] - x[0]

        self.height = y[-1] - y[0]



        if not np.allclose(np.diff(x), self.width / (self.nx - 1)):

            raise ValueError("'x' values must be equally spaced")

        if not np.allclose(np.diff(y), self.height / (self.ny - 1)):

            raise ValueError("'y' values must be equally spaced")



    @property

    def shape(self):

        return self.ny, self.nx



    def within_grid(self, xi, yi):

        

                                                                               

                                                                       

        return 0 <= xi <= self.nx - 1 and 0 <= yi <= self.ny - 1





class StreamMask:

    



    def __init__(self, density):

        try:

            self.nx, self.ny = (30 * np.broadcast_to(density, 2)).astype(int)

        except ValueError as err:

            raise ValueError("'density' must be a scalar or be of length "

                             "2") from err

        if self.nx < 0 or self.ny < 0:

            raise ValueError("'density' must be positive")

        self._mask = np.zeros((self.ny, self.nx))

        self.shape = self._mask.shape



        self._current_xy = None



    def __getitem__(self, args):

        return self._mask[args]



    def _start_trajectory(self, xm, ym, broken_streamlines=True):

        

        self._traj = []

        self._update_trajectory(xm, ym, broken_streamlines)



    def _undo_trajectory(self):

        

        for t in self._traj:

            self._mask[t] = 0



    def _update_trajectory(self, xm, ym, broken_streamlines=True):

        

        if self._current_xy != (xm, ym):

            if self[ym, xm] == 0:

                self._traj.append((ym, xm))

                self._mask[ym, xm] = 1

                self._current_xy = (xm, ym)

            else:

                if broken_streamlines:

                    raise InvalidIndexError

                else:

                    pass





class InvalidIndexError(Exception):

    pass





class TerminateTrajectory(Exception):

    pass





                        

                         



def _get_integrator(u, v, dmap, minlength, maxlength, integration_direction):



                                                              

    u, v = dmap.data2grid(u, v)



                                                     

    u_ax = u / (dmap.grid.nx - 1)

    v_ax = v / (dmap.grid.ny - 1)

    speed = np.ma.sqrt(u_ax ** 2 + v_ax ** 2)



    def forward_time(xi, yi):

        if not dmap.grid.within_grid(xi, yi):

            raise OutOfBounds

        ds_dt = interpgrid(speed, xi, yi)

        if ds_dt == 0:

            raise TerminateTrajectory()

        dt_ds = 1. / ds_dt

        ui = interpgrid(u, xi, yi)

        vi = interpgrid(v, xi, yi)

        return ui * dt_ds, vi * dt_ds



    def backward_time(xi, yi):

        dxi, dyi = forward_time(xi, yi)

        return -dxi, -dyi



    def integrate(x0, y0, broken_streamlines=True, integration_max_step_scale=1.0,

                  integration_max_error_scale=1.0):

        



        stotal, xy_traj = 0., []



        try:

            dmap.start_trajectory(x0, y0, broken_streamlines)

        except InvalidIndexError:

            return None

        if integration_direction in ['both', 'backward']:

            s, xyt = _integrate_rk12(x0, y0, dmap, backward_time, maxlength,

                                     broken_streamlines,

                                     integration_max_step_scale,

                                     integration_max_error_scale)

            stotal += s

            xy_traj += xyt[::-1]



        if integration_direction in ['both', 'forward']:

            dmap.reset_start_point(x0, y0)

            s, xyt = _integrate_rk12(x0, y0, dmap, forward_time, maxlength,

                                     broken_streamlines,

                                     integration_max_step_scale,

                                     integration_max_error_scale)

            stotal += s

            xy_traj += xyt[1:]



        if stotal > minlength:

            return np.broadcast_arrays(xy_traj, np.empty((1, 2)))[0]

        else:                             

            dmap.undo_trajectory()

            return None



    return integrate





class OutOfBounds(IndexError):

    pass





def _integrate_rk12(x0, y0, dmap, f, maxlength, broken_streamlines=True,

                    integration_max_step_scale=1.0,

                    integration_max_error_scale=1.0):

    

                                                                     

                                                            

                                              

    maxerror = 0.003 * integration_max_error_scale



                                                                

                                                              

                                                                  

                                                                     

                                                                   

                                    

    maxds = min(1. / dmap.mask.nx, 1. / dmap.mask.ny, 0.1)

    maxds *= integration_max_step_scale



    ds = maxds

    stotal = 0

    xi = x0

    yi = y0

    xyf_traj = []



    while True:

        try:

            if dmap.grid.within_grid(xi, yi):

                xyf_traj.append((xi, yi))

            else:

                raise OutOfBounds



                                                     

                                                                   

                               

            k1x, k1y = f(xi, yi)

            k2x, k2y = f(xi + ds * k1x, yi + ds * k1y)



        except OutOfBounds:

                                                 

                                                                    

                                                       

            if xyf_traj:

                ds, xyf_traj = _euler_step(xyf_traj, dmap, f)

                stotal += ds

            break

        except TerminateTrajectory:

            break



        dx1 = ds * k1x

        dy1 = ds * k1y

        dx2 = ds * 0.5 * (k1x + k2x)

        dy2 = ds * 0.5 * (k1y + k2y)



        ny, nx = dmap.grid.shape

                                                     

        error = np.hypot((dx2 - dx1) / (nx - 1), (dy2 - dy1) / (ny - 1))



                                                  

        if error < maxerror:

            xi += dx2

            yi += dy2

            try:

                dmap.update_trajectory(xi, yi, broken_streamlines)

            except InvalidIndexError:

                break

            if stotal + ds > maxlength:

                break

            stotal += ds



                                                  

        if error == 0:

            ds = maxds

        else:

            ds = min(maxds, 0.85 * ds * (maxerror / error) ** 0.5)



    return stotal, xyf_traj





def _euler_step(xyf_traj, dmap, f):

    

    ny, nx = dmap.grid.shape

    xi, yi = xyf_traj[-1]

    cx, cy = f(xi, yi)

    if cx == 0:

        dsx = np.inf

    elif cx < 0:

        dsx = xi / -cx

    else:

        dsx = (nx - 1 - xi) / cx

    if cy == 0:

        dsy = np.inf

    elif cy < 0:

        dsy = yi / -cy

    else:

        dsy = (ny - 1 - yi) / cy

    ds = min(dsx, dsy)

    xyf_traj.append((xi + cx * ds, yi + cy * ds))

    return ds, xyf_traj





                   

                          



def interpgrid(a, xi, yi):

    



    Ny, Nx = np.shape(a)

    if isinstance(xi, np.ndarray):

        x = xi.astype(int)

        y = yi.astype(int)

                                                  

        xn = np.clip(x + 1, 0, Nx - 1)

        yn = np.clip(y + 1, 0, Ny - 1)

    else:

        x = int(xi)

        y = int(yi)

                                                          

        if x == (Nx - 1):

            xn = x

        else:

            xn = x + 1

        if y == (Ny - 1):

            yn = y

        else:

            yn = y + 1



    a00 = a[y, x]

    a01 = a[y, xn]

    a10 = a[yn, x]

    a11 = a[yn, xn]

    xt = xi - x

    yt = yi - y

    a0 = a00 * (1 - xt) + a01 * xt

    a1 = a10 * (1 - xt) + a11 * xt

    ai = a0 * (1 - yt) + a1 * yt



    if not isinstance(xi, np.ndarray):

        if np.ma.is_masked(ai):

            raise TerminateTrajectory



    return ai





def _gen_starting_points(shape):

    

    ny, nx = shape

    xfirst = 0

    yfirst = 1

    xlast = nx - 1

    ylast = ny - 1

    x, y = 0, 0

    direction = 'right'

    for i in range(nx * ny):

        yield x, y



        if direction == 'right':

            x += 1

            if x >= xlast:

                xlast -= 1

                direction = 'up'

        elif direction == 'up':

            y += 1

            if y >= ylast:

                ylast -= 1

                direction = 'left'

        elif direction == 'left':

            x -= 1

            if x <= xfirst:

                xfirst += 1

                direction = 'down'

        elif direction == 'down':

            y -= 1

            if y <= yfirst:

                yfirst += 1

                direction = 'right'






import numpy as np



from matplotlib import _api

from matplotlib.tri import Triangulation

from matplotlib.tri._trifinder import TriFinder

from matplotlib.tri._tritools import TriAnalyzer



__all__ = ('TriInterpolator', 'LinearTriInterpolator', 'CubicTriInterpolator')





class TriInterpolator:

    



    def __init__(self, triangulation, z, trifinder=None):

        _api.check_isinstance(Triangulation, triangulation=triangulation)

        self._triangulation = triangulation



        self._z = np.asarray(z)

        if self._z.shape != self._triangulation.x.shape:

            raise ValueError("z array must have same length as triangulation x"

                             " and y arrays")



        _api.check_isinstance((TriFinder, None), trifinder=trifinder)

        self._trifinder = trifinder or self._triangulation.get_trifinder()



                                                      

                                                                       

                                                                        

                                                                     

        self._unit_x = 1.0

        self._unit_y = 1.0



                                                               

                                                                   

                                                                   

                                                                     

        self._tri_renum = None



                                                                   

                                              

                                                                       

                                     

    _docstring__call__ = """
        Returns a masked array containing interpolated values at the specified
        (x, y) points.

        Parameters
        ----------
        x, y : array-like
            x and y coordinates of the same shape and any number of
            dimensions.

        Returns
        -------
        np.ma.array
            Masked array of the same shape as *x* and *y*; values corresponding
            to (*x*, *y*) points outside of the triangulation are masked out.

        """



    _docstringgradient = r"""
        Returns a list of 2 masked arrays containing interpolated derivatives
        at the specified (x, y) points.

        Parameters
        ----------
        x, y : array-like
            x and y coordinates of the same shape and any number of
            dimensions.

        Returns
        -------
        dzdx, dzdy : np.ma.array
            2 masked arrays of the same shape as *x* and *y*; values
            corresponding to (x, y) points outside of the triangulation
            are masked out.
            The first returned array contains the values of
            :math:`\frac{\partial z}{\partial x}` and the second those of
            :math:`\frac{\partial z}{\partial y}`.

        """



    def _interpolate_multikeys(self, x, y, tri_index=None,

                               return_keys=('z',)):

        

                                                     

                                              

        x = np.asarray(x, dtype=np.float64)

        y = np.asarray(y, dtype=np.float64)

        sh_ret = x.shape

        if x.shape != y.shape:

            raise ValueError("x and y shall have same shapes."

                             f" Given: {x.shape} and {y.shape}")

        x = np.ravel(x)

        y = np.ravel(y)

        x_scaled = x/self._unit_x

        y_scaled = y/self._unit_y

        size_ret = np.size(x_scaled)



                                                                        

        if tri_index is None:

            tri_index = self._trifinder(x, y)

        else:

            if tri_index.shape != sh_ret:

                raise ValueError(

                    "tri_index array is provided and shall"

                    " have same shape as x and y. Given: "

                    f"{tri_index.shape} and {sh_ret}")

            tri_index = np.ravel(tri_index)



        mask_in = (tri_index != -1)

        if self._tri_renum is None:

            valid_tri_index = tri_index[mask_in]

        else:

            valid_tri_index = self._tri_renum[tri_index[mask_in]]

        valid_x = x_scaled[mask_in]

        valid_y = y_scaled[mask_in]



        ret = []

        for return_key in return_keys:

                                                            

            try:

                return_index = {'z': 0, 'dzdx': 1, 'dzdy': 2}[return_key]

            except KeyError as err:

                raise ValueError("return_keys items shall take values in"

                                 " {'z', 'dzdx', 'dzdy'}") from err



                                                         

            scale = [1., 1./self._unit_x, 1./self._unit_y][return_index]



                                        

            ret_loc = np.empty(size_ret, dtype=np.float64)

            ret_loc[~mask_in] = np.nan

            ret_loc[mask_in] = self._interpolate_single_key(

                return_key, valid_tri_index, valid_x, valid_y) * scale

            ret += [np.ma.masked_invalid(ret_loc.reshape(sh_ret), copy=False)]



        return ret



    def _interpolate_single_key(self, return_key, tri_index, x, y):

        

        raise NotImplementedError("TriInterpolator subclasses" +

                                  "should implement _interpolate_single_key!")





class LinearTriInterpolator(TriInterpolator):

    

    def __init__(self, triangulation, z, trifinder=None):

        super().__init__(triangulation, z, trifinder)



                                                                       

        self._plane_coefficients =
            self._triangulation.calculate_plane_coefficients(self._z)



    def __call__(self, x, y):

        return self._interpolate_multikeys(x, y, tri_index=None,

                                           return_keys=('z',))[0]

    __call__.__doc__ = TriInterpolator._docstring__call__



    def gradient(self, x, y):

        return self._interpolate_multikeys(x, y, tri_index=None,

                                           return_keys=('dzdx', 'dzdy'))

    gradient.__doc__ = TriInterpolator._docstringgradient



    def _interpolate_single_key(self, return_key, tri_index, x, y):

        _api.check_in_list(['z', 'dzdx', 'dzdy'], return_key=return_key)

        if return_key == 'z':

            return (self._plane_coefficients[tri_index, 0]*x +

                    self._plane_coefficients[tri_index, 1]*y +

                    self._plane_coefficients[tri_index, 2])

        elif return_key == 'dzdx':

            return self._plane_coefficients[tri_index, 0]

        else:          

            return self._plane_coefficients[tri_index, 1]





class CubicTriInterpolator(TriInterpolator):

    

    def __init__(self, triangulation, z, kind='min_E', trifinder=None,

                 dz=None):

        super().__init__(triangulation, z, trifinder)



                                                  

                                                                              

                                                          

        self._triangulation.get_cpp_triangulation()



                                                                            

                                                                          

                                                  

                                                              

                                                                           

                                                                         

                                                                            

                                   

        tri_analyzer = TriAnalyzer(self._triangulation)

        (compressed_triangles, compressed_x, compressed_y, tri_renum,

         node_renum) = tri_analyzer._get_compressed_triangulation()

        self._triangles = compressed_triangles

        self._tri_renum = tri_renum

                                                              

        valid_node = (node_renum != -1)

        self._z[node_renum[valid_node]] = self._z[valid_node]



                                 

        self._unit_x = np.ptp(compressed_x)

        self._unit_y = np.ptp(compressed_y)

        self._pts = np.column_stack([compressed_x / self._unit_x,

                                     compressed_y / self._unit_y])

                                   

        self._tris_pts = self._pts[self._triangles]

                                  

        self._eccs = self._compute_tri_eccentricities(self._tris_pts)

                                                                   

        _api.check_in_list(['user', 'geom', 'min_E'], kind=kind)

        self._dof = self._compute_dof(kind, dz=dz)

                             

        self._ReferenceElement = _ReducedHCT_Element()



    def __call__(self, x, y):

        return self._interpolate_multikeys(x, y, tri_index=None,

                                           return_keys=('z',))[0]

    __call__.__doc__ = TriInterpolator._docstring__call__



    def gradient(self, x, y):

        return self._interpolate_multikeys(x, y, tri_index=None,

                                           return_keys=('dzdx', 'dzdy'))

    gradient.__doc__ = TriInterpolator._docstringgradient



    def _interpolate_single_key(self, return_key, tri_index, x, y):

        _api.check_in_list(['z', 'dzdx', 'dzdy'], return_key=return_key)

        tris_pts = self._tris_pts[tri_index]

        alpha = self._get_alpha_vec(x, y, tris_pts)

        ecc = self._eccs[tri_index]

        dof = np.expand_dims(self._dof[tri_index], axis=1)

        if return_key == 'z':

            return self._ReferenceElement.get_function_values(

                alpha, ecc, dof)

        else:                  

            J = self._get_jacobian(tris_pts)

            dzdx = self._ReferenceElement.get_function_derivatives(

                alpha, J, ecc, dof)

            if return_key == 'dzdx':

                return dzdx[:, 0, 0]

            else:

                return dzdx[:, 1, 0]



    def _compute_dof(self, kind, dz=None):

        

        if kind == 'user':

            if dz is None:

                raise ValueError("For a CubicTriInterpolator with "

                                 "*kind*='user', a valid *dz* "

                                 "argument is expected.")

            TE = _DOF_estimator_user(self, dz=dz)

        elif kind == 'geom':

            TE = _DOF_estimator_geom(self)

        else:                                

            TE = _DOF_estimator_min_E(self)

        return TE.compute_dof_from_df()



    @staticmethod

    def _get_alpha_vec(x, y, tris_pts):

        

        ndim = tris_pts.ndim-2



        a = tris_pts[:, 1, :] - tris_pts[:, 0, :]

        b = tris_pts[:, 2, :] - tris_pts[:, 0, :]

        abT = np.stack([a, b], axis=-1)

        ab = _transpose_vectorized(abT)

        OM = np.stack([x, y], axis=1) - tris_pts[:, 0, :]



        metric = ab @ abT

                                                      

                                                                            

                                                                      

                      

        metric_inv = _pseudo_inv22sym_vectorized(metric)

        Covar = ab @ _transpose_vectorized(np.expand_dims(OM, ndim))

        ksi = metric_inv @ Covar

        alpha = _to_matrix_vectorized([

            [1-ksi[:, 0, 0]-ksi[:, 1, 0]], [ksi[:, 0, 0]], [ksi[:, 1, 0]]])

        return alpha



    @staticmethod

    def _get_jacobian(tris_pts):

        

        a = np.array(tris_pts[:, 1, :] - tris_pts[:, 0, :])

        b = np.array(tris_pts[:, 2, :] - tris_pts[:, 0, :])

        J = _to_matrix_vectorized([[a[:, 0], a[:, 1]],

                                   [b[:, 0], b[:, 1]]])

        return J



    @staticmethod

    def _compute_tri_eccentricities(tris_pts):

        

        a = np.expand_dims(tris_pts[:, 2, :] - tris_pts[:, 1, :], axis=2)

        b = np.expand_dims(tris_pts[:, 0, :] - tris_pts[:, 2, :], axis=2)

        c = np.expand_dims(tris_pts[:, 1, :] - tris_pts[:, 0, :], axis=2)

                                                                       

                                 

        dot_a = (_transpose_vectorized(a) @ a)[:, 0, 0]

        dot_b = (_transpose_vectorized(b) @ b)[:, 0, 0]

        dot_c = (_transpose_vectorized(c) @ c)[:, 0, 0]

                                                                            

                                                                              

        return _to_matrix_vectorized([[(dot_c-dot_b) / dot_a],

                                      [(dot_a-dot_c) / dot_b],

                                      [(dot_b-dot_a) / dot_c]])





                                                                 

                               

class _ReducedHCT_Element:

    

                                                                    

                                                        

    M = np.array([

        [ 0.00, 0.00, 0.00,  4.50,  4.50, 0.00, 0.00, 0.00, 0.00, 0.00],

        [-0.25, 0.00, 0.00,  0.50,  1.25, 0.00, 0.00, 0.00, 0.00, 0.00],

        [-0.25, 0.00, 0.00,  1.25,  0.50, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.50, 1.00, 0.00, -1.50,  0.00, 3.00, 3.00, 0.00, 0.00, 3.00],

        [ 0.00, 0.00, 0.00, -0.25,  0.25, 0.00, 1.00, 0.00, 0.00, 0.50],

        [ 0.25, 0.00, 0.00, -0.50, -0.25, 1.00, 0.00, 0.00, 0.00, 1.00],

        [ 0.50, 0.00, 1.00,  0.00, -1.50, 0.00, 0.00, 3.00, 3.00, 3.00],

        [ 0.25, 0.00, 0.00, -0.25, -0.50, 0.00, 0.00, 0.00, 1.00, 1.00],

        [ 0.00, 0.00, 0.00,  0.25, -0.25, 0.00, 0.00, 1.00, 0.00, 0.50]])

    M0 = np.array([

        [ 0.00, 0.00, 0.00,  0.00,  0.00, 0.00, 0.00, 0.00, 0.00,  0.00],

        [ 0.00, 0.00, 0.00,  0.00,  0.00, 0.00, 0.00, 0.00, 0.00,  0.00],

        [ 0.00, 0.00, 0.00,  0.00,  0.00, 0.00, 0.00, 0.00, 0.00,  0.00],

        [-1.00, 0.00, 0.00,  1.50,  1.50, 0.00, 0.00, 0.00, 0.00, -3.00],

        [-0.50, 0.00, 0.00,  0.75,  0.75, 0.00, 0.00, 0.00, 0.00, -1.50],

        [ 0.00, 0.00, 0.00,  0.00,  0.00, 0.00, 0.00, 0.00, 0.00,  0.00],

        [ 1.00, 0.00, 0.00, -1.50, -1.50, 0.00, 0.00, 0.00, 0.00,  3.00],

        [ 0.00, 0.00, 0.00,  0.00,  0.00, 0.00, 0.00, 0.00, 0.00,  0.00],

        [ 0.50, 0.00, 0.00, -0.75, -0.75, 0.00, 0.00, 0.00, 0.00,  1.50]])

    M1 = np.array([

        [-0.50, 0.00, 0.00,  1.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [-0.25, 0.00, 0.00,  0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.50, 0.00, 0.00, -1.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.25, 0.00, 0.00, -0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]])

    M2 = np.array([

        [ 0.50, 0.00, 0.00, 0.00, -1.50, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.25, 0.00, 0.00, 0.00, -0.75, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [-0.50, 0.00, 0.00, 0.00,  1.50, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [-0.25, 0.00, 0.00, 0.00,  0.75, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00],

        [ 0.00, 0.00, 0.00, 0.00,  0.00, 0.00, 0.00, 0.00, 0.00, 0.00]])



                                                                  

                                                                   

    rotate_dV = np.array([[ 1.,  0.], [ 0.,  1.],

                          [ 0.,  1.], [-1., -1.],

                          [-1., -1.], [ 1.,  0.]])



    rotate_d2V = np.array([[1., 0., 0.], [0., 1., 0.], [ 0.,  0.,  1.],

                           [0., 1., 0.], [1., 1., 1.], [ 0., -2., -1.],

                           [1., 1., 1.], [1., 0., 0.], [-2.,  0., -1.]])



                                                                    

                                                        

                                                                           

             

    n_gauss = 9

    gauss_pts = np.array([[13./18.,  4./18.,  1./18.],

                          [ 4./18., 13./18.,  1./18.],

                          [ 7./18.,  7./18.,  4./18.],

                          [ 1./18., 13./18.,  4./18.],

                          [ 1./18.,  4./18., 13./18.],

                          [ 4./18.,  7./18.,  7./18.],

                          [ 4./18.,  1./18., 13./18.],

                          [13./18.,  1./18.,  4./18.],

                          [ 7./18.,  4./18.,  7./18.]], dtype=np.float64)

    gauss_w = np.ones([9], dtype=np.float64) / 9.



                                               

    E = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 2.]])



                                                                  

    J0_to_J1 = np.array([[-1.,  1.], [-1.,  0.]])

    J0_to_J2 = np.array([[ 0., -1.], [ 1., -1.]])



    def get_function_values(self, alpha, ecc, dofs):

        

        subtri = np.argmin(alpha, axis=1)[:, 0]

        ksi = _roll_vectorized(alpha, -subtri, axis=0)

        E = _roll_vectorized(ecc, -subtri, axis=0)

        x = ksi[:, 0, 0]

        y = ksi[:, 1, 0]

        z = ksi[:, 2, 0]

        x_sq = x*x

        y_sq = y*y

        z_sq = z*z

        V = _to_matrix_vectorized([

            [x_sq*x], [y_sq*y], [z_sq*z], [x_sq*z], [x_sq*y], [y_sq*x],

            [y_sq*z], [z_sq*y], [z_sq*x], [x*y*z]])

        prod = self.M @ V

        prod += _scalar_vectorized(E[:, 0, 0], self.M0 @ V)

        prod += _scalar_vectorized(E[:, 1, 0], self.M1 @ V)

        prod += _scalar_vectorized(E[:, 2, 0], self.M2 @ V)

        s = _roll_vectorized(prod, 3*subtri, axis=0)

        return (dofs @ s)[:, 0, 0]



    def get_function_derivatives(self, alpha, J, ecc, dofs):

        

        subtri = np.argmin(alpha, axis=1)[:, 0]

        ksi = _roll_vectorized(alpha, -subtri, axis=0)

        E = _roll_vectorized(ecc, -subtri, axis=0)

        x = ksi[:, 0, 0]

        y = ksi[:, 1, 0]

        z = ksi[:, 2, 0]

        x_sq = x*x

        y_sq = y*y

        z_sq = z*z

        dV = _to_matrix_vectorized([

            [    -3.*x_sq,     -3.*x_sq],

            [     3.*y_sq,           0.],

            [          0.,      3.*z_sq],

            [     -2.*x*z, -2.*x*z+x_sq],

            [-2.*x*y+x_sq,      -2.*x*y],

            [ 2.*x*y-y_sq,        -y_sq],

            [      2.*y*z,         y_sq],

            [        z_sq,       2.*y*z],

            [       -z_sq,  2.*x*z-z_sq],

            [     x*z-y*z,      x*y-y*z]])

                                          

        dV = dV @ _extract_submatrices(

            self.rotate_dV, subtri, block_size=2, axis=0)



        prod = self.M @ dV

        prod += _scalar_vectorized(E[:, 0, 0], self.M0 @ dV)

        prod += _scalar_vectorized(E[:, 1, 0], self.M1 @ dV)

        prod += _scalar_vectorized(E[:, 2, 0], self.M2 @ dV)

        dsdksi = _roll_vectorized(prod, 3*subtri, axis=0)

        dfdksi = dofs @ dsdksi

                                

                                                                           

                      

        J_inv = _safe_inv22_vectorized(J)

        dfdx = J_inv @ _transpose_vectorized(dfdksi)

        return dfdx



    def get_function_hessians(self, alpha, J, ecc, dofs):

        

        d2sdksi2 = self.get_d2Sidksij2(alpha, ecc)

        d2fdksi2 = dofs @ d2sdksi2

        H_rot = self.get_Hrot_from_J(J)

        d2fdx2 = d2fdksi2 @ H_rot

        return _transpose_vectorized(d2fdx2)



    def get_d2Sidksij2(self, alpha, ecc):

        

        subtri = np.argmin(alpha, axis=1)[:, 0]

        ksi = _roll_vectorized(alpha, -subtri, axis=0)

        E = _roll_vectorized(ecc, -subtri, axis=0)

        x = ksi[:, 0, 0]

        y = ksi[:, 1, 0]

        z = ksi[:, 2, 0]

        d2V = _to_matrix_vectorized([

            [     6.*x,      6.*x,      6.*x],

            [     6.*y,        0.,        0.],

            [       0.,      6.*z,        0.],

            [     2.*z, 2.*z-4.*x, 2.*z-2.*x],

            [2.*y-4.*x,      2.*y, 2.*y-2.*x],

            [2.*x-4.*y,        0.,     -2.*y],

            [     2.*z,        0.,      2.*y],

            [       0.,      2.*y,      2.*z],

            [       0., 2.*x-4.*z,     -2.*z],

            [    -2.*z,     -2.*y,     x-y-z]])

                                           

        d2V = d2V @ _extract_submatrices(

            self.rotate_d2V, subtri, block_size=3, axis=0)

        prod = self.M @ d2V

        prod += _scalar_vectorized(E[:, 0, 0], self.M0 @ d2V)

        prod += _scalar_vectorized(E[:, 1, 0], self.M1 @ d2V)

        prod += _scalar_vectorized(E[:, 2, 0], self.M2 @ d2V)

        d2sdksi2 = _roll_vectorized(prod, 3*subtri, axis=0)

        return d2sdksi2



    def get_bending_matrices(self, J, ecc):

        

        n = np.size(ecc, 0)



                                                        

        J1 = self.J0_to_J1 @ J

        J2 = self.J0_to_J2 @ J

        DOF_rot = np.zeros([n, 9, 9], dtype=np.float64)

        DOF_rot[:, 0, 0] = 1

        DOF_rot[:, 3, 3] = 1

        DOF_rot[:, 6, 6] = 1

        DOF_rot[:, 1:3, 1:3] = J

        DOF_rot[:, 4:6, 4:6] = J1

        DOF_rot[:, 7:9, 7:9] = J2



                                                            

        H_rot, area = self.get_Hrot_from_J(J, return_area=True)



                                      

                           

        K = np.zeros([n, 9, 9], dtype=np.float64)

        weights = self.gauss_w

        pts = self.gauss_pts

        for igauss in range(self.n_gauss):

            alpha = np.tile(pts[igauss, :], n).reshape(n, 3)

            alpha = np.expand_dims(alpha, 2)

            weight = weights[igauss]

            d2Skdksi2 = self.get_d2Sidksij2(alpha, ecc)

            d2Skdx2 = d2Skdksi2 @ H_rot

            K += weight * (d2Skdx2 @ self.E @ _transpose_vectorized(d2Skdx2))



                                       

        K = _transpose_vectorized(DOF_rot) @ K @ DOF_rot



                                                          

        return _scalar_vectorized(area, K)



    def get_Hrot_from_J(self, J, return_area=False):

        

                                                                      

                                     

        J_inv = _safe_inv22_vectorized(J)

        Ji00 = J_inv[:, 0, 0]

        Ji11 = J_inv[:, 1, 1]

        Ji10 = J_inv[:, 1, 0]

        Ji01 = J_inv[:, 0, 1]

        H_rot = _to_matrix_vectorized([

            [Ji00*Ji00, Ji10*Ji10, Ji00*Ji10],

            [Ji01*Ji01, Ji11*Ji11, Ji01*Ji11],

            [2*Ji00*Ji01, 2*Ji11*Ji10, Ji00*Ji11+Ji10*Ji01]])

        if not return_area:

            return H_rot

        else:

            area = 0.5 * (J[:, 0, 0]*J[:, 1, 1] - J[:, 0, 1]*J[:, 1, 0])

            return H_rot, area



    def get_Kff_and_Ff(self, J, ecc, triangles, Uc):

        

        ntri = np.size(ecc, 0)

        vec_range = np.arange(ntri, dtype=np.int32)

        c_indices = np.full(ntri, -1, dtype=np.int32)                       

        f_dof = [1, 2, 4, 5, 7, 8]

        c_dof = [0, 3, 6]



                                                             

        f_dof_indices = _to_matrix_vectorized([[

            c_indices, triangles[:, 0]*2, triangles[:, 0]*2+1,

            c_indices, triangles[:, 1]*2, triangles[:, 1]*2+1,

            c_indices, triangles[:, 2]*2, triangles[:, 2]*2+1]])



        expand_indices = np.ones([ntri, 9, 1], dtype=np.int32)

        f_row_indices = _transpose_vectorized(expand_indices @ f_dof_indices)

        f_col_indices = expand_indices @ f_dof_indices

        K_elem = self.get_bending_matrices(J, ecc)



                                 

                                  

                                                                             

                                                                          

                                  

                                            

                                                  

                            

                                                               

                            

                                                                    



                                                             

        Kff_vals = np.ravel(K_elem[np.ix_(vec_range, f_dof, f_dof)])

        Kff_rows = np.ravel(f_row_indices[np.ix_(vec_range, f_dof, f_dof)])

        Kff_cols = np.ravel(f_col_indices[np.ix_(vec_range, f_dof, f_dof)])



                                                        

        Kfc_elem = K_elem[np.ix_(vec_range, f_dof, c_dof)]

        Uc_elem = np.expand_dims(Uc, axis=2)

        Ff_elem = -(Kfc_elem @ Uc_elem)[:, :, 0]

        Ff_indices = f_dof_indices[np.ix_(vec_range, [0], f_dof)][:, 0, :]



                                                    

                                                            

        Ff = np.bincount(np.ravel(Ff_indices), weights=np.ravel(Ff_elem))

        return Kff_rows, Kff_cols, Kff_vals, Ff





                                                                  

                      

                                                                          

                                       

class _DOF_estimator:

    

    def __init__(self, interpolator, **kwargs):

        _api.check_isinstance(CubicTriInterpolator, interpolator=interpolator)

        self._pts = interpolator._pts

        self._tris_pts = interpolator._tris_pts

        self.z = interpolator._z

        self._triangles = interpolator._triangles

        (self._unit_x, self._unit_y) = (interpolator._unit_x,

                                        interpolator._unit_y)

        self.dz = self.compute_dz(**kwargs)

        self.compute_dof_from_df()



    def compute_dz(self, **kwargs):

        raise NotImplementedError



    def compute_dof_from_df(self):

        

        J = CubicTriInterpolator._get_jacobian(self._tris_pts)

        tri_z = self.z[self._triangles]

        tri_dz = self.dz[self._triangles]

        tri_dof = self.get_dof_vec(tri_z, tri_dz, J)

        return tri_dof



    @staticmethod

    def get_dof_vec(tri_z, tri_dz, J):

        

        npt = tri_z.shape[0]

        dof = np.zeros([npt, 9], dtype=np.float64)

        J1 = _ReducedHCT_Element.J0_to_J1 @ J

        J2 = _ReducedHCT_Element.J0_to_J2 @ J



        col0 = J @ np.expand_dims(tri_dz[:, 0, :], axis=2)

        col1 = J1 @ np.expand_dims(tri_dz[:, 1, :], axis=2)

        col2 = J2 @ np.expand_dims(tri_dz[:, 2, :], axis=2)



        dfdksi = _to_matrix_vectorized([

            [col0[:, 0, 0], col1[:, 0, 0], col2[:, 0, 0]],

            [col0[:, 1, 0], col1[:, 1, 0], col2[:, 1, 0]]])

        dof[:, 0:7:3] = tri_z

        dof[:, 1:8:3] = dfdksi[:, 0]

        dof[:, 2:9:3] = dfdksi[:, 1]

        return dof





class _DOF_estimator_user(_DOF_estimator):

    



    def compute_dz(self, dz):

        (dzdx, dzdy) = dz

        dzdx = dzdx * self._unit_x

        dzdy = dzdy * self._unit_y

        return np.vstack([dzdx, dzdy]).T





class _DOF_estimator_geom(_DOF_estimator):

    



    def compute_dz(self):

        

        el_geom_w = self.compute_geom_weights()

        el_geom_grad = self.compute_geom_grads()



                               

        w_node_sum = np.bincount(np.ravel(self._triangles),

                                 weights=np.ravel(el_geom_w))



                                         

        dfx_el_w = np.empty_like(el_geom_w)

        dfy_el_w = np.empty_like(el_geom_w)

        for iapex in range(3):

            dfx_el_w[:, iapex] = el_geom_w[:, iapex]*el_geom_grad[:, 0]

            dfy_el_w[:, iapex] = el_geom_w[:, iapex]*el_geom_grad[:, 1]

        dfx_node_sum = np.bincount(np.ravel(self._triangles),

                                   weights=np.ravel(dfx_el_w))

        dfy_node_sum = np.bincount(np.ravel(self._triangles),

                                   weights=np.ravel(dfy_el_w))



                          

        dfx_estim = dfx_node_sum/w_node_sum

        dfy_estim = dfy_node_sum/w_node_sum

        return np.vstack([dfx_estim, dfy_estim]).T



    def compute_geom_weights(self):

        

        weights = np.zeros([np.size(self._triangles, 0), 3])

        tris_pts = self._tris_pts

        for ipt in range(3):

            p0 = tris_pts[:, ipt % 3, :]

            p1 = tris_pts[:, (ipt+1) % 3, :]

            p2 = tris_pts[:, (ipt-1) % 3, :]

            alpha1 = np.arctan2(p1[:, 1]-p0[:, 1], p1[:, 0]-p0[:, 0])

            alpha2 = np.arctan2(p2[:, 1]-p0[:, 1], p2[:, 0]-p0[:, 0])

                                                              

                                                                             

            angle = np.abs(((alpha2-alpha1) / np.pi) % 1)

                                                                      

                                                                            

                        

            weights[:, ipt] = 0.5 - np.abs(angle-0.5)

        return weights



    def compute_geom_grads(self):

        

        tris_pts = self._tris_pts

        tris_f = self.z[self._triangles]



        dM1 = tris_pts[:, 1, :] - tris_pts[:, 0, :]

        dM2 = tris_pts[:, 2, :] - tris_pts[:, 0, :]

        dM = np.dstack([dM1, dM2])

                                                                      

                                           

        dM_inv = _safe_inv22_vectorized(dM)



        dZ1 = tris_f[:, 1] - tris_f[:, 0]

        dZ2 = tris_f[:, 2] - tris_f[:, 0]

        dZ = np.vstack([dZ1, dZ2]).T

        df = np.empty_like(dZ)



                                               

        df[:, 0] = dZ[:, 0]*dM_inv[:, 0, 0] + dZ[:, 1]*dM_inv[:, 1, 0]

        df[:, 1] = dZ[:, 0]*dM_inv[:, 0, 1] + dZ[:, 1]*dM_inv[:, 1, 1]

        return df





class _DOF_estimator_min_E(_DOF_estimator_geom):

    

    def __init__(self, Interpolator):

        self._eccs = Interpolator._eccs

        super().__init__(Interpolator)



    def compute_dz(self):

        

                                                 

        dz_init = super().compute_dz()

        Uf0 = np.ravel(dz_init)



        reference_element = _ReducedHCT_Element()

        J = CubicTriInterpolator._get_jacobian(self._tris_pts)

        eccs = self._eccs

        triangles = self._triangles

        Uc = self.z[self._triangles]



                                                                  

        Kff_rows, Kff_cols, Kff_vals, Ff = reference_element.get_Kff_and_Ff(

            J, eccs, triangles, Uc)



                                                                 

                                                                        

                                                                           

                                                                 

        tol = 1.e-10

        n_dof = Ff.shape[0]

        Kff_coo = _Sparse_Matrix_coo(Kff_vals, Kff_rows, Kff_cols,

                                     shape=(n_dof, n_dof))

        Kff_coo.compress_csc()

        Uf, err = _cg(A=Kff_coo, b=Ff, x0=Uf0, tol=tol)

                                                                           

                 

        err0 = np.linalg.norm(Kff_coo.dot(Uf0) - Ff)

        if err0 < err:

                                                             

            _api.warn_external("In TriCubicInterpolator initialization, "

                               "PCG sparse solver did not converge after "

                               "1000 iterations. `geom` approximation is "

                               "used instead of `min_E`")

            Uf = Uf0



                             

        dz = np.empty([self._pts.shape[0], 2], dtype=np.float64)

        dz[:, 0] = Uf[::2]

        dz[:, 1] = Uf[1::2]

        return dz





                                                                       

                                                        

class _Sparse_Matrix_coo:

    def __init__(self, vals, rows, cols, shape):

        

        self.n, self.m = shape

        self.vals = np.asarray(vals, dtype=np.float64)

        self.rows = np.asarray(rows, dtype=np.int32)

        self.cols = np.asarray(cols, dtype=np.int32)



    def dot(self, V):

        

        assert V.shape == (self.m,)

        return np.bincount(self.rows,

                           weights=self.vals*V[self.cols],

                           minlength=self.m)



    def compress_csc(self):

        

        _, unique, indices = np.unique(

            self.rows + self.n*self.cols,

            return_index=True, return_inverse=True)

        self.rows = self.rows[unique]

        self.cols = self.cols[unique]

        self.vals = np.bincount(indices, weights=self.vals)



    def compress_csr(self):

        

        _, unique, indices = np.unique(

            self.m*self.rows + self.cols,

            return_index=True, return_inverse=True)

        self.rows = self.rows[unique]

        self.cols = self.cols[unique]

        self.vals = np.bincount(indices, weights=self.vals)



    def to_dense(self):

        

        ret = np.zeros([self.n, self.m], dtype=np.float64)

        nvals = self.vals.size

        for i in range(nvals):

            ret[self.rows[i], self.cols[i]] += self.vals[i]

        return ret



    def __str__(self):

        return self.to_dense().__str__()



    @property

    def diag(self):

        

        in_diag = (self.rows == self.cols)

        diag = np.zeros(min(self.n, self.n), dtype=np.float64)              

        diag[self.rows[in_diag]] = self.vals[in_diag]

        return diag





def _cg(A, b, x0=None, tol=1.e-10, maxiter=1000):

    

    n = b.size

    assert A.n == n

    assert A.m == n

    b_norm = np.linalg.norm(b)



                            

    kvec = A.diag

                                        

    kvec = np.maximum(kvec, 1e-6)



                   

    if x0 is None:

        x = np.zeros(n)

    else:

        x = x0



    r = b - A.dot(x)

    w = r/kvec



    p = np.zeros(n)

    beta = 0.0

    rho = np.dot(r, w)

    k = 0



                            

    while (np.sqrt(abs(rho)) > tol*b_norm) and (k < maxiter):

        p = w + beta*p

        z = A.dot(p)

        alpha = rho/np.dot(p, z)

        r = r - alpha*z

        w = r/kvec

        rhoold = rho

        rho = np.dot(r, w)

        x = x + alpha*p

        beta = rho/rhoold

                                                                            

        k += 1

    err = np.linalg.norm(A.dot(x) - b)

    return x, err





                                  

                                    

                                         

                                

                                   

                              

                                   

                                  

                                                                            

                                                            



                                                                   

                                                                           

                                                                         

 

        

                                                                          

                                        

                                                                           

                                                                             

                                                    

                                                                      

                                                           

                                                                             

                                                                             

 

               

                                                                        

                                                                  

                                    

 

                 

                                                                            

                                                                          

                                                                      

              

                                                                   

                                                               

                                    

                                                                              

                                                            

                                                                            

                                                                             

                                                                            

                                                                              

                                                                    

def _safe_inv22_vectorized(M):

    

    _api.check_shape((None, 2, 2), M=M)

    M_inv = np.empty_like(M)

    prod1 = M[:, 0, 0]*M[:, 1, 1]

    delta = prod1 - M[:, 0, 1]*M[:, 1, 0]



                                                                  

                                                                          

    rank2 = (np.abs(delta) > 1e-8*np.abs(prod1))

    if np.all(rank2):

                                  

        delta_inv = 1./delta

    else:

                            

        delta_inv = np.zeros(M.shape[0])

        delta_inv[rank2] = 1./delta[rank2]



    M_inv[:, 0, 0] = M[:, 1, 1]*delta_inv

    M_inv[:, 0, 1] = -M[:, 0, 1]*delta_inv

    M_inv[:, 1, 0] = -M[:, 1, 0]*delta_inv

    M_inv[:, 1, 1] = M[:, 0, 0]*delta_inv

    return M_inv





def _pseudo_inv22sym_vectorized(M):

    

    _api.check_shape((None, 2, 2), M=M)

    M_inv = np.empty_like(M)

    prod1 = M[:, 0, 0]*M[:, 1, 1]

    delta = prod1 - M[:, 0, 1]*M[:, 1, 0]

    rank2 = (np.abs(delta) > 1e-8*np.abs(prod1))



    if np.all(rank2):

                                  

        M_inv[:, 0, 0] = M[:, 1, 1] / delta

        M_inv[:, 0, 1] = -M[:, 0, 1] / delta

        M_inv[:, 1, 0] = -M[:, 1, 0] / delta

        M_inv[:, 1, 1] = M[:, 0, 0] / delta

    else:

                            

                                               

                                                

        delta = delta[rank2]

        M_inv[rank2, 0, 0] = M[rank2, 1, 1] / delta

        M_inv[rank2, 0, 1] = -M[rank2, 0, 1] / delta

        M_inv[rank2, 1, 0] = -M[rank2, 1, 0] / delta

        M_inv[rank2, 1, 1] = M[rank2, 0, 0] / delta

                                                                      

        rank01 = ~rank2

        tr = M[rank01, 0, 0] + M[rank01, 1, 1]

        tr_zeros = (np.abs(tr) < 1.e-8)

        sq_tr_inv = (1.-tr_zeros) / (tr**2+tr_zeros)

                                

        M_inv[rank01, 0, 0] = M[rank01, 0, 0] * sq_tr_inv

        M_inv[rank01, 0, 1] = M[rank01, 0, 1] * sq_tr_inv

        M_inv[rank01, 1, 0] = M[rank01, 1, 0] * sq_tr_inv

        M_inv[rank01, 1, 1] = M[rank01, 1, 1] * sq_tr_inv



    return M_inv





def _scalar_vectorized(scalar, M):

    

    return scalar[:, np.newaxis, np.newaxis]*M





def _transpose_vectorized(M):

    

    return np.transpose(M, [0, 2, 1])





def _roll_vectorized(M, roll_indices, axis):

    

    assert axis in [0, 1]

    ndim = M.ndim

    assert ndim == 3

    ndim_roll = roll_indices.ndim

    assert ndim_roll == 1

    sh = M.shape

    r, c = sh[-2:]

    assert sh[0] == roll_indices.shape[0]

    vec_indices = np.arange(sh[0], dtype=np.int32)



                              

    M_roll = np.empty_like(M)

    if axis == 0:

        for ir in range(r):

            for ic in range(c):

                M_roll[:, ir, ic] = M[vec_indices, (-roll_indices+ir) % r, ic]

    else:     

        for ir in range(r):

            for ic in range(c):

                M_roll[:, ir, ic] = M[vec_indices, ir, (-roll_indices+ic) % c]

    return M_roll





def _to_matrix_vectorized(M):

    

    assert isinstance(M, (tuple, list))

    assert all(isinstance(item, (tuple, list)) for item in M)

    c_vec = np.asarray([len(item) for item in M])

    assert np.all(c_vec-c_vec[0] == 0)

    r = len(M)

    c = c_vec[0]

    M00 = np.asarray(M[0][0])

    dt = M00.dtype

    sh = [M00.shape[0], r, c]

    M_ret = np.empty(sh, dtype=dt)

    for irow in range(r):

        for icol in range(c):

            M_ret[:, irow, icol] = np.asarray(M[irow][icol])

    return M_ret





def _extract_submatrices(M, block_indices, block_size, axis):

    

    assert block_indices.ndim == 1

    assert axis in [0, 1]



    r, c = M.shape

    if axis == 0:

        sh = [block_indices.shape[0], block_size, c]

    else:     

        sh = [block_indices.shape[0], r, block_size]



    dt = M.dtype

    M_res = np.empty(sh, dtype=dt)

    if axis == 0:

        for ir in range(block_size):

            M_res[:, ir, :] = M[(block_indices*block_size+ir), :]

    else:     

        for ic in range(block_size):

            M_res[:, :, ic] = M[:, (block_indices*block_size+ic)]



    return M_res


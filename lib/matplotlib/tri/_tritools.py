



import numpy as np



from matplotlib import _api

from matplotlib.tri import Triangulation





class TriAnalyzer:

    



    def __init__(self, triangulation):

        _api.check_isinstance(Triangulation, triangulation=triangulation)

        self._triangulation = triangulation



    @property

    def scale_factors(self):

        

        compressed_triangles = self._triangulation.get_masked_triangles()

        node_used = (np.bincount(np.ravel(compressed_triangles),

                                 minlength=self._triangulation.x.size) != 0)

        return (1 / np.ptp(self._triangulation.x[node_used]),

                1 / np.ptp(self._triangulation.y[node_used]))



    def circle_ratios(self, rescale=True):

        

                          

        if rescale:

            (kx, ky) = self.scale_factors

        else:

            (kx, ky) = (1.0, 1.0)

        pts = np.vstack([self._triangulation.x*kx,

                         self._triangulation.y*ky]).T

        tri_pts = pts[self._triangulation.triangles]

                                     

        a = tri_pts[:, 1, :] - tri_pts[:, 0, :]

        b = tri_pts[:, 2, :] - tri_pts[:, 1, :]

        c = tri_pts[:, 0, :] - tri_pts[:, 2, :]

        a = np.hypot(a[:, 0], a[:, 1])

        b = np.hypot(b[:, 0], b[:, 1])

        c = np.hypot(c[:, 0], c[:, 1])

                                         

        s = (a+b+c)*0.5

        prod = s*(a+b-s)*(a+c-s)*(b+c-s)

                                                                         

        bool_flat = (prod == 0.)

        if np.any(bool_flat):

                             

            ntri = tri_pts.shape[0]

            circum_radius = np.empty(ntri, dtype=np.float64)

            circum_radius[bool_flat] = np.inf

            abc = a*b*c

            circum_radius[~bool_flat] = abc[~bool_flat] / (

                4.0*np.sqrt(prod[~bool_flat]))

        else:

                                   

            circum_radius = (a*b*c) / (4.0*np.sqrt(prod))

        in_radius = (a*b*c) / (4.0*circum_radius*s)

        circle_ratio = in_radius/circum_radius

        mask = self._triangulation.mask

        if mask is None:

            return circle_ratio

        else:

            return np.ma.array(circle_ratio, mask=mask)



    def get_flat_tri_mask(self, min_circle_ratio=0.01, rescale=True):

        

                                                                              

                                                                             

                                                

        ntri = self._triangulation.triangles.shape[0]

        mask_bad_ratio = self.circle_ratios(rescale) < min_circle_ratio



        current_mask = self._triangulation.mask

        if current_mask is None:

            current_mask = np.zeros(ntri, dtype=bool)

        valid_neighbors = np.copy(self._triangulation.neighbors)

        renum_neighbors = np.arange(ntri, dtype=np.int32)

        nadd = -1

        while nadd != 0:

                                                                             

                                                     

            wavefront = (np.min(valid_neighbors, axis=1) == -1) & ~current_mask

                                                                           

                                  

            added_mask = wavefront & mask_bad_ratio

            current_mask = added_mask | current_mask

            nadd = np.sum(added_mask)



                                                              

            valid_neighbors[added_mask, :] = -1

            renum_neighbors[added_mask] = -1

            valid_neighbors = np.where(valid_neighbors == -1, -1,

                                       renum_neighbors[valid_neighbors])



        return np.ma.filled(current_mask, True)



    def _get_compressed_triangulation(self):

        

                                         

        tri_mask = self._triangulation.mask

        compressed_triangles = self._triangulation.get_masked_triangles()

        ntri = self._triangulation.triangles.shape[0]

        if tri_mask is not None:

            tri_renum = self._total_to_compress_renum(~tri_mask)

        else:

            tri_renum = np.arange(ntri, dtype=np.int32)



                                     

        valid_node = (np.bincount(np.ravel(compressed_triangles),

                                  minlength=self._triangulation.x.size) != 0)

        compressed_x = self._triangulation.x[valid_node]

        compressed_y = self._triangulation.y[valid_node]

        node_renum = self._total_to_compress_renum(valid_node)



                                                   

        compressed_triangles = node_renum[compressed_triangles]



        return (compressed_triangles, compressed_x, compressed_y, tri_renum,

                node_renum)



    @staticmethod

    def _total_to_compress_renum(valid):

        

        renum = np.full(np.size(valid), -1, dtype=np.int32)

        n_valid = np.sum(valid)

        renum[valid] = np.arange(n_valid, dtype=np.int32)

        return renum


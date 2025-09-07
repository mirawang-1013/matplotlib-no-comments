



import logging

from types import SimpleNamespace



import numpy as np



import matplotlib as mpl

from matplotlib.path import Path

from matplotlib.patches import PathPatch

from matplotlib.transforms import Affine2D

from matplotlib import _docstring



_log = logging.getLogger(__name__)



__author__ = "Kevin L. Davies"

__credits__ = ["Yannick Copin"]

__license__ = "BSD"

__version__ = "2011/09/16"



                 

RIGHT = 0

UP = 1

          

DOWN = 3





class Sankey:

    



    def __init__(self, ax=None, scale=1.0, unit='', format='%G', gap=0.25,

                 radius=0.1, shoulder=0.03, offset=0.15, head_angle=100,

                 margin=0.4, tolerance=1e-6, **kwargs):

        

                              

        if gap < 0:

            raise ValueError(

                "'gap' is negative, which is not allowed because it would "

                "cause the paths to overlap")

        if radius > gap:

            raise ValueError(

                "'radius' is greater than 'gap', which is not allowed because "

                "it would cause the paths to overlap")

        if head_angle < 0:

            raise ValueError(

                "'head_angle' is negative, which is not allowed because it "

                "would cause inputs to look like outputs and vice versa")

        if tolerance < 0:

            raise ValueError(

                "'tolerance' is negative, but it must be a magnitude")



                                   

        if ax is None:

            import matplotlib.pyplot as plt

            fig = plt.figure()

            ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[])



        self.diagrams = []



                           

        self.ax = ax

        self.unit = unit

        self.format = format

        self.scale = scale

        self.gap = gap

        self.radius = radius

        self.shoulder = shoulder

        self.offset = offset

        self.margin = margin

        self.pitch = np.tan(np.pi * (1 - head_angle / 180.0) / 2.0)

        self.tolerance = tolerance



                                                                     

        self.extent = np.array((np.inf, -np.inf, np.inf, -np.inf))



                                                               

        if len(kwargs):

            self.add(**kwargs)



    def _arc(self, quadrant=0, cw=True, radius=1, center=(0, 0)):

        

                                                                               

                                                                          

                                                                   

        ARC_CODES = [Path.LINETO,

                     Path.CURVE4,

                     Path.CURVE4,

                     Path.CURVE4,

                     Path.CURVE4,

                     Path.CURVE4,

                     Path.CURVE4]

                                                                     

                                                     

        ARC_VERTICES = np.array([[1.00000000e+00, 0.00000000e+00],

                                 [1.00000000e+00, 2.65114773e-01],

                                 [8.94571235e-01, 5.19642327e-01],

                                 [7.07106781e-01, 7.07106781e-01],

                                 [5.19642327e-01, 8.94571235e-01],

                                 [2.65114773e-01, 1.00000000e+00],

                                                

                                                                     

                                 [0.00000000e+00, 1.00000000e+00]])

        if quadrant in (0, 2):

            if cw:

                vertices = ARC_VERTICES

            else:

                vertices = ARC_VERTICES[:, ::-1]                 

        else:        

                       

            if cw:

                               

                vertices = np.column_stack((-ARC_VERTICES[:, 1],

                                             ARC_VERTICES[:, 0]))

            else:

                vertices = np.column_stack((-ARC_VERTICES[:, 0],

                                             ARC_VERTICES[:, 1]))

        if quadrant > 1:

            radius = -radius                   

        return list(zip(ARC_CODES, radius * vertices +

                        np.tile(center, (ARC_VERTICES.shape[0], 1))))



    def _add_input(self, path, angle, flow, length):

        

        if angle is None:

            return [0, 0], [0, 0]

        else:

            x, y = path[-1][1]                                      

            dipdepth = (flow / 2) * self.pitch

            if angle == RIGHT:

                x -= length

                dip = [x + dipdepth, y + flow / 2.0]

                path.extend([(Path.LINETO, [x, y]),

                             (Path.LINETO, dip),

                             (Path.LINETO, [x, y + flow]),

                             (Path.LINETO, [x + self.gap, y + flow])])

                label_location = [dip[0] - self.offset, dip[1]]

            else:            

                x -= self.gap

                if angle == UP:

                    sign = 1

                else:

                    sign = -1



                dip = [x - flow / 2, y - sign * (length - dipdepth)]

                if angle == DOWN:

                    quadrant = 2

                else:

                    quadrant = 1



                                                                

                if self.radius:

                    path.extend(self._arc(quadrant=quadrant,

                                          cw=angle == UP,

                                          radius=self.radius,

                                          center=(x + self.radius,

                                                  y - sign * self.radius)))

                else:

                    path.append((Path.LINETO, [x, y]))

                path.extend([(Path.LINETO, [x, y - sign * length]),

                             (Path.LINETO, dip),

                             (Path.LINETO, [x - flow, y - sign * length])])

                path.extend(self._arc(quadrant=quadrant,

                                      cw=angle == DOWN,

                                      radius=flow + self.radius,

                                      center=(x + self.radius,

                                              y - sign * self.radius)))

                path.append((Path.LINETO, [x - flow, y + sign * flow]))

                label_location = [dip[0], dip[1] - sign * self.offset]



            return dip, label_location



    def _add_output(self, path, angle, flow, length):

        

        if angle is None:

            return [0, 0], [0, 0]

        else:

            x, y = path[-1][1]                                      

            tipheight = (self.shoulder - flow / 2) * self.pitch

            if angle == RIGHT:

                x += length

                tip = [x + tipheight, y + flow / 2.0]

                path.extend([(Path.LINETO, [x, y]),

                             (Path.LINETO, [x, y + self.shoulder]),

                             (Path.LINETO, tip),

                             (Path.LINETO, [x, y - self.shoulder + flow]),

                             (Path.LINETO, [x, y + flow]),

                             (Path.LINETO, [x - self.gap, y + flow])])

                label_location = [tip[0] + self.offset, tip[1]]

            else:            

                x += self.gap

                if angle == UP:

                    sign, quadrant = 1, 3

                else:

                    sign, quadrant = -1, 0



                tip = [x - flow / 2.0, y + sign * (length + tipheight)]

                                                                

                if self.radius:

                    path.extend(self._arc(quadrant=quadrant,

                                          cw=angle == UP,

                                          radius=self.radius,

                                          center=(x - self.radius,

                                                  y + sign * self.radius)))

                else:

                    path.append((Path.LINETO, [x, y]))

                path.extend([(Path.LINETO, [x, y + sign * length]),

                             (Path.LINETO, [x - self.shoulder,

                                            y + sign * length]),

                             (Path.LINETO, tip),

                             (Path.LINETO, [x + self.shoulder - flow,

                                            y + sign * length]),

                             (Path.LINETO, [x - flow, y + sign * length])])

                path.extend(self._arc(quadrant=quadrant,

                                      cw=angle == DOWN,

                                      radius=self.radius - flow,

                                      center=(x - self.radius,

                                              y + sign * self.radius)))

                path.append((Path.LINETO, [x - flow, y + sign * flow]))

                label_location = [tip[0], tip[1] + sign * self.offset]

            return tip, label_location



    def _revert(self, path, first_action=Path.LINETO):

        

        reverse_path = []

        next_code = first_action

        for code, position in path[::-1]:

            reverse_path.append((next_code, position))

            next_code = code

        return reverse_path

                                                                           

                                          

                                    

                                   

                                 

                     



    @_docstring.interpd

    def add(self, patchlabel='', flows=None, orientations=None, labels='',

            trunklength=1.0, pathlengths=0.25, prior=None, connect=(0, 0),

            rotation=0, **kwargs):

        

                                             

        flows = np.array([1.0, -1.0]) if flows is None else np.array(flows)

        n = flows.shape[0]                   

        if rotation is None:

            rotation = 0

        else:

                                                                

            rotation /= 90.0

        if orientations is None:

            orientations = 0

        try:

            orientations = np.broadcast_to(orientations, n)

        except ValueError:

            raise ValueError(

                f"The shapes of 'flows' {np.shape(flows)} and 'orientations' "

                f"{np.shape(orientations)} are incompatible"

            ) from None

        try:

            labels = np.broadcast_to(labels, n)

        except ValueError:

            raise ValueError(

                f"The shapes of 'flows' {np.shape(flows)} and 'labels' "

                f"{np.shape(labels)} are incompatible"

            ) from None

        if trunklength < 0:

            raise ValueError(

                "'trunklength' is negative, which is not allowed because it "

                "would cause poor layout")

        if abs(np.sum(flows)) > self.tolerance:

            _log.info("The sum of the flows is nonzero (%f; patchlabel=%r); "

                      "is the system not at steady state?",

                      np.sum(flows), patchlabel)

        scaled_flows = self.scale * flows

        gain = sum(max(flow, 0) for flow in scaled_flows)

        loss = sum(min(flow, 0) for flow in scaled_flows)

        if prior is not None:

            if prior < 0:

                raise ValueError("The index of the prior diagram is negative")

            if min(connect) < 0:

                raise ValueError(

                    "At least one of the connection indices is negative")

            if prior >= len(self.diagrams):

                raise ValueError(

                    f"The index of the prior diagram is {prior}, but there "

                    f"are only {len(self.diagrams)} other diagrams")

            if connect[0] >= len(self.diagrams[prior].flows):

                raise ValueError(

                    "The connection index to the source diagram is {}, but "

                    "that diagram has only {} flows".format(

                        connect[0], len(self.diagrams[prior].flows)))

            if connect[1] >= n:

                raise ValueError(

                    f"The connection index to this diagram is {connect[1]}, "

                    f"but this diagram has only {n} flows")

            if self.diagrams[prior].angles[connect[0]] is None:

                raise ValueError(

                    f"The connection cannot be made, which may occur if the "

                    f"magnitude of flow {connect[0]} of diagram {prior} is "

                    f"less than the specified tolerance")

            flow_error = (self.diagrams[prior].flows[connect[0]] +

                          flows[connect[1]])

            if abs(flow_error) >= self.tolerance:

                raise ValueError(

                    f"The scaled sum of the connected flows is {flow_error}, "

                    f"which is not within the tolerance ({self.tolerance})")



                                            

        are_inputs = [None] * n

        for i, flow in enumerate(flows):

            if flow >= self.tolerance:

                are_inputs[i] = True

            elif flow <= -self.tolerance:

                are_inputs[i] = False

            else:

                _log.info(

                    "The magnitude of flow %d (%f) is below the tolerance "

                    "(%f).\nIt will not be shown, and it cannot be used in a "

                    "connection.", i, flow, self.tolerance)



                                                               

        angles = [None] * n

        for i, (orient, is_input) in enumerate(zip(orientations, are_inputs)):

            if orient == 1:

                if is_input:

                    angles[i] = DOWN

                elif is_input is False:

                                                             

                    angles[i] = UP

            elif orient == 0:

                if is_input is not None:

                    angles[i] = RIGHT

            else:

                if orient != -1:

                    raise ValueError(

                        f"The value of orientations[{i}] is {orient}, "

                        f"but it must be -1, 0, or 1")

                if is_input:

                    angles[i] = UP

                elif is_input is False:

                    angles[i] = DOWN



                                           

        if np.iterable(pathlengths):

            if len(pathlengths) != n:

                raise ValueError(

                    f"The lengths of 'flows' ({n}) and 'pathlengths' "

                    f"({len(pathlengths)}) are incompatible")

        else:                                 

            urlength = pathlengths

            ullength = pathlengths

            lrlength = pathlengths

            lllength = pathlengths

            d = dict(RIGHT=pathlengths)

            pathlengths = [d.get(angle, 0) for angle in angles]

                                                          

                                       

            for i, (angle, is_input, flow) in enumerate(zip(angles, are_inputs,

                                                            scaled_flows)):

                if angle == DOWN and is_input:

                    pathlengths[i] = ullength

                    ullength += flow

                elif angle == UP and is_input is False:

                    pathlengths[i] = urlength

                    urlength -= flow                                 

                                                             

                                       

            for i, (angle, is_input, flow) in enumerate(reversed(list(zip(

                  angles, are_inputs, scaled_flows)))):

                if angle == UP and is_input:

                    pathlengths[n - i - 1] = lllength

                    lllength += flow

                elif angle == DOWN and is_input is False:

                    pathlengths[n - i - 1] = lrlength

                    lrlength -= flow

                                                           

                                      

            has_left_input = False

            for i, (angle, is_input, spec) in enumerate(reversed(list(zip(

                  angles, are_inputs, zip(scaled_flows, pathlengths))))):

                if angle == RIGHT:

                    if is_input:

                        if has_left_input:

                            pathlengths[n - i - 1] = 0

                        else:

                            has_left_input = True

                                                            

                                     

            has_right_output = False

            for i, (angle, is_input, spec) in enumerate(zip(

                  angles, are_inputs, list(zip(scaled_flows, pathlengths)))):

                if angle == RIGHT:

                    if is_input is False:

                        if has_right_output:

                            pathlengths[i] = 0

                        else:

                            has_right_output = True



                                                                               

                     

        urpath = [(Path.MOVETO, [(self.gap - trunklength / 2.0),               

                                 gain / 2.0]),

                  (Path.LINETO, [(self.gap - trunklength / 2.0) / 2.0,

                                 gain / 2.0]),

                  (Path.CURVE4, [(self.gap - trunklength / 2.0) / 8.0,

                                 gain / 2.0]),

                  (Path.CURVE4, [(trunklength / 2.0 - self.gap) / 8.0,

                                 -loss / 2.0]),

                  (Path.LINETO, [(trunklength / 2.0 - self.gap) / 2.0,

                                 -loss / 2.0]),

                  (Path.LINETO, [(trunklength / 2.0 - self.gap),

                                 -loss / 2.0])]

        llpath = [(Path.LINETO, [(trunklength / 2.0 - self.gap),              

                                 loss / 2.0]),

                  (Path.LINETO, [(trunklength / 2.0 - self.gap) / 2.0,

                                 loss / 2.0]),

                  (Path.CURVE4, [(trunklength / 2.0 - self.gap) / 8.0,

                                 loss / 2.0]),

                  (Path.CURVE4, [(self.gap - trunklength / 2.0) / 8.0,

                                 -gain / 2.0]),

                  (Path.LINETO, [(self.gap - trunklength / 2.0) / 2.0,

                                 -gain / 2.0]),

                  (Path.LINETO, [(self.gap - trunklength / 2.0),

                                 -gain / 2.0])]

        lrpath = [(Path.LINETO, [(trunklength / 2.0 - self.gap),               

                                 loss / 2.0])]

        ulpath = [(Path.LINETO, [self.gap - trunklength / 2.0,              

                                 gain / 2.0])]



                                                                           

        tips = np.zeros((n, 2))

        label_locations = np.zeros((n, 2))

                                                                       

        for i, (angle, is_input, spec) in enumerate(zip(

              angles, are_inputs, list(zip(scaled_flows, pathlengths)))):

            if angle == DOWN and is_input:

                tips[i, :], label_locations[i, :] = self._add_input(

                    ulpath, angle, *spec)

            elif angle == UP and is_input is False:

                tips[i, :], label_locations[i, :] = self._add_output(

                    urpath, angle, *spec)

                                                                          

        for i, (angle, is_input, spec) in enumerate(reversed(list(zip(

              angles, are_inputs, list(zip(scaled_flows, pathlengths)))))):

            if angle == UP and is_input:

                tip, label_location = self._add_input(llpath, angle, *spec)

                tips[n - i - 1, :] = tip

                label_locations[n - i - 1, :] = label_location

            elif angle == DOWN and is_input is False:

                tip, label_location = self._add_output(lrpath, angle, *spec)

                tips[n - i - 1, :] = tip

                label_locations[n - i - 1, :] = label_location

                                                           

        has_left_input = False

        for i, (angle, is_input, spec) in enumerate(reversed(list(zip(

              angles, are_inputs, list(zip(scaled_flows, pathlengths)))))):

            if angle == RIGHT and is_input:

                if not has_left_input:

                                                      

                                                       

                    if llpath[-1][1][0] > ulpath[-1][1][0]:

                        llpath.append((Path.LINETO, [ulpath[-1][1][0],

                                                     llpath[-1][1][1]]))

                    has_left_input = True

                tip, label_location = self._add_input(llpath, angle, *spec)

                tips[n - i - 1, :] = tip

                label_locations[n - i - 1, :] = label_location

                                                            

        has_right_output = False

        for i, (angle, is_input, spec) in enumerate(zip(

              angles, are_inputs, list(zip(scaled_flows, pathlengths)))):

            if angle == RIGHT and is_input is False:

                if not has_right_output:

                                                      

                                                       

                    if urpath[-1][1][0] < lrpath[-1][1][0]:

                        urpath.append((Path.LINETO, [lrpath[-1][1][0],

                                                     urpath[-1][1][1]]))

                    has_right_output = True

                tips[i, :], label_locations[i, :] = self._add_output(

                    urpath, angle, *spec)

                                    

        if not has_left_input:

            ulpath.pop()

            llpath.pop()

        if not has_right_output:

            lrpath.pop()

            urpath.pop()



                                                                             

        path = (urpath + self._revert(lrpath) + llpath + self._revert(ulpath) +

                [(Path.CLOSEPOLY, urpath[0][1])])



                                                 

        codes, vertices = zip(*path)

        vertices = np.array(vertices)



        def _get_angle(a, r):

            if a is None:

                return None

            else:

                return a + r



        if prior is None:

            if rotation != 0:                                       

                angles = [_get_angle(angle, rotation) for angle in angles]

                rotate = Affine2D().rotate_deg(rotation * 90).transform_affine

                tips = rotate(tips)

                label_locations = rotate(label_locations)

                vertices = rotate(vertices)

            text = self.ax.text(0, 0, s=patchlabel, ha='center', va='center')

        else:

            rotation = (self.diagrams[prior].angles[connect[0]] -

                        angles[connect[1]])

            angles = [_get_angle(angle, rotation) for angle in angles]

            rotate = Affine2D().rotate_deg(rotation * 90).transform_affine

            tips = rotate(tips)

            offset = self.diagrams[prior].tips[connect[0]] - tips[connect[1]]

            translate = Affine2D().translate(*offset).transform_affine

            tips = translate(tips)

            label_locations = translate(rotate(label_locations))

            vertices = translate(rotate(vertices))

            kwds = dict(s=patchlabel, ha='center', va='center')

            text = self.ax.text(*offset, **kwds)

        if mpl.rcParams['_internal.classic_mode']:

            fc = kwargs.pop('fc', kwargs.pop('facecolor', '#bfd1d4'))

            lw = kwargs.pop('lw', kwargs.pop('linewidth', 0.5))

        else:

            fc = kwargs.pop('fc', kwargs.pop('facecolor', None))

            lw = kwargs.pop('lw', kwargs.pop('linewidth', None))

        if fc is None:

            fc = self.ax._get_patches_for_fill.get_next_color()

        patch = PathPatch(Path(vertices, codes), fc=fc, lw=lw, **kwargs)

        self.ax.add_patch(patch)



                              

        texts = []

        for number, angle, label, location in zip(flows, angles, labels,

                                                  label_locations):

            if label is None or angle is None:

                label = ''

            elif self.unit is not None:

                if isinstance(self.format, str):

                    quantity = self.format % abs(number) + self.unit

                elif callable(self.format):

                    quantity = self.format(number)

                else:

                    raise TypeError(

                        'format must be callable or a format string')

                if label != '':

                    label += "\n"

                label += quantity

            texts.append(self.ax.text(x=location[0], y=location[1],

                                      s=label,

                                      ha='center', va='center'))

                                                                               

                                                                             

                                             



                                                      

        self.extent = (min(np.min(vertices[:, 0]),

                           np.min(label_locations[:, 0]),

                           self.extent[0]),

                       max(np.max(vertices[:, 0]),

                           np.max(label_locations[:, 0]),

                           self.extent[1]),

                       min(np.min(vertices[:, 1]),

                           np.min(label_locations[:, 1]),

                           self.extent[2]),

                       max(np.max(vertices[:, 1]),

                           np.max(label_locations[:, 1]),

                           self.extent[3]))

                                                                               

                                                                           



                                           

        self.diagrams.append(

            SimpleNamespace(patch=patch, flows=flows, angles=angles, tips=tips,

                            text=text, texts=texts))



                                                                             

        return self



    def finish(self):

        

        self.ax.axis([self.extent[0] - self.margin,

                      self.extent[1] + self.margin,

                      self.extent[2] - self.margin,

                      self.extent[3] + self.margin])

        self.ax.set_aspect('equal', adjustable='datalim')

        return self.diagrams






import logging



import numpy as np



from matplotlib import _api, artist as martist

import matplotlib.transforms as mtransforms

import matplotlib._layoutgrid as mlayoutgrid





_log = logging.getLogger(__name__)





                                                      

def do_constrained_layout(fig, h_pad, w_pad,

                          hspace=None, wspace=None, rect=(0, 0, 1, 1),

                          compress=False):

    



    renderer = fig._get_renderer()

                             

    layoutgrids = make_layoutgrids(fig, None, rect=rect)

    if not layoutgrids['hasgrids']:

        _api.warn_external('There are no gridspecs with layoutgrids. '

                           'Possibly did not call parent GridSpec with the'

                           ' "figure" keyword')

        return



    for _ in range(2):

                                                                          

                                                                         

                                                                           

                                              



                                                             

                                               

        make_layout_margins(layoutgrids, fig, renderer, h_pad=h_pad,

                            w_pad=w_pad, hspace=hspace, wspace=wspace)

        make_margin_suptitles(layoutgrids, fig, renderer, h_pad=h_pad,

                              w_pad=w_pad)



                                                                    

                                                                     

                               

        match_submerged_margins(layoutgrids, fig)



                                                 

        layoutgrids[fig].update_variables()



        warn_collapsed = ('constrained_layout not applied because '

                          'axes sizes collapsed to zero.  Try making '

                          'figure larger or Axes decorations smaller.')

        if check_no_collapsed_axes(layoutgrids, fig):

            reposition_axes(layoutgrids, fig, renderer, h_pad=h_pad,

                            w_pad=w_pad, hspace=hspace, wspace=wspace)

            if compress:

                layoutgrids = compress_fixed_aspect(layoutgrids, fig)

                layoutgrids[fig].update_variables()

                if check_no_collapsed_axes(layoutgrids, fig):

                    reposition_axes(layoutgrids, fig, renderer, h_pad=h_pad,

                                    w_pad=w_pad, hspace=hspace, wspace=wspace)

                else:

                    _api.warn_external(warn_collapsed)



                if ((suptitle := fig._suptitle) is not None and

                        suptitle.get_in_layout() and suptitle._autopos):

                    x, _ = suptitle.get_position()

                    suptitle.set_position(

                        (x, layoutgrids[fig].get_inner_bbox().y1 + h_pad))

                    suptitle.set_verticalalignment('bottom')

        else:

            _api.warn_external(warn_collapsed)

        reset_margins(layoutgrids, fig)

    return layoutgrids





def make_layoutgrids(fig, layoutgrids, rect=(0, 0, 1, 1)):

    



    if layoutgrids is None:

        layoutgrids = dict()

        layoutgrids['hasgrids'] = False

    if not hasattr(fig, '_parent'):

                                                                  

                 

        layoutgrids[fig] = mlayoutgrid.LayoutGrid(parent=rect, name='figlb')

    else:

                   

        gs = fig._subplotspec.get_gridspec()

                                                                      

                                     

        layoutgrids = make_layoutgrids_gs(layoutgrids, gs)

                                               

        parentlb = layoutgrids[gs]

        layoutgrids[fig] = mlayoutgrid.LayoutGrid(

            parent=parentlb,

            name='panellb',

            parent_inner=True,

            nrows=1, ncols=1,

            parent_pos=(fig._subplotspec.rowspan,

                        fig._subplotspec.colspan))

                                                     

    for sfig in fig.subfigs:

        layoutgrids = make_layoutgrids(sfig, layoutgrids)



                                                        

    for ax in fig._localaxes:

        gs = ax.get_gridspec()

        if gs is not None:

            layoutgrids = make_layoutgrids_gs(layoutgrids, gs)



    return layoutgrids





def make_layoutgrids_gs(layoutgrids, gs):

    



    if gs in layoutgrids or gs.figure is None:

        return layoutgrids

                                                                      

                           

    layoutgrids['hasgrids'] = True

    if not hasattr(gs, '_subplot_spec'):

                         

        parent = layoutgrids[gs.figure]

        layoutgrids[gs] = mlayoutgrid.LayoutGrid(

                parent=parent,

                parent_inner=True,

                name='gridspec',

                ncols=gs._ncols, nrows=gs._nrows,

                width_ratios=gs.get_width_ratios(),

                height_ratios=gs.get_height_ratios())

    else:

                                            

        subplot_spec = gs._subplot_spec

        parentgs = subplot_spec.get_gridspec()

                                                                             

        if parentgs not in layoutgrids:

            layoutgrids = make_layoutgrids_gs(layoutgrids, parentgs)

        subspeclb = layoutgrids[parentgs]

                                                          

                                      

        rep = (gs, 'top')

        if rep not in layoutgrids:

            layoutgrids[rep] = mlayoutgrid.LayoutGrid(

                parent=subspeclb,

                name='top',

                nrows=1, ncols=1,

                parent_pos=(subplot_spec.rowspan, subplot_spec.colspan))

        layoutgrids[gs] = mlayoutgrid.LayoutGrid(

                parent=layoutgrids[rep],

                name='gridspec',

                nrows=gs._nrows, ncols=gs._ncols,

                width_ratios=gs.get_width_ratios(),

                height_ratios=gs.get_height_ratios())

    return layoutgrids





def check_no_collapsed_axes(layoutgrids, fig):

    

    for sfig in fig.subfigs:

        ok = check_no_collapsed_axes(layoutgrids, sfig)

        if not ok:

            return False

    for ax in fig.axes:

        gs = ax.get_gridspec()

        if gs in layoutgrids:                                

            lg = layoutgrids[gs]

            for i in range(gs.nrows):

                for j in range(gs.ncols):

                    bb = lg.get_inner_bbox(i, j)

                    if bb.width <= 0 or bb.height <= 0:

                        return False

    return True





def compress_fixed_aspect(layoutgrids, fig):

    gs = None

    for ax in fig.axes:

        if ax.get_subplotspec() is None:

            continue

        ax.apply_aspect()

        sub = ax.get_subplotspec()

        _gs = sub.get_gridspec()

        if gs is None:

            gs = _gs

            extraw = np.zeros(gs.ncols)

            extrah = np.zeros(gs.nrows)

        elif _gs != gs:

            raise ValueError('Cannot do compressed layout if Axes are not'

                             'all from the same gridspec')

        orig = ax.get_position(original=True)

        actual = ax.get_position(original=False)

        dw = orig.width - actual.width

        if dw > 0:

            extraw[sub.colspan] = np.maximum(extraw[sub.colspan], dw)

        dh = orig.height - actual.height

        if dh > 0:

            extrah[sub.rowspan] = np.maximum(extrah[sub.rowspan], dh)



    if gs is None:

        raise ValueError('Cannot do compressed layout if no Axes '

                         'are part of a gridspec.')

    w = np.sum(extraw) / 2

    layoutgrids[fig].edit_margin_min('left', w)

    layoutgrids[fig].edit_margin_min('right', w)



    h = np.sum(extrah) / 2

    layoutgrids[fig].edit_margin_min('top', h)

    layoutgrids[fig].edit_margin_min('bottom', h)

    return layoutgrids





def get_margin_from_padding(obj, *, w_pad=0, h_pad=0,

                            hspace=0, wspace=0):



    ss = obj._subplotspec

    gs = ss.get_gridspec()



    if hasattr(gs, 'hspace'):

        _hspace = (gs.hspace if gs.hspace is not None else hspace)

        _wspace = (gs.wspace if gs.wspace is not None else wspace)

    else:

        _hspace = (gs._hspace if gs._hspace is not None else hspace)

        _wspace = (gs._wspace if gs._wspace is not None else wspace)



    _wspace = _wspace / 2

    _hspace = _hspace / 2



    nrows, ncols = gs.get_geometry()

                                                         

                                                          

                                            

    margin = {'leftcb': w_pad, 'rightcb': w_pad,

              'bottomcb': h_pad, 'topcb': h_pad,

              'left': 0, 'right': 0,

              'top': 0, 'bottom': 0}

    if _wspace / ncols > w_pad:

        if ss.colspan.start > 0:

            margin['leftcb'] = _wspace / ncols

        if ss.colspan.stop < ncols:

            margin['rightcb'] = _wspace / ncols

    if _hspace / nrows > h_pad:

        if ss.rowspan.stop < nrows:

            margin['bottomcb'] = _hspace / nrows

        if ss.rowspan.start > 0:

            margin['topcb'] = _hspace / nrows



    return margin





def make_layout_margins(layoutgrids, fig, renderer, *, w_pad=0, h_pad=0,

                        hspace=0, wspace=0):

    

    for sfig in fig.subfigs:                                        

        ss = sfig._subplotspec

        gs = ss.get_gridspec()



        make_layout_margins(layoutgrids, sfig, renderer,

                            w_pad=w_pad, h_pad=h_pad,

                            hspace=hspace, wspace=wspace)



        margins = get_margin_from_padding(sfig, w_pad=0, h_pad=0,

                                          hspace=hspace, wspace=wspace)

        layoutgrids[gs].edit_outer_margin_mins(margins, ss)



    for ax in fig._localaxes:

        if not ax.get_subplotspec() or not ax.get_in_layout():

            continue



        ss = ax.get_subplotspec()

        gs = ss.get_gridspec()



        if gs not in layoutgrids:

            return



        margin = get_margin_from_padding(ax, w_pad=w_pad, h_pad=h_pad,

                                         hspace=hspace, wspace=wspace)

        pos, bbox = get_pos_and_bbox(ax, renderer)

                                                                         

                                                        

        margin['left'] += pos.x0 - bbox.x0

        margin['right'] += bbox.x1 - pos.x1

                                                  

        margin['bottom'] += pos.y0 - bbox.y0

        margin['top'] += bbox.y1 - pos.y1



                                                             

                                                                

        for cbax in ax._colorbars:

                                                           

            pad = colorbar_get_pad(layoutgrids, cbax)

                                                                   

            cbp_rspan, cbp_cspan = get_cb_parent_spans(cbax)

            loc = cbax._colorbar_info['location']

            cbpos, cbbbox = get_pos_and_bbox(cbax, renderer)

            if loc == 'right':

                if cbp_cspan.stop == ss.colspan.stop:

                                                                        

                    margin['rightcb'] += cbbbox.width + pad

            elif loc == 'left':

                if cbp_cspan.start == ss.colspan.start:

                                                                       

                    margin['leftcb'] += cbbbox.width + pad

            elif loc == 'top':

                if cbp_rspan.start == ss.rowspan.start:

                    margin['topcb'] += cbbbox.height + pad

            else:

                if cbp_rspan.stop == ss.rowspan.stop:

                    margin['bottomcb'] += cbbbox.height + pad

                                                                   

                             

            if loc in ['top', 'bottom']:

                if (cbp_cspan.start == ss.colspan.start and

                        cbbbox.x0 < bbox.x0):

                    margin['left'] += bbox.x0 - cbbbox.x0

                if (cbp_cspan.stop == ss.colspan.stop and

                        cbbbox.x1 > bbox.x1):

                    margin['right'] += cbbbox.x1 - bbox.x1

                        

            if loc in ['left', 'right']:

                if (cbp_rspan.stop == ss.rowspan.stop and

                        cbbbox.y0 < bbox.y0):

                    margin['bottom'] += bbox.y0 - cbbbox.y0

                if (cbp_rspan.start == ss.rowspan.start and

                        cbbbox.y1 > bbox.y1):

                    margin['top'] += cbbbox.y1 - bbox.y1

                                                                          

        layoutgrids[gs].edit_outer_margin_mins(margin, ss)



                                            

    for leg in fig.legends:

        inv_trans_fig = None

        if leg._outside_loc and leg._bbox_to_anchor is None:

            if inv_trans_fig is None:

                inv_trans_fig = fig.transFigure.inverted().transform_bbox

            bbox = inv_trans_fig(leg.get_tightbbox(renderer))

            w = bbox.width + 2 * w_pad

            h = bbox.height + 2 * h_pad

            legendloc = leg._outside_loc

            if legendloc == 'lower':

                layoutgrids[fig].edit_margin_min('bottom', h)

            elif legendloc == 'upper':

                layoutgrids[fig].edit_margin_min('top', h)

            if legendloc == 'right':

                layoutgrids[fig].edit_margin_min('right', w)

            elif legendloc == 'left':

                layoutgrids[fig].edit_margin_min('left', w)





def make_margin_suptitles(layoutgrids, fig, renderer, *, w_pad=0, h_pad=0):

                                                       

                                     



    inv_trans_fig = fig.transFigure.inverted().transform_bbox

                                                                              

    padbox = mtransforms.Bbox([[0, 0], [w_pad, h_pad]])

    padbox = (fig.transFigure -

              fig.transSubfigure).transform_bbox(padbox)

    h_pad_local = padbox.height

    w_pad_local = padbox.width



    for sfig in fig.subfigs:

        make_margin_suptitles(layoutgrids, sfig, renderer,

                              w_pad=w_pad, h_pad=h_pad)



    if fig._suptitle is not None and fig._suptitle.get_in_layout():

        p = fig._suptitle.get_position()

        if getattr(fig._suptitle, '_autopos', False):

            fig._suptitle.set_position((p[0], 1 - h_pad_local))

            bbox = inv_trans_fig(fig._suptitle.get_tightbbox(renderer))

            layoutgrids[fig].edit_margin_min('top', bbox.height + 2 * h_pad)



    if fig._supxlabel is not None and fig._supxlabel.get_in_layout():

        p = fig._supxlabel.get_position()

        if getattr(fig._supxlabel, '_autopos', False):

            fig._supxlabel.set_position((p[0], h_pad_local))

            bbox = inv_trans_fig(fig._supxlabel.get_tightbbox(renderer))

            layoutgrids[fig].edit_margin_min('bottom',

                                             bbox.height + 2 * h_pad)



    if fig._supylabel is not None and fig._supylabel.get_in_layout():

        p = fig._supylabel.get_position()

        if getattr(fig._supylabel, '_autopos', False):

            fig._supylabel.set_position((w_pad_local, p[1]))

            bbox = inv_trans_fig(fig._supylabel.get_tightbbox(renderer))

            layoutgrids[fig].edit_margin_min('left', bbox.width + 2 * w_pad)





def match_submerged_margins(layoutgrids, fig):

    



    axsdone = []

    for sfig in fig.subfigs:

        axsdone += match_submerged_margins(layoutgrids, sfig)



    axs = [a for a in fig.get_axes()

           if (a.get_subplotspec() is not None and a.get_in_layout() and

               a not in axsdone)]



    for ax1 in axs:

        ss1 = ax1.get_subplotspec()

        if ss1.get_gridspec() not in layoutgrids:

            axs.remove(ax1)

            continue

        lg1 = layoutgrids[ss1.get_gridspec()]



                           

        if len(ss1.colspan) > 1:

            maxsubl = np.max(

                lg1.margin_vals['left'][ss1.colspan[1:]] +

                lg1.margin_vals['leftcb'][ss1.colspan[1:]]

            )

            maxsubr = np.max(

                lg1.margin_vals['right'][ss1.colspan[:-1]] +

                lg1.margin_vals['rightcb'][ss1.colspan[:-1]]

            )

            for ax2 in axs:

                ss2 = ax2.get_subplotspec()

                lg2 = layoutgrids[ss2.get_gridspec()]

                if lg2 is not None and len(ss2.colspan) > 1:

                    maxsubl2 = np.max(

                        lg2.margin_vals['left'][ss2.colspan[1:]] +

                        lg2.margin_vals['leftcb'][ss2.colspan[1:]])

                    if maxsubl2 > maxsubl:

                        maxsubl = maxsubl2

                    maxsubr2 = np.max(

                        lg2.margin_vals['right'][ss2.colspan[:-1]] +

                        lg2.margin_vals['rightcb'][ss2.colspan[:-1]])

                    if maxsubr2 > maxsubr:

                        maxsubr = maxsubr2

            for i in ss1.colspan[1:]:

                lg1.edit_margin_min('left', maxsubl, cell=i)

            for i in ss1.colspan[:-1]:

                lg1.edit_margin_min('right', maxsubr, cell=i)



                        

        if len(ss1.rowspan) > 1:

            maxsubt = np.max(

                lg1.margin_vals['top'][ss1.rowspan[1:]] +

                lg1.margin_vals['topcb'][ss1.rowspan[1:]]

            )

            maxsubb = np.max(

                lg1.margin_vals['bottom'][ss1.rowspan[:-1]] +

                lg1.margin_vals['bottomcb'][ss1.rowspan[:-1]]

            )



            for ax2 in axs:

                ss2 = ax2.get_subplotspec()

                lg2 = layoutgrids[ss2.get_gridspec()]

                if lg2 is not None:

                    if len(ss2.rowspan) > 1:

                        maxsubt = np.max([np.max(

                            lg2.margin_vals['top'][ss2.rowspan[1:]] +

                            lg2.margin_vals['topcb'][ss2.rowspan[1:]]

                        ), maxsubt])

                        maxsubb = np.max([np.max(

                            lg2.margin_vals['bottom'][ss2.rowspan[:-1]] +

                            lg2.margin_vals['bottomcb'][ss2.rowspan[:-1]]

                        ), maxsubb])

            for i in ss1.rowspan[1:]:

                lg1.edit_margin_min('top', maxsubt, cell=i)

            for i in ss1.rowspan[:-1]:

                lg1.edit_margin_min('bottom', maxsubb, cell=i)



    return axs





def get_cb_parent_spans(cbax):

    

    rowstart = np.inf

    rowstop = -np.inf

    colstart = np.inf

    colstop = -np.inf

    for parent in cbax._colorbar_info['parents']:

        ss = parent.get_subplotspec()

        rowstart = min(ss.rowspan.start, rowstart)

        rowstop = max(ss.rowspan.stop, rowstop)

        colstart = min(ss.colspan.start, colstart)

        colstop = max(ss.colspan.stop, colstop)



    rowspan = range(rowstart, rowstop)

    colspan = range(colstart, colstop)

    return rowspan, colspan





def get_pos_and_bbox(ax, renderer):

    

    fig = ax.get_figure(root=False)

    pos = ax.get_position(original=True)

                                                                   

    pos = pos.transformed(fig.transSubfigure - fig.transFigure)

    tightbbox = martist._get_tightbbox_for_layout_only(ax, renderer)

    if tightbbox is None:

        bbox = pos

    else:

        bbox = tightbbox.transformed(fig.transFigure.inverted())

    return pos, bbox





def reposition_axes(layoutgrids, fig, renderer, *,

                    w_pad=0, h_pad=0, hspace=0, wspace=0):

    

    trans_fig_to_subfig = fig.transFigure - fig.transSubfigure

    for sfig in fig.subfigs:

        bbox = layoutgrids[sfig].get_outer_bbox()

        sfig._redo_transform_rel_fig(

            bbox=bbox.transformed(trans_fig_to_subfig))

        reposition_axes(layoutgrids, sfig, renderer,

                        w_pad=w_pad, h_pad=h_pad,

                        wspace=wspace, hspace=hspace)



    for ax in fig._localaxes:

        if ax.get_subplotspec() is None or not ax.get_in_layout():

            continue



                                                                     

                        

        ss = ax.get_subplotspec()

        gs = ss.get_gridspec()

        if gs not in layoutgrids:

            return



        bbox = layoutgrids[gs].get_inner_bbox(rows=ss.rowspan,

                                              cols=ss.colspan)



                                                          

        newbbox = trans_fig_to_subfig.transform_bbox(bbox)

        ax._set_position(newbbox)



                             

                                                                      

                       

        offset = {'left': 0, 'right': 0, 'bottom': 0, 'top': 0}

        for nn, cbax in enumerate(ax._colorbars[::-1]):

            if ax == cbax._colorbar_info['parents'][0]:

                reposition_colorbar(layoutgrids, cbax, renderer,

                                    offset=offset)





def reposition_colorbar(layoutgrids, cbax, renderer, *, offset=None):

    



    parents = cbax._colorbar_info['parents']

    gs = parents[0].get_gridspec()

    fig = cbax.get_figure(root=False)

    trans_fig_to_subfig = fig.transFigure - fig.transSubfigure



    cb_rspans, cb_cspans = get_cb_parent_spans(cbax)

    bboxparent = layoutgrids[gs].get_bbox_for_cb(rows=cb_rspans,

                                                 cols=cb_cspans)

    pb = layoutgrids[gs].get_inner_bbox(rows=cb_rspans, cols=cb_cspans)



    location = cbax._colorbar_info['location']

    anchor = cbax._colorbar_info['anchor']

    fraction = cbax._colorbar_info['fraction']

    aspect = cbax._colorbar_info['aspect']

    shrink = cbax._colorbar_info['shrink']



    cbpos, cbbbox = get_pos_and_bbox(cbax, renderer)



                                                                        

                                                                

                                                   

    cbpad = colorbar_get_pad(layoutgrids, cbax)

    if location in ('left', 'right'):

                                                     

        pbcb = pb.shrunk(fraction, shrink).anchored(anchor, pb)

                                                               

                                         

        if location == 'right':

            lmargin = cbpos.x0 - cbbbox.x0

            dx = bboxparent.x1 - pbcb.x0 + offset['right']

            dx += cbpad + lmargin

            offset['right'] += cbbbox.width + cbpad

            pbcb = pbcb.translated(dx, 0)

        else:

            lmargin = cbpos.x0 - cbbbox.x0

            dx = bboxparent.x0 - pbcb.x0                  

            dx += -cbbbox.width - cbpad + lmargin - offset['left']

            offset['left'] += cbbbox.width + cbpad

            pbcb = pbcb.translated(dx, 0)

    else:                    

        pbcb = pb.shrunk(shrink, fraction).anchored(anchor, pb)

        if location == 'top':

            bmargin = cbpos.y0 - cbbbox.y0

            dy = bboxparent.y1 - pbcb.y0 + offset['top']

            dy += cbpad + bmargin

            offset['top'] += cbbbox.height + cbpad

            pbcb = pbcb.translated(0, dy)

        else:

            bmargin = cbpos.y0 - cbbbox.y0

            dy = bboxparent.y0 - pbcb.y0

            dy += -cbbbox.height - cbpad + bmargin - offset['bottom']

            offset['bottom'] += cbbbox.height + cbpad

            pbcb = pbcb.translated(0, dy)



    pbcb = trans_fig_to_subfig.transform_bbox(pbcb)

    cbax.set_transform(fig.transSubfigure)

    cbax._set_position(pbcb)

    cbax.set_anchor(anchor)

    if location in ['bottom', 'top']:

        aspect = 1 / aspect

    cbax.set_box_aspect(aspect)

    cbax.set_aspect('auto')

    return offset





def reset_margins(layoutgrids, fig):

    

    for sfig in fig.subfigs:

        reset_margins(layoutgrids, sfig)

    for ax in fig.axes:

        if ax.get_in_layout():

            gs = ax.get_gridspec()

            if gs in layoutgrids:                                

                layoutgrids[gs].reset_margins()

    layoutgrids[fig].reset_margins()





def colorbar_get_pad(layoutgrids, cax):

    parents = cax._colorbar_info['parents']

    gs = parents[0].get_gridspec()



    cb_rspans, cb_cspans = get_cb_parent_spans(cax)

    bboxouter = layoutgrids[gs].get_inner_bbox(rows=cb_rspans, cols=cb_cspans)



    if cax._colorbar_info['location'] in ['right', 'left']:

        size = bboxouter.width

    else:

        size = bboxouter.height



    return cax._colorbar_info['pad'] * size


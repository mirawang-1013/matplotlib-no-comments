



from urllib.parse import urlsplit, urlunsplit



from docutils import nodes



import matplotlib

from matplotlib import rcParamsDefault





class _QueryReference(nodes.Inline, nodes.TextElement):

    



    def to_query_string(self):

        

        return '&'.join(f'{name}={value}' for name, value in self.attlist())





def _visit_query_reference_node(self, node):

    

    query = node.to_query_string()

    for refnode in node.findall(nodes.reference):

        uri = urlsplit(refnode['refuri'])._replace(query=query)

        refnode['refuri'] = urlunsplit(uri)



    self.visit_literal(node)





def _depart_query_reference_node(self, node):

    

    self.depart_literal(node)





def _rcparam_role(name, rawtext, text, lineno, inliner, options=None, content=None):

    

                                                                             

                                               

    title = f'rcParams["{text}"]'

    target = 'matplotlibrc-sample'

    ref_nodes, messages = inliner.interpreted(title, f'{title} <{target}>',

                                              'ref', lineno)



    qr = _QueryReference(rawtext, highlight=text)

    qr += ref_nodes

    node_list = [qr]



                                                                               

                                                      

    if text in rcParamsDefault and text != "backend":

        node_list.extend([

            nodes.Text(' (default: '),

            nodes.literal('', repr(rcParamsDefault[text])),

            nodes.Text(')'),

            ])



    return node_list, messages





def _mpltype_role(name, rawtext, text, lineno, inliner, options=None, content=None):

    

    mpltype = text

    type_to_link_target = {

        'color': 'colors_def',

        'hatch': 'hatch_def',

    }

    if mpltype not in type_to_link_target:

        raise ValueError(f"Unknown mpltype: {mpltype!r}")



    node_list, messages = inliner.interpreted(

        mpltype, f'{mpltype} <{type_to_link_target[mpltype]}>', 'ref', lineno)

    return node_list, messages





def setup(app):

    app.add_role("rc", _rcparam_role)

    app.add_role("mpltype", _mpltype_role)

    app.add_node(

        _QueryReference,

        html=(_visit_query_reference_node, _depart_query_reference_node),

        latex=(_visit_query_reference_node, _depart_query_reference_node),

        text=(_visit_query_reference_node, _depart_query_reference_node),

    )

    return {"version": matplotlib.__version__,

            "parallel_read_safe": True, "parallel_write_safe": True}


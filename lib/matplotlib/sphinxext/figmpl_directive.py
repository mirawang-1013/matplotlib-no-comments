

import os

from os.path import relpath

from pathlib import PurePath, Path

import shutil



from docutils import nodes

from docutils.parsers.rst import directives

from docutils.parsers.rst.directives.images import Figure, Image

from sphinx.errors import ExtensionError



import matplotlib





class figmplnode(nodes.General, nodes.Element):

    pass





class FigureMpl(Figure):

    



    has_content = False

    required_arguments = 1

    optional_arguments = 2

    final_argument_whitespace = False

    option_spec = {

        'alt': directives.unchanged,

        'height': directives.length_or_unitless,

        'width': directives.length_or_percentage_or_unitless,

        'scale': directives.nonnegative_int,

        'align': Image.align,

        'class': directives.class_option,

        'caption': directives.unchanged,

        'srcset': directives.unchanged,

    }



    def run(self):



        image_node = figmplnode()



        imagenm = self.arguments[0]

        image_node['alt'] = self.options.get('alt', '')

        image_node['align'] = self.options.get('align', None)

        image_node['class'] = self.options.get('class', None)

        image_node['width'] = self.options.get('width', None)

        image_node['height'] = self.options.get('height', None)

        image_node['scale'] = self.options.get('scale', None)

        image_node['caption'] = self.options.get('caption', None)



                                                                 

                                                               

                                       



        image_node['uri'] = imagenm

        image_node['srcset'] = self.options.get('srcset', None)



        return [image_node]





def _parse_srcsetNodes(st):

    

    entries = st.split(',')

    srcset = {}

    for entry in entries:

        spl = entry.strip().split(' ')

        if len(spl) == 1:

            srcset[0] = spl[0]

        elif len(spl) == 2:

            mult = spl[1][:-1]

            srcset[float(mult)] = spl[0]

        else:

            raise ExtensionError(f'srcset argument "{entry}" is invalid.')

    return srcset





def _copy_images_figmpl(self, node):



                                                                             

                                                                          

    if node['srcset']:

        srcset = _parse_srcsetNodes(node['srcset'])

    else:

        srcset = None



                                                                                       

    docsource = PurePath(self.document['source']).parent



                                       

    srctop = self.builder.srcdir

    rel = relpath(docsource, srctop).replace('.', '').replace(os.sep, '-')

    if len(rel):

        rel += '-'

                               



    imagedir = PurePath(self.builder.outdir, self.builder.imagedir)

                                                                                 



    Path(imagedir).mkdir(parents=True, exist_ok=True)



                                           

    if srcset:

        for src in srcset.values():

                                                                         

            abspath = PurePath(docsource, src)

            name = rel + abspath.name

            shutil.copyfile(abspath, imagedir / name)

    else:

        abspath = PurePath(docsource, node['uri'])

        name = rel + abspath.name

        shutil.copyfile(abspath, imagedir / name)



    return imagedir, srcset, rel





def visit_figmpl_html(self, node):



    imagedir, srcset, rel = _copy_images_figmpl(self, node)



                                   

    docsource = PurePath(self.document['source'])

           

                                          

    srctop = PurePath(self.builder.srcdir, '')

                              

    relsource = relpath(docsource, srctop)

                     

    desttop = PurePath(self.builder.outdir, '')

                                   

    dest = desttop / relsource



                                                         

    imagerel = PurePath(relpath(imagedir, dest.parent)).as_posix()

    if self.builder.name == "dirhtml":

        imagerel = f'..{imagerel}'



                                  

    nm = PurePath(node['uri'][1:]).name

    uri = f'{imagerel}/{rel}{nm}'

    img_attrs = {'src': uri, 'alt': node['alt']}



                                                        

    maxsrc = uri

    if srcset:

        maxmult = -1

        srcsetst = ''

        for mult, src in srcset.items():

            nm = PurePath(src[1:]).name

                                           

            path = f'{imagerel}/{rel}{nm}'

            srcsetst += path

            if mult == 0:

                srcsetst += ', '

            else:

                srcsetst += f' {mult:1.2f}x, '



            if mult > maxmult:

                maxmult = mult

                maxsrc = path



                                          

        img_attrs['srcset'] = srcsetst[:-2]



    if node['class'] is not None:

        img_attrs['class'] = ' '.join(node['class'])

    for style in ['width', 'height', 'scale']:

        if node[style]:

            if 'style' not in img_attrs:

                img_attrs['style'] = f'{style}: {node[style]};'

            else:

                img_attrs['style'] += f'{style}: {node[style]};'



                                             

                                                                                  

                                       

                                                          

          

                  

                                                                     

                                                                                 

                   

               

    self.body.append(

        self.starttag(

            node, 'figure',

            CLASS=f'align-{node["align"]}' if node['align'] else 'align-center'))

    self.body.append(

        self.starttag(node, 'a', CLASS='reference internal image-reference',

                      href=maxsrc) +

        self.emptytag(node, 'img', **img_attrs) +

        '</a>\n')

    if node['caption']:

        self.body.append(self.starttag(node, 'figcaption'))

        self.body.append(self.starttag(node, 'p'))

        self.body.append(self.starttag(node, 'span', CLASS='caption-text'))

        self.body.append(node['caption'])

        self.body.append('</span></p></figcaption>\n')

    self.body.append('</figure>\n')





def visit_figmpl_latex(self, node):



    if node['srcset'] is not None:

        imagedir, srcset = _copy_images_figmpl(self, node)

        maxmult = -1

                                                   

        maxmult = max(srcset, default=-1)

        node['uri'] = PurePath(srcset[maxmult]).name



    self.visit_figure(node)





def depart_figmpl_html(self, node):

    pass





def depart_figmpl_latex(self, node):

    self.depart_figure(node)





def figurempl_addnode(app):

    app.add_node(figmplnode,

                 html=(visit_figmpl_html, depart_figmpl_html),

                 latex=(visit_figmpl_latex, depart_figmpl_latex))





def setup(app):

    app.add_directive("figure-mpl", FigureMpl)

    figurempl_addnode(app)

    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True,

                'version': matplotlib.__version__}

    return metadata


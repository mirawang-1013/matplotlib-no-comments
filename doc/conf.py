                                                               

                                                

 

                                                                           

      

 

                                                                             

                                                                 

                 

 

                                                                              

                                  



from datetime import datetime, timezone

import logging

import os

from pathlib import Path

import re

import shutil

import subprocess

import sys

import time

from urllib.parse import urlsplit, urlunsplit

import warnings



from packaging.version import parse as parse_version

import sphinx

import yaml



import matplotlib



                                      

print(f"Building Documentation for Matplotlib: {matplotlib.__version__}")



                                                               

is_release_build = tags.has('release')        



                           

CIRCLECI = 'CIRCLECI' in os.environ

                                                        

                                                         

DEVDOCS = (

    CIRCLECI and

    (os.environ.get("CIRCLE_PROJECT_USERNAME") == "matplotlib") and

    (os.environ.get("CIRCLE_BRANCH") == "main") and

    (not os.environ.get("CIRCLE_PULL_REQUEST", "").startswith(

        "https://github.com/matplotlib/matplotlib/pull")))





def _parse_skip_subdirs_file():

    

    default_skip_subdirs = [

        'release/prev_whats_new/*', 'users/explain/*', 'api/*', 'gallery/*',

        'tutorials/*', 'plot_types/*', 'devel/*']

    try:

        with open(".mpl_skip_subdirs.yaml", 'r') as fin:

            print('Reading subdirectories to skip from',

                  '.mpl_skip_subdirs.yaml')

            out = yaml.full_load(fin)

        return out['skip_subdirs']

    except FileNotFoundError:

                         

        with open(".mpl_skip_subdirs.yaml", 'w') as fout:

            yamldict = {'skip_subdirs': default_skip_subdirs,

                        'comment': 'For use with make html-skip-subdirs'}

            yaml.dump(yamldict, fout)

        print('Skipping subdirectories, but .mpl_skip_subdirs.yaml',

              'not found so creating a default one. Edit this file',

              'to customize which directories are included in build.')



        return default_skip_subdirs





skip_subdirs = []

                                      

if 'skip_sub_dirs=1' in sys.argv:

    skip_subdirs = _parse_skip_subdirs_file()



                                                                   

                                                          

sourceyear = datetime.fromtimestamp(

    int(os.environ.get('SOURCE_DATE_EPOCH', time.time())), timezone.utc).year



                                                                            

                                                                       

                            

sys.path.append(os.path.abspath('.'))

sys.path.append('.')



                       

                       



                                                                              

                                                                             

                       

warnings.filterwarnings('error', append=True)



                                                                                      

                                                                                       

                                                                     

warnings.filterwarnings('default', category=UserWarning,

                        message=r'Glyph \d+ \(.+\) missing from font\(s\)')

warnings.filterwarnings('default', category=UserWarning,

                        message=r'Matplotlib currently does not support .+ natively\.')



                                                                     

                                                                           

extensions = [

    'sphinx.ext.autodoc',

    'sphinx.ext.autosummary',

    'sphinx.ext.graphviz',

    'sphinx.ext.inheritance_diagram',

    'sphinx.ext.intersphinx',

    'sphinx.ext.ifconfig',

    'IPython.sphinxext.ipython_console_highlighting',

    'IPython.sphinxext.ipython_directive',

    'numpydoc',                                       

    'sphinx_gallery.gen_gallery',

    'matplotlib.sphinxext.mathmpl',

    'matplotlib.sphinxext.plot_directive',

    'matplotlib.sphinxext.roles',

    'matplotlib.sphinxext.figmpl_directive',

    'sphinxcontrib.inkscapeconverter',

    'sphinxext.github',

    'sphinxext.math_symbol_table',

    'sphinxext.missing_references',

    'sphinxext.mock_gui_toolkits',

    'sphinxext.skip_deprecated',

    'sphinxext.redirect_from',

    'sphinx_copybutton',

    'sphinx_design',

    'sphinx_tags',

]



exclude_patterns = [

    'api/prev_api_changes/api_changes_*/*',

    '**/*inc.rst',

    'users/explain/index.rst'                                                       

]



exclude_patterns += skip_subdirs





def _check_dependencies():

    names = {

        **{ext: ext.split(".")[0] for ext in extensions},

                                                                             

                                                         

        "colorspacious": 'colorspacious',

        "mpl_sphinx_theme": 'mpl_sphinx_theme',

        "sphinxcontrib.inkscapeconverter": 'sphinxcontrib-svg2pdfconverter',

    }

    missing = []

    for name in names:

        try:

            __import__(name)

        except ImportError:

            missing.append(names[name])

    if missing:

        raise ImportError(

            "The following dependencies are missing to build the "

            f"documentation: {', '.join(missing)}")



                                                     

    if 'mpl_sphinx_theme' not in missing:

        import pydata_sphinx_theme

        import mpl_sphinx_theme

        print(f"pydata sphinx theme: {pydata_sphinx_theme.__version__}")

        print(f"mpl sphinx theme: {mpl_sphinx_theme.__version__}")



    if shutil.which('dot') is None:

        raise OSError(

            "No binary named dot - graphviz must be installed to build the "

            "documentation")

    if shutil.which('latex') is None:

        raise OSError(

            "No binary named latex - a LaTeX distribution must be installed to build "

            "the documentation")



_check_dependencies()





                                              

import sphinx_gallery



if parse_version(sphinx_gallery.__version__) >= parse_version('0.16.0'):

    gallery_order_sectionorder = 'sphinxext.gallery_order.sectionorder'

    gallery_order_subsectionorder = 'sphinxext.gallery_order.subsectionorder'

    clear_basic_units = 'sphinxext.util.clear_basic_units'

    matplotlib_reduced_latex_scraper = 'sphinxext.util.matplotlib_reduced_latex_scraper'

else:

                                                                          

                                                                      

    from sphinxext.gallery_order import (

        sectionorder as gallery_order_sectionorder,

        subsectionorder as gallery_order_subsectionorder)

    from sphinxext.util import clear_basic_units, matplotlib_reduced_latex_scraper



if parse_version(sphinx_gallery.__version__) >= parse_version('0.17.0'):

    sg_matplotlib_animations = (True, 'mp4')

else:

    sg_matplotlib_animations = True



                                                                               

from sphinx_gallery import gen_rst



                                                             

warnings.filterwarnings('ignore', category=UserWarning,

                        message=r'(\n|.)*is non-interactive, and thus cannot be shown')





                                            

def tutorials_download_error(record):

    if re.match("download file not readable: .*tutorials_(python|jupyter).zip",

                record.msg):

        return False





logger = logging.getLogger('sphinx')

logger.addFilter(tutorials_download_error)



autosummary_generate = True

autodoc_typehints = "none"

autodoc_mock_imports = ["pytest"]



                                                                        

                                                                              

warnings.filterwarnings('ignore', category=DeprecationWarning,

                        module='importlib',                                   

                        message=r'(\n|.)*module was deprecated.*')



autodoc_docstring_signature = True

autodoc_default_options = {'members': None, 'undoc-members': None}





def autodoc_process_bases(app, name, obj, options, bases):

    

    for cls in bases[:]:

        if not isinstance(cls, type):

            continue

        if cls.__module__ == 'pybind11_builtins' and cls.__name__ == 'pybind11_object':

            bases.remove(cls)





                                                                          

                        

warnings.filterwarnings('ignore', category=DeprecationWarning,

                        module='sphinx.util.inspect')



nitpicky = True

                                                    

missing_references_write_json = False

missing_references_warn_unused_ignores = False





intersphinx_mapping = {

    'Pillow': ('https://pillow.readthedocs.io/en/stable/', None),

    'cycler': ('https://matplotlib.org/cycler/', None),

    'dateutil': ('https://dateutil.readthedocs.io/en/stable/', None),

    'ipykernel': ('https://ipykernel.readthedocs.io/en/latest/', None),

    'numpy': ('https://numpy.org/doc/stable/', None),

    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),

    'pytest': ('https://pytest.org/en/stable/', None),

    'python': ('https://docs.python.org/3/', None),

    'scipy': ('https://docs.scipy.org/doc/scipy/', None),

    'tornado': ('https://www.tornadoweb.org/en/stable/', None),

    'xarray': ('https://docs.xarray.dev/en/stable/', None),

    'meson-python': ('https://mesonbuild.com/meson-python/', None),

    'pip': ('https://pip.pypa.io/en/stable/', None),

}





gallery_dirs = [f'{ed}' for ed in

                ['gallery', 'tutorials', 'plot_types', 'users/explain']

                if f'{ed}/*' not in skip_subdirs]



example_dirs = []

for gd in gallery_dirs:

    gd = gd.replace('gallery', 'examples').replace('users/explain', 'users_explain')

    example_dirs += [f'../galleries/{gd}']



sphinx_gallery_conf = {

    'backreferences_dir': Path('api', '_as_gen'),

                                                                               

    'compress_images': ('thumbnails', 'images') if is_release_build else (),

    'doc_module': ('matplotlib', 'mpl_toolkits'),

    'examples_dirs': example_dirs,

    'filename_pattern': '^((?!sgskip).)*$',

    'gallery_dirs': gallery_dirs,

    'image_scrapers': (matplotlib_reduced_latex_scraper, ),

    'image_srcset': ["2x"],

    'junit': '../test-results/sphinx-gallery/junit.xml' if CIRCLECI else '',

    'matplotlib_animations': sg_matplotlib_animations,

    'min_reported_time': 1,

    'plot_gallery': 'True',                      

    'reference_url': {'matplotlib': None, 'mpl_toolkits': None},

    'prefer_full_module': {r'mpl_toolkits\.'},

    'remove_config_comments': True,

    'reset_modules': ('matplotlib', clear_basic_units),

    'subsection_order': gallery_order_sectionorder,

    'thumbnail_size': (320, 224),

    'within_subsection_order': gallery_order_subsectionorder,

    'capture_repr': (),

    'copyfile_regex': r'.*\.rst',

}



if parse_version(sphinx_gallery.__version__) >= parse_version('0.17.0'):

    sphinx_gallery_conf['parallel'] = True

                                                                       

    warnings.filterwarnings('default', category=UserWarning, module='joblib')



if 'plot_gallery=0' in sys.argv:

                                                                              

                                                      



    def gallery_image_warning_filter(record):

        msg = record.msg

        for pattern in (sphinx_gallery_conf['gallery_dirs'] +

                        ['_static/constrained_layout']):

            if msg.startswith(f'image file not readable: {pattern}'):

                return False



        if msg == 'Could not obtain image size. :scale: option is ignored.':

            return False



        return True



    logger = logging.getLogger('sphinx')

    logger.addFilter(gallery_image_warning_filter)



                           

tags_create_tags = True

tags_page_title = "All tags"

tags_create_badges = True

tags_badge_colors = {

    "animation": "primary",

    "component:*": "secondary",

    "event-handling": "success",

    "interactivity:*": "dark",

    "plot-type:*": "danger",

    "*": "light"                 

}



mathmpl_fontsize = 11.0

mathmpl_srcset = ['2x']



                                                           

gen_rst.EXAMPLE_HEADER = """
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "{0}"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. meta::
        :keywords: codex

    .. note::
        :class: sphx-glr-download-link-note

        :ref:`Go to the end <sphx_glr_download_{1}>`
        to download the full example code.{2}

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_{1}:

"""



                                                                        

templates_path = ['_templates']



                                 

source_suffix = '.rst'



                                                                  

source_encoding = "utf-8"



                                

root_doc = 'index'



                        

try:

    SHA = subprocess.check_output(

        ['git', 'describe', '--dirty']).decode('utf-8').strip()

                                                                               

                        

except (subprocess.CalledProcessError, FileNotFoundError):

    SHA = matplotlib.__version__





html_context = {

    "doc_version": SHA,

}



project = 'Matplotlib'

copyright = (

    '2002–2012 John Hunter, Darren Dale, Eric Firing, Michael Droettboom '

    'and the Matplotlib development team; '

    f'2012–{sourceyear} The Matplotlib development team'

)





                                                                            

                                              

 

                        



version = matplotlib.__version__

                                                 

release = version



                                                                            

                                   

            

                                                            

today_fmt = '%B %d, %Y'



                                                            

unused_docs = []



                                                                     

                                 



                                                                       

                                      

                         



                                                                         

                                      

                      



                                                              

pygments_style = 'sphinx'



default_role = 'obj'



                              

                              



                                                                         

                      

                       

                                                         

                                                                              

                                                                        

formats = {'html': ('png', 100), 'latex': ('pdf', 100)}

plot_formats = [formats[target] for target in ['html', 'latex']

                if target in sys.argv] or list(formats.values())

                                             

plot_srcset = ['2x']



                  



github_project_url = "https://github.com/matplotlib/matplotlib/"





                         

                         



def add_html_cache_busting(app, pagename, templatename, context, doctree):

    

    from sphinx.builders.html import Stylesheet, JavaScript



    css_tag = context['css_tag']

    js_tag = context['js_tag']



    def css_tag_with_cache_busting(css):

        if isinstance(css, Stylesheet) and css.filename is not None:

            url = urlsplit(css.filename)

            if not url.netloc and not url.query:

                url = url._replace(query=SHA)

                css = Stylesheet(urlunsplit(url), priority=css.priority,

                                 **css.attributes)

        return css_tag(css)



    def js_tag_with_cache_busting(js):

        if isinstance(js, JavaScript) and js.filename is not None:

            url = urlsplit(js.filename)

            if not url.netloc and not url.query:

                url = url._replace(query=SHA)

                js = JavaScript(urlunsplit(url), priority=js.priority,

                                **js.attributes)

        return js_tag(js)



    context['css_tag'] = css_tag_with_cache_busting

    context['js_tag'] = js_tag_with_cache_busting





                                                                          

                                                                          

                            

html_css_files = [

    "mpl.css",

]



html_theme = "mpl_sphinx_theme"



                                                                     

                                       

                   



                                                                           

              

html_theme_options = {

    "navbar_links": "internal",

                                                                              

                                                                          

    "collapse_navigation": not is_release_build,

    "show_prev_next": False,

    "switcher": {

                                                                               

                                                                                 

                                                                                 

                                 

        "json_url": (

            "https://output.circle-artifacts.com/output/job/"

            f"{os.environ['CIRCLE_WORKFLOW_JOB_ID']}/artifacts/"

            f"{os.environ['CIRCLE_NODE_INDEX']}"

            "/doc/build/html/_static/switcher.json" if CIRCLECI and not DEVDOCS else

            f"https://matplotlib.org/devdocs/_static/switcher.json?{SHA}"

        ),

        "version_match": (

            matplotlib.__version__

            if matplotlib.__version_info__.releaselevel == 'final'

            else 'dev')

    },

    "navbar_end": ["theme-switcher", "version-switcher", "mpl_icon_links"],

    "navbar_persistent": ["search-button"],

    "footer_start": ["copyright", "sphinx-version", "doc_version"],

                                                                           

                                                                               

                                                                     

    "announcement": "unreleased" if not is_release_build else "",

    "show_version_warning_banner": True,

}

include_analytics = is_release_build

if include_analytics:

    html_theme_options["analytics"] = {

        "plausible_analytics_domain": "matplotlib.org",

        "plausible_analytics_url": "https://views.scientific-python.org/js/script.js"

    }



                                                                             

                                                                             

                                                                         

html_static_path = ['_static']



                                                                          

                         

html_file_suffix = '.html'



                                                                     

html_baseurl = 'https://matplotlib.org/stable/'



                                                                             

                                  

html_last_updated_fmt = '%b %d, %Y'



                                      

html_index = 'index.html'



                                                                  

                    



                                                         

html_sidebars = {

    "index": [

                                      

        "cheatsheet_sidebar.html",

        "donate_sidebar.html",

    ],

                                                                                   

                                                                                

                                                        

    "release/release_notes": ["empty_sidebar.html"],

                                                

}



                                        

html_show_sourcelink = False



                                                 

copybutton_prompt_text = r'>>> |\.\.\. '

copybutton_prompt_is_regexp = True



                                              

html_use_index = False



                                                                             

                                                              

html_domain_index = False



                                                                              

                         



                                                                            

                                       

html_use_opensearch = 'https://matplotlib.org/stable'



                                              

htmlhelp_basename = 'Matplotlibdoc'



                                   

smartquotes = False



                 

html_favicon = '_static/favicon.ico'



                          

                          



                                    

latex_paper_size = 'letter'



                                              

                 

                                                   

                                   



latex_documents = [

    (root_doc, 'Matplotlib.tex', 'Matplotlib',

     'John Hunter\\and Darren Dale\\and Eric Firing\\and Michael Droettboom'

     '\\and and the matplotlib development team', 'manual'),

]





                                                                               

                 

latex_logo = None



                                

latex_engine = 'xelatex'                 



latex_elements = {}



                                                                    

                                                                          

latex_elements['babel'] = r'\usepackage{babel}'



                    

                                                          

                                                    

latex_elements['fontenc'] = r'''
\usepackage{fontspec}
\defaultfontfeatures[\rmfamily,\sffamily,\ttfamily]{}
'''



                                                                     

                                                              

                                    

latex_elements['fontpkg'] = r"""
\IfFontExistsTF{XITS}{
 \setmainfont{XITS}
}{
 \setmainfont{XITS}[
  Extension      = .otf,
  UprightFont    = *-Regular,
  ItalicFont     = *-Italic,
  BoldFont       = *-Bold,
  BoldItalicFont = *-BoldItalic,
]}
\IfFontExistsTF{FreeSans}{
 \setsansfont{FreeSans}
}{
 \setsansfont{FreeSans}[
  Extension      = .otf,
  UprightFont    = *,
  ItalicFont     = *Oblique,
  BoldFont       = *Bold,
  BoldItalicFont = *BoldOblique,
]}
\IfFontExistsTF{FreeMono}{
 \setmonofont{FreeMono}
}{
 \setmonofont{FreeMono}[
  Extension      = .otf,
  UprightFont    = *,
  ItalicFont     = *Oblique,
  BoldFont       = *Bold,
  BoldItalicFont = *BoldOblique,
]}
% needed for \mathbb (blackboard alphabet) to actually work
\usepackage{unicode-math}
\IfFontExistsTF{XITS Math}{
 \setmathfont{XITS Math}
}{
 \setmathfont{XITSMath-Regular}[
  Extension      = .otf,
]}
"""



                                                            

latex_elements['passoptionstopackages'] = r"""
    \PassOptionsToPackage{headheight=14pt}{geometry}
"""



                                          

latex_elements['preamble'] = r"""
   % Show Parts and Chapters in Table of Contents
   \setcounter{tocdepth}{0}
   % One line per author on title page
   \DeclareRobustCommand{\and}%
     {\end{tabular}\kern-\tabcolsep\\\begin{tabular}[t]{c}}%
   \usepackage{etoolbox}
   \AtBeginEnvironment{sphinxthebibliography}{\appendix\part{Appendices}}
   \usepackage{expdlist}
   \let\latexdescription=\description
   \def\description{\latexdescription{}{} \breaklabel}
   % But expdlist old LaTeX package requires fixes:
   % 1) remove extra space
   \makeatletter
   \patchcmd\@item{{\@breaklabel} }{{\@breaklabel}}{}{}
   \makeatother
   % 2) fix bug in expdlist's way of breaking the line after long item label
   \makeatletter
   \def\breaklabel{%
       \def\@breaklabel{%
           \leavevmode\par
           % now a hack because Sphinx inserts \leavevmode after term node
           \def\leavevmode{\def\leavevmode{\unhbox\voidb@x}}%
      }%
   }
   \makeatother
"""

                                                                   

                                                    

                                                                    

                                                                    

latex_elements['maxlistdepth'] = '10'

latex_elements['pointsize'] = '11pt'



                                     

latex_elements['printindex'] = r'\footnotesize\raggedright\printindex'



                                                    

latex_appendices = []



                                         

latex_use_modindex = True



latex_toplevel_sectioning = 'part'



                                                                 

               

autoclass_content = 'both'



texinfo_documents = [

    (root_doc, 'matplotlib', 'Matplotlib Documentation',

     'John Hunter@*Darren Dale@*Eric Firing@*Michael Droettboom@*'

     'The matplotlib development team',

     'Matplotlib', "Python plotting package", 'Programming',

     1),

]



                 



numpydoc_show_class_members = False



                                                                       

inheritance_graph_attrs = dict(size='1000.0', splines='polyline')

                                                                    

inheritance_node_attrs = dict(height=0.02, margin=0.055, penwidth=1,

                              width=0.01)

inheritance_edge_attrs = dict(penwidth=1)



graphviz_dot = shutil.which('dot')

graphviz_output_format = 'svg'



                                                                               

                   

                                                                               

link_github = True

                                                



if link_github:

    import inspect



    extensions.append('sphinx.ext.linkcode')



    def linkcode_resolve(domain, info):

        

        if domain != 'py':

            return None



        modname = info['module']

        fullname = info['fullname']



        submod = sys.modules.get(modname)

        if submod is None:

            return None



        obj = submod

        for part in fullname.split('.'):

            try:

                obj = getattr(obj, part)

            except AttributeError:

                return None



        if inspect.isfunction(obj):

            obj = inspect.unwrap(obj)

        try:

            fn = inspect.getsourcefile(obj)

        except TypeError:

            fn = None

        if not fn or fn.endswith('__init__.py'):

            try:

                fn = inspect.getsourcefile(sys.modules[obj.__module__])

            except (TypeError, AttributeError, KeyError):

                fn = None

        if not fn:

            return None



        try:

            source, lineno = inspect.getsourcelines(obj)

        except (OSError, TypeError):

            lineno = None



        linespec = (f"#L{lineno:d}-L{lineno + len(source) - 1:d}"

                    if lineno else "")



        startdir = Path(matplotlib.__file__).parent.parent

        try:

            fn = os.path.relpath(fn, start=startdir).replace(os.path.sep, '/')

        except ValueError:

            return None



        if not fn.startswith(('matplotlib/', 'mpl_toolkits/')):

            return None



        version = parse_version(matplotlib.__version__)

        tag = 'main' if version.is_devrelease else f'v{version.public}'

        return ("https://github.com/matplotlib/matplotlib/blob"

                f"/{tag}/lib/{fn}{linespec}")

else:

    extensions.append('sphinx.ext.viewcode')





def generate_ScalarMappable_docs():



    import matplotlib.colorizer

    from numpydoc.docscrape_sphinx import get_doc_object

    from pathlib import Path

    import textwrap

    from sphinx.util.inspect import stringify_signature

    target_file = Path(__file__).parent / 'api' / 'scalarmappable.gen_rst'

    with open(target_file, 'w') as fout:

        fout.write("""
.. class:: ScalarMappable(colorizer, **kwargs)
   :canonical: matplotlib.colorizer._ScalarMappable

""")

        for meth in [

                matplotlib.colorizer._ScalarMappable.autoscale,

                matplotlib.colorizer._ScalarMappable.autoscale_None,

                matplotlib.colorizer._ScalarMappable.changed,

                """
   .. attribute:: colorbar

        The last colorbar associated with this ScalarMappable. May be None.
""",

                matplotlib.colorizer._ScalarMappable.get_alpha,

                matplotlib.colorizer._ScalarMappable.get_array,

                matplotlib.colorizer._ScalarMappable.get_clim,

                matplotlib.colorizer._ScalarMappable.get_cmap,

                """
   .. property:: norm
""",

                matplotlib.colorizer._ScalarMappable.set_array,

                matplotlib.colorizer._ScalarMappable.set_clim,

                matplotlib.colorizer._ScalarMappable.set_cmap,

                matplotlib.colorizer._ScalarMappable.set_norm,

                matplotlib.colorizer._ScalarMappable.to_rgba,

        ]:

            if isinstance(meth, str):

                fout.write(meth)

            else:

                name = meth.__name__

                sig = stringify_signature(inspect.signature(meth))

                docstring = textwrap.indent(

                    str(get_doc_object(meth)),

                    '      '

                ).rstrip()

                fout.write(f"""
   .. method::  {name}{sig}
{docstring}

""")





                                                                               

              

                                                                               

def setup(app):

    if any(st in version for st in ('post', 'dev', 'alpha', 'beta')):

        bld_type = 'dev'

    else:

        bld_type = 'rel'

    app.add_config_value('skip_sub_dirs', 0, '')

    app.add_config_value('releaselevel', bld_type, 'env')

    app.connect('autodoc-process-bases', autodoc_process_bases)

    if sphinx.version_info[:2] < (7, 1):

        app.connect('html-page-context', add_html_cache_busting, priority=1000)

    generate_ScalarMappable_docs()


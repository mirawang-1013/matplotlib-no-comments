import sys





def matplotlib_reduced_latex_scraper(block, block_vars, gallery_conf,

                                     **kwargs):

    

    from sphinx_gallery.scrapers import matplotlib_scraper



    if gallery_conf['builder_name'] == 'latex':

        gallery_conf['image_srcset'] = []

    return matplotlib_scraper(block, block_vars, gallery_conf, **kwargs)





                                                                       

def clear_basic_units(gallery_conf, fname):

    return sys.modules.pop('basic_units', None)


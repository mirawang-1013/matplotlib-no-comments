



from pathlib import Path

from sphinx.util.docutils import SphinxDirective

from sphinx.domains import Domain

from sphinx.util import logging



logger = logging.getLogger(__name__)





HTML_TEMPLATE = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url={v}">
  </head>
</html>
"""





def setup(app):

    app.add_directive("redirect-from", RedirectFrom)

    app.add_domain(RedirectFromDomain)

    app.connect("builder-inited", _clear_redirects)

    app.connect("build-finished", _generate_redirects)



    metadata = {'parallel_read_safe': True}

    return metadata





class RedirectFromDomain(Domain):

    

    name = 'redirect_from'

    label = 'redirect_from'



    @property

    def redirects(self):

        

        return self.data.setdefault('redirects', {})



    def clear_doc(self, docname):

        self.redirects.pop(docname, None)



    def merge_domaindata(self, docnames, otherdata):

        for src, dst in otherdata['redirects'].items():

            if src not in self.redirects:

                self.redirects[src] = dst

            elif self.redirects[src] != dst:

                raise ValueError(

                    f"Inconsistent redirections from {src} to "

                    f"{self.redirects[src]} and {otherdata['redirects'][src]}")





class RedirectFrom(SphinxDirective):

    required_arguments = 1



    def run(self):

        redirected_doc, = self.arguments

        domain = self.env.get_domain('redirect_from')

        current_doc = self.env.path2doc(self.state.document.current_source)

        redirected_reldoc, _ = self.env.relfn2path(redirected_doc, current_doc)

        if (

            redirected_reldoc in domain.redirects

            and domain.redirects[redirected_reldoc] != current_doc

        ):

            raise ValueError(

                f"{redirected_reldoc} is already noted as redirecting to "

                f"{domain.redirects[redirected_reldoc]}\n"

                f"Cannot also redirect it to {current_doc}"

            )

        domain.redirects[redirected_reldoc] = current_doc

        return []





def _generate_redirects(app, exception):

    builder = app.builder

    if builder.name != "html" or exception:

        return

    for k, v in app.env.get_domain('redirect_from').redirects.items():

        p = Path(app.outdir, k + builder.out_suffix)

        html = HTML_TEMPLATE.format(v=builder.get_relative_uri(k, v))

        if p.is_file():

            if p.read_text() != html:

                logger.warning('A redirect-from directive is trying to '

                               'create %s, but that file already exists '

                               '(perhaps you need to run "make clean")', p)

        else:

            logger.info('making refresh html file: %s redirect to %s', k, v)

            p.parent.mkdir(parents=True, exist_ok=True)

            p.write_text(html, encoding='utf-8')





def _clear_redirects(app):

    domain = app.env.get_domain('redirect_from')

    if domain.redirects:

        logger.info('clearing cached redirects')

        domain.redirects.clear()


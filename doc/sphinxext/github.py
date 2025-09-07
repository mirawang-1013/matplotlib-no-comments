

 

                                                                  

 



from docutils import nodes, utils

from docutils.parsers.rst.roles import set_classes





def make_link_node(rawtext, app, type, slug, options):

    



    try:

        base = app.config.github_project_url

        if not base:

            raise AttributeError

        if not base.endswith('/'):

            base += '/'

    except AttributeError as err:

        raise ValueError(

            f'github_project_url configuration value is not set '

            f'({err})') from err



    ref = base + type + '/' + slug + '/'

    set_classes(options)

    prefix = "#"

    if type == 'pull':

        prefix = "PR " + prefix

    node = nodes.reference(rawtext, prefix + utils.unescape(slug), refuri=ref,

                           **options)

    return node





def ghissue_role(name, rawtext, text, lineno, inliner, options={}, content=[]):

    



    try:

        issue_num = int(text)

        if issue_num <= 0:

            raise ValueError

    except ValueError:

        msg = inliner.reporter.error(

            'GitHub issue number must be a number greater than or equal to 1; '

            '"%s" is invalid.' % text, line=lineno)

        prb = inliner.problematic(rawtext, rawtext, msg)

        return [prb], [msg]

    app = inliner.document.settings.env.app

    if 'pull' in name.lower():

        category = 'pull'

    elif 'issue' in name.lower():

        category = 'issues'

    else:

        msg = inliner.reporter.error(

            'GitHub roles include "ghpull" and "ghissue", '

            '"%s" is invalid.' % name, line=lineno)

        prb = inliner.problematic(rawtext, rawtext, msg)

        return [prb], [msg]

    node = make_link_node(rawtext, app, category, str(issue_num), options)

    return [node], []





def ghuser_role(name, rawtext, text, lineno, inliner, options={}, content=[]):

    

    ref = 'https://www.github.com/' + text

    node = nodes.reference(rawtext, text, refuri=ref, **options)

    return [node], []





def ghcommit_role(

        name, rawtext, text, lineno, inliner, options={}, content=[]):

    

    app = inliner.document.settings.env.app

    try:

        base = app.config.github_project_url

        if not base:

            raise AttributeError

        if not base.endswith('/'):

            base += '/'

    except AttributeError as err:

        raise ValueError(

            f'github_project_url configuration value is not set '

            f'({err})') from err



    ref = base + text

    node = nodes.reference(rawtext, text[:6], refuri=ref, **options)

    return [node], []





def setup(app):

    

    app.add_role('ghissue', ghissue_role)

    app.add_role('ghpull', ghissue_role)

    app.add_role('ghuser', ghuser_role)

    app.add_role('ghcommit', ghcommit_role)

    app.add_config_value('github_project_url', None, 'env')



    metadata = {'parallel_read_safe': True, 'parallel_write_safe': True}

    return metadata


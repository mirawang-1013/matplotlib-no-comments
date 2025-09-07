



from collections import defaultdict

import json

from pathlib import Path



from docutils.utils import get_source_line

from sphinx.util import logging as sphinx_logging



import matplotlib



logger = sphinx_logging.getLogger(__name__)





def get_location(node, app):

    

    source, line = get_source_line(node)



    if source:

                                                                               

                                                                            

        if ':docstring of' in source:

            path, *post = source.rpartition(':docstring of')

            post = ''.join(post)

        else:

            path = source

            post = ''

                                                                

                                                                  

                                                                     

                                                                     

               

        basepath = Path(app.srcdir).parent.resolve()



        fullpath = Path(path).resolve()



        try:

            path = fullpath.relative_to(basepath)

        except ValueError:

                                                             

                                                            

                                                             

                                  

            path = Path("<external>") / fullpath.name



                                                               

                                                                  

        path = path.as_posix()



    else:

        path = "<unknown>"

        post = ''

    if not line:

        line = ""



    return f"{path}{post}:{line}"





def _truncate_location(location):

    

    return location.split(":", 1)[0]





def handle_missing_reference(app, domain, node):

    

    refdomain = node["refdomain"]

    reftype = node["reftype"]

    target = node["reftarget"]

    location = get_location(node, app)

    domain_type = f"{refdomain}:{reftype}"



    app.env.missing_references_events[(domain_type, target)].add(location)



                                                                                    

                                                                                        

                                          

    if location in app.env.missing_references_ignored_references.get(

            (domain_type, target), []):

        return True





def warn_unused_missing_references(app, exc):

    

                                                               

                                                

    basepath = Path(matplotlib.__file__).parent.parent.parent.resolve()

    srcpath = Path(app.srcdir).parent.resolve()



    if basepath != srcpath:

        return



                                                                

    references_ignored = app.env.missing_references_ignored_references

    references_events = app.env.missing_references_events



                                                          

    for (domain_type, target), locations in references_ignored.items():

        missing_reference_locations = [

            _truncate_location(location)

            for location in references_events.get((domain_type, target), [])]



                                                                         

                                                               

        for ignored_reference_location in locations:

            short_location = _truncate_location(ignored_reference_location)

            if short_location not in missing_reference_locations:

                msg = (f"Reference {domain_type} {target} for "

                       f"{ignored_reference_location} can be removed"

                       f" from {app.config.missing_references_filename}."

                        " It is no longer a missing reference in the docs.")

                logger.warning(msg,

                               location=ignored_reference_location,

                               type='ref',

                               subtype=domain_type)





def save_missing_references(app, exc):

    

    json_path = Path(app.confdir) / app.config.missing_references_filename

    references_warnings = app.env.missing_references_events

    _write_missing_references_json(references_warnings, json_path)





def _write_missing_references_json(records, json_path):

    

                                                               

                                             

    transformed_records = defaultdict(dict)

    for (domain_type, target), paths in records.items():

        transformed_records[domain_type][target] = sorted(paths)

    with json_path.open("w") as stream:

        json.dump(transformed_records, stream, sort_keys=True, indent=2)

        stream.write("\n")                                                         





def _read_missing_references_json(json_path):

    

    with json_path.open("r") as stream:

        data = json.load(stream)



    ignored_references = {}

    for domain_type, targets in data.items():

        for target, locations in targets.items():

            ignored_references[(domain_type, target)] = locations

    return ignored_references





def prepare_missing_references_setup(app):

    

    if not app.config.missing_references_enabled:

                                     

        return



    app.connect("warn-missing-reference", handle_missing_reference)

    if app.config.missing_references_warn_unused_ignores:

        app.connect("build-finished", warn_unused_missing_references)

    if app.config.missing_references_write_json:

        app.connect("build-finished", save_missing_references)



    json_path = Path(app.confdir) / app.config.missing_references_filename

    app.env.missing_references_ignored_references = (

        _read_missing_references_json(json_path) if json_path.exists() else {}

    )

    app.env.missing_references_events = defaultdict(set)





def setup(app):

    app.add_config_value("missing_references_enabled", True, "env")

    app.add_config_value("missing_references_write_json", False, "env")

    app.add_config_value("missing_references_warn_unused_ignores", True, "env")

    app.add_config_value("missing_references_filename",

                         "missing-references.json", "env")



    app.connect("builder-inited", prepare_missing_references_setup)



    return {'parallel_read_safe': True}


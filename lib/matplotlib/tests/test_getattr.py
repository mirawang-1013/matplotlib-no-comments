from importlib import import_module

from pkgutil import walk_packages



import matplotlib

import pytest



                                             

                                                

module_names = [

    m.name

    for m in walk_packages(

        path=matplotlib.__path__, prefix=f'{matplotlib.__name__}.'

    )

    if not m.name.startswith(__package__)

    and not any(x.startswith('_') for x in m.name.split('.'))

]





@pytest.mark.parametrize('module_name', module_names)

@pytest.mark.filterwarnings('ignore::DeprecationWarning')

@pytest.mark.filterwarnings('ignore::ImportWarning')

def test_getattr(module_name):

    

    try:

        module = import_module(module_name)

    except (ImportError, RuntimeError, OSError) as e:

                                                                          

        pytest.skip(f'Cannot import {module_name} due to {e}')



    key = 'THIS_SYMBOL_SHOULD_NOT_EXIST'

    if hasattr(module, key):

        delattr(module, key)


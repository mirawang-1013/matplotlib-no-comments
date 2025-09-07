import pytest

import sys

import matplotlib

from matplotlib import _api





def pytest_configure(config):

                                                                          

                                                                             

                                                                      

                                                                             

    for key, value in [

        ("markers", "flaky: (Provided by pytest-rerunfailures.)"),

        ("markers", "timeout: (Provided by pytest-timeout.)"),

        ("markers", "backend: Set alternate Matplotlib backend temporarily."),

        ("markers", "baseline_images: Compare output against references."),

        ("markers", "pytz: Tests that require pytz to be installed."),

        ("filterwarnings", "error"),

        ("filterwarnings",

         "ignore:.*The py23 module has been deprecated:DeprecationWarning"),

        ("filterwarnings",

         r"ignore:DynamicImporter.find_spec\(\) not found; "

         r"falling back to find_module\(\):ImportWarning"),

    ]:

        config.addinivalue_line(key, value)



    matplotlib.use('agg', force=True)

    matplotlib._called_from_pytest = True

    matplotlib._init_tests()





def pytest_unconfigure(config):

    matplotlib._called_from_pytest = False





@pytest.fixture(autouse=True)

def mpl_test_settings(request):

    from matplotlib.testing.decorators import _cleanup_cm



    with _cleanup_cm():



        backend = None

        backend_marker = request.node.get_closest_marker('backend')

        prev_backend = matplotlib.get_backend()

        if backend_marker is not None:

            assert len(backend_marker.args) == 1,
                "Marker 'backend' must specify 1 backend."

            backend, = backend_marker.args

            skip_on_importerror = backend_marker.kwargs.get(

                'skip_on_importerror', False)



                                                                  

            if backend.lower().startswith('qt5'):

                if any(sys.modules.get(k) for k in ('PyQt4', 'PySide')):

                    pytest.skip('Qt4 binding already imported')



        matplotlib.testing.setup()

        with _api.suppress_matplotlib_deprecation_warning():

            if backend is not None:

                                                                            

                                              

                import matplotlib.pyplot as plt

                try:

                    plt.switch_backend(backend)

                except ImportError as exc:

                                                                               

                                                          

                    if 'cairo' in backend.lower() or skip_on_importerror:

                        pytest.skip("Failed to switch to backend "

                                    f"{backend} ({exc}).")

                    else:

                        raise

                                                          

            matplotlib.style.use(["classic", "_classic_test_patch"])

        try:

            yield

        finally:

            if backend is not None:

                plt.close("all")

                matplotlib.use(prev_backend)





@pytest.fixture

def pd():

    

    pd = pytest.importorskip('pandas')

    try:

        from pandas.plotting import (

            deregister_matplotlib_converters as deregister)

        deregister()

    except ImportError:

        pass

    return pd





@pytest.fixture

def xr():

    



    xr = pytest.importorskip('xarray')

    return xr





@pytest.fixture

def text_placeholders(monkeypatch):

    

    from matplotlib.patches import Rectangle



    def patched_get_text_metrics_with_cache(renderer, text, fontprop, ismath, dpi):

        

                                                                                      

                                                                                

                                                                               

        height = fontprop.get_size()

        width = len(text) * height / 1.618                                    

        descent = 0

        return width, height, descent



    def patched_text_draw(self, renderer):

        

        if renderer is not None:

            self._renderer = renderer

        if not self.get_visible():

            return

        if self.get_text() == '':

            return

        bbox = self.get_window_extent()

        rect = Rectangle(bbox.p0, bbox.width, bbox.height,

                         facecolor=self.get_color(), edgecolor='none')

        rect.draw(renderer)



    monkeypatch.setattr('matplotlib.text._get_text_metrics_with_cache',

                        patched_get_text_metrics_with_cache)

    monkeypatch.setattr('matplotlib.text.Text.draw', patched_text_draw)


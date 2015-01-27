import os
import json

from rdflib import Graph
from pyld import jsonld

from IPython.html.nbextensions import install_nbextension, check_nbextension
from IPython.html.widgets import DOMWidget
from IPython.display import display, Javascript
from IPython.utils.traitlets import (
    Unicode,
    Instance,
    Dict,
)


pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
nbextension = os.path.basename(pkg_path)
static = os.path.join(pkg_path, 'static', nbextension)


class GraphMixin(DOMWidget):
    """
    An eventful object which has a graph
    """
    ld = Unicode(sync=True)
    graph = Instance(klass=Graph)

    context = Dict({})

    def __init__(self, *args, **kwargs):
        super(GraphMixin, self).__init__(*args, **kwargs)
        self.graph = self.graph or Graph()

    def _graph_changed(self, name, old, new):
        self._setting_ld = True
        self.ld = new.serialize(format="json-ld", indent=2)
        self._setting_ld = False

    def _ld_changed(self, name, old, new):
        if not self._setting_ld:
            def ld_args(graph):
                norm = jsonld.normalize({
                        "@context": self.context,
                        "@graph": json.loads(graph)
                    },
                    {
                        "format": "application/nquads"
                    }
                )
                return {
                    "data": norm,
                    "format": "n3"
                }
            old = Graph().parse(**ld_args(old))
            new = Graph().parse(**ld_args(new))

            self.graph -= old
            self.graph += new


class InstallerMixin(object):
    '''
    An opinonated mixin for handling static assets associated with IPython
    widgets
    '''

    def __init__(self, install_assets=False, *args, **kwargs):
        '''
        Each time an instance is created:
        - if the nbextension is not installed...
            - copy all assets in `static` to the current profile's nbextensions
        - automagically load any css
        '''

        if install_assets or not check_nbextension([nbextension]):
            # copy the static files to a namespaced location in `nbextensions`
            install_nbextension(static, user=True)

        # magically-named files css/SomeWidgetView.css
        magic_style = os.path.join(static, 'css', '%s.css' % self._view_name)

        styles = getattr(self, '_view_styles', [])
        if os.path.exists(magic_style):
            styles.append('css/%s.css' % self._view_name)
        styles = [
            '/nbextensions/%s/%s' % (nbextension, style)
            for style in styles
        ]

        # tell the front-end to request the assets
        display(Javascript('', css=styles))

        # always call the parent constructor!
        super(InstallerMixin, self).__init__(*args, **kwargs)

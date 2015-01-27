import datetime
import json

from rdflib.namespace import (
    RDFS,
    XSD,
    Namespace,
)
from pyld import jsonld

from IPython.utils.traitlets import (
    Instance,
    Unicode,
    Tuple,
    Dict,
)

from IPython.html import widgets

from .base import (
    InstallerMixin,
    GraphMixin,
)

# Alchemy of Growth
AOG = Namespace("http://www.amazon.com/"
                "The-Alchemy-Growth-Practical-Enterprise/dp/0738203092#")

# some years in the future
DEFAULT_MAX_HORIZON = 52 * 30


class Horizons(InstallerMixin, GraphMixin):
    _view_name = Unicode('HorizonsView', sync=True)
    _view_module = Unicode('/nbextensions/nbmonty/js/widget-horizons.js',
                           sync=True)

    nodes = Tuple([], sync=True)

    title = Unicode("Horizons", sync=True)

    x_label = Unicode("Time", sync=True)
    x_scale = Tuple([
        datetime.datetime.today().isoformat(),
        (
            datetime.datetime.today() +
            datetime.timedelta(weeks=DEFAULT_MAX_HORIZON)
        ).isoformat()
    ], sync=True)

    y_label = Unicode("Value", sync=True)
    y_scale = Tuple([0, 100], sync=True)

    context = Dict({
        "rdfs": str(RDFS),
        "aog": str(AOG),
        "xsd": str(XSD),
        "name": "rdfs:label",
        "x": {
            "@id": "aog:timeOfAttention",
            "@type": "xsd:date"
        },
        "y": "aog:growthInValue"
    })

    def __init__(self, *args, **kwargs):
        super(Horizons, self).__init__(*args, **kwargs)
        self.width = self.width or "100%"
        self.height = self.height or 500

    def _ld_changed(self, name, old, new):
        super(Horizons, self)._ld_changed(name, old, new)
        try:
            node_ld = self.graph.serialize(
                format="json-ld",
                indent=2,
                context=self.context
            ).decode('utf-8')
            self.nodes = json.loads(node_ld)["@graph"]
        except Exception as err:
            print(err)

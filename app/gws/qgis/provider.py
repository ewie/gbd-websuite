import zipfile

import gws
import gws.common.ows.provider
import gws.gis.ows
import gws.config
import gws.tools.xml2
import gws.tools.net
import gws.gis.util

import gws.types as t

from . import types, parser


def create_shared(root: t.IRootObject, cfg) -> 'Object':
    path = cfg.get('path')
    uid = path
    root.application.monitor.add_path(path)
    return root.create_shared_object(Object, uid, t.Config(path=path))


# see https://docs.qgis.org/2.18/en/docs/user_manual/working_with_ogc/ogc_server_support.html#getlegendgraphics-request

_DEFAULT_LEGEND_PARAMS = {
    'BOXSPACE': 2,
    'ICONLABELSPACE': 2,
    'ITEMFONTBOLD': False,
    'ITEMFONTCOLOR': '#000000',
    'ITEMFONTFAMILY': 'DejaVuSans',
    'ITEMFONTITALIC': False,
    'ITEMFONTSIZE': 9,
    'LAYERFONTBOLD': True,
    'LAYERFONTCOLOR': '#000000',
    'LAYERFONTFAMILY': 'DejaVuSans',
    'LAYERFONTITALIC': False,
    'LAYERFONTSIZE': 9,
    'LAYERSPACE': 4,
    'LAYERTITLE': True,
    'LAYERTITLESPACE': 4,
    'RULELABEL': True,
    'SYMBOLHEIGHT': 8,
    'SYMBOLSPACE': 2,
    'SYMBOLWIDTH': 8,
}


class Object(gws.common.ows.provider.Object):
    legend_params: dict
    path: str
    print_templates: t.List[types.PrintTemplate]
    properties: dict
    source_text: str

    def configure(self):
        super().configure()

        self.legend_params = gws.merge(_DEFAULT_LEGEND_PARAMS, self.root.var('server.qgis.legend'))

        self.path = self.var('path')
        self.url = 'http://%s:%s' % (
            self.root.var('server.qgis.host'),
            self.root.var('server.qgis.port'))

        self.type = 'QGIS/WMS'
        self.version = '1.3.0'  # as of QGIS 3.4

        self.print_templates = []
        self.properties = {}

        self.source_text = self._read(self.path)

        parser.parse(self, self.source_text)

    def find_features(self, args: t.SearchArgs) -> t.List[t.IFeature]:
        if not args.shapes:
            return []

        shape = args.shapes[0]
        if shape.type != t.GeometryType.point:
            return []

        our_crs = gws.gis.util.best_crs(shape.crs, self.supported_crs)
        shape = shape.transformed_to(our_crs)

        #  draw a 1000x1000 bbox around a point
        width = 1000
        height = 1000

        bbox = gws.gis.util.make_bbox(
            shape.x,
            shape.y,
            our_crs,
            args.resolution,
            width,
            height
        )

        p = {
            'BBOX': bbox,
            'CRS': self.supported_crs[0],

            'WIDTH': width,
            'HEIGHT': height,
            'I': width >> 1,
            'J': height >> 1,

            'INFO_FORMAT': 'text/xml',
            'LAYERS': args.source_layer_names,
            'MAP': self.path,
            'QUERY_LAYERS': args.source_layer_names,
            'STYLES': [''] * len(args.source_layer_names),

            # @TODO should be configurable

            'FI_LINE_TOLERANCE': 8,
            'FI_POINT_TOLERANCE': 16,
            'FI_POLYGON_TOLERANCE': 4,

            # see https://github.com/qgis/qwc2-demo-app/issues/55
            'WITH_GEOMETRY': 1,
        }

        if args.limit:
            p['FEATURE_COUNT'] = args.limit

        p = gws.merge(p, args.params)

        text = gws.gis.ows.request.get_text(self.url, service='WMS', request='GetFeatureInfo', params=p)
        found = gws.gis.ows.formats.read(text, crs=our_crs)

        if found is None:
            gws.p('QGIS/WMS QUERY', p, 'NOT PARSED')
            return []

        gws.p('QGIS/WMS QUERY', p, f'FOUND={len(found)}')
        return found

    def get_legend(self, source_layers, options=None):
        # qgis legends are rendered bottom-up (rightmost first)
        # we need the straight order (leftmost first), like in the config

        params = gws.merge(self.legend_params, {
            'MAP': self.path,
            'LAYER': ','.join(sl.name for sl in reversed(source_layers)),
            'FORMAT': 'image/png',
            'TRANSPARENT': True,
            'STYLE': '',
            'VERSION': '1.1.1',
            'DPI': 96,
        }, options)

        resp = gws.gis.ows.request.get(
            self.url,
            service='WMS',
            request='GetLegendGraphic',
            params=params)

        return resp.content

    def _read(self, path):
        if path.endswith('.qgz'):
            with zipfile.ZipFile(path) as zf:
                for info in zf.infolist():
                    if info.filename.endswith('.qgs'):
                        with zf.open(info) as fp:
                            return fp.read()

        with open(self.path) as fp:
            return fp.read()

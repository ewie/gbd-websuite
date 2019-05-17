import re

import gws
import gws.gis.layer
import gws.types as t
import gws.gis.source
import gws.tools.misc
import gws.tools.json2

_EPSG_3857_EXTENT = [
    -20037508.342789244,
    -20037508.342789244,
    20037508.342789244,
    20037508.342789244
]


class ServiceConfig:
    """Tile service configuration"""

    extent: t.Optional[t.Extent]  #: service extent
    crs: t.crsref = 'EPSG:3857'  #: service CRS
    origin: str = 'nw'  #: position of the first tile (nw or sw)
    tileSize: int = 256  #: tile size


class Config(gws.gis.layer.ImageTileConfig):
    """Tile layer"""

    maxRequests: int = 0  #: max concurrent requests to this source
    service: t.Optional[ServiceConfig] = {}  #: service configuration
    url: t.url  #: rest url with placeholders {x}, {y} and {z}


class Object(gws.gis.layer.ImageTile):
    def __init__(self):
        super().__init__()

        self.service: ServiceConfig = None
        self.url = ''

    def configure(self):
        super().configure()

        self.url = self.var('url')
        self.service = self.var('service')

        if not self.service.extent:
            if self.service.crs == 'EPSG:3857':
                self.service.extent = _EPSG_3857_EXTENT
            else:
                raise gws.Error(r'service extent required for crs {self.service.crs!r}')

    def mapproxy_config(self, mc, options=None):
        # we use {x} like in Ol, mapproxy wants %(x)s
        url = re.sub(
            r'{([xyz])}',
            r'%(\1)s',
            self.url)

        grid_uid = mc.grid(gws.compact({
            'origin': self.service.origin,
            'bbox': self.service.extent,
            # 'res': res,
            'srs': self.service.crs,
            'tile_size': [self.service.tileSize, self.service.tileSize],
        }))

        src = self.mapproxy_back_cache_config(mc, url, grid_uid)
        self.mapproxy_layer_config(mc, src)
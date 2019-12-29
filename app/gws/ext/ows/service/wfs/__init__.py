import gws
import gws.common.model
import gws.common.ows.service
import gws.common.search.runner
import gws.gis.proj
import gws.gis.render
import gws.gis.shape
import gws.gis.gml
import gws.tools.shell
import gws.tools.xml3
import gws.web.error

import gws.types as t

import gws.common.ows.service as ows


class Config(gws.common.ows.service.Config):
    """WFS Service configuration"""

    pass


VERSION = '2.0'
MAX_LIMIT = 100


class Object(ows.Object):
    def __init__(self):
        super().__init__()

        self.type = 'wfs'
        self.version = VERSION

    @property
    def service_link(self):
        return t.MetaLink({
            'url': self.service_url,
            'scheme': 'OGC:WFS',
            'function': 'download'
        })

    def configure(self):
        super().configure()

        for tpl in 'getCapabilities', 'describeFeatureType', 'getFeature', 'feature':
            self.templates[tpl] = self.configure_template(tpl, 'wfs/templates')

    def handle_getcapabilities(self, rd: ows.RequestData):
        nodes = ows.layer_node_list(rd)
        if self.use_inspire_data:
            nodes = ows.inspire_nodes(nodes)
        return ows.xml_response(self.render_template(rd, 'getCapabilities', {
            'layer_node_list': nodes,
        }))

    def handle_describefeaturetype(self, rd: ows.RequestData):
        nodes = ows.layer_nodes_from_request_params(rd, 'typeName', 'typeNames')
        if self.use_inspire_data:
            nodes = ows.inspire_nodes(nodes)
        if not nodes:
            raise gws.web.error.NotFound()


        if self.use_inspire_data:
            # @TODO inspiure schemas
            pass
        else:
            for node in nodes:
                dm = node.layer.data_model
                node.feature_schema = []
                for a in dm:
                    xtype = ows.ATTR_TYPE_TO_XML.get(a.type or 'str')
                    if xtype:
                        node.feature_schema.append({
                            'name': a.name,
                            'type': xtype
                        })

                gtype = node.layer.geometry_type
                if gtype:
                    node.feature_schema.append({
                        'name': 'geometry',
                        'type': ows.ATTR_TYPE_TO_XML.get(gtype)
                    })

        return ows.xml_response(self.render_template(rd, 'describeFeatureType', {
            'layer_node_list': nodes,
        }))

    def handle_getfeature(self, rd: ows.RequestData):
        nodes = ows.layer_nodes_from_request_params(rd, 'typeName', 'typeNames')
        if self.use_inspire_data:
            nodes = ows.inspire_nodes(nodes)
        if not nodes:
            raise gws.web.error.NotFound()

        try:
            limit = int(rd.req.kparam('count') or rd.req.kparam('maxFeatures') or MAX_LIMIT)
            bbox = rd.project.map.extent
            if rd.req.kparam('bbox'):
                bbox = [float(n) for n in rd.req.kparam('bbox').split(',')[:4]]
        except:
            raise gws.web.error.BadRequest()

        args = t.SearchArgs({
            'shapes': [gws.gis.shape.from_bbox(bbox, rd.project.map.crs)],
            'crs': rd.project.map.crs,
            'project': None,
            'keyword': None,
            'layers': [n.layer for n in nodes],
            'limit': min(limit, MAX_LIMIT),
            'tolerance': 10,
        })

        features = gws.common.search.runner.run(rd.req, args)
        nodes = ows.feature_node_list(rd, features)
        return self.render_feature_nodes(rd, nodes, 'getFeature')

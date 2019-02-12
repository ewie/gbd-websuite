import gws.gis.feature
import gws.tools.json2
import gws.web

import gws.types as t


class Config(t.WithTypeAndAccess):
    """feature edit action"""
    pass


class EditParams(t.Data):
    projectUid: str
    layerUid: str
    features: t.List[t.FeatureProps]


class EditResponse(t.Response):
    features: t.List[t.FeatureProps]


class Object(gws.Object):
    def api_add_features(self, req, p: EditParams) -> EditResponse:
        """Add features to the layer"""

        layer = req.require('gws.ext.layer', p.layerUid)
        fs = layer.add_features(p.features)
        return EditResponse({'features': [f.props for f in fs]})

    def api_delete_features(self, req, p: EditParams) -> EditResponse:
        """Delete features from the layer"""

        layer = req.require('gws.ext.layer', p.layerUid)
        fs = layer.delete_features(p.features)
        return EditResponse({'features': [f.props for f in fs]})

    def api_update_features(self, req, p: EditParams) -> EditResponse:
        """Update features on the layer"""

        layer: t.LayerObject = req.require('gws.ext.layer', p.layerUid)
        if not layer.edit_access(req.user):
            raise gws.web.error.Forbidden()

        fs = layer.update_features(p.features)
        return EditResponse({'features': [f.props for f in fs]})

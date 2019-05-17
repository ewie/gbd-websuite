import gws
import gws.types as t


class OptionsParams(t.Data):
    projectUid: str


class OptionsResponse(t.Response):
    layerUids: t.Optional[t.List[str]]
    pixelTolerance: int = 10


class Config(t.WithTypeAndAccess):
    """Dimension action"""
    layers: t.Optional[t.List[str]]  #: target layer uids
    pixelTolerance: int = 10  #: pixel tolerance


class Object(gws.Object):

    def api_options(self, req, p: OptionsParams) -> OptionsResponse:
        req.require_project(p.projectUid)

        return OptionsResponse({
            'layerUids': self.var('layers') or [],
            'pixelTolerance': self.var('pixelTolerance'),

        })
import gws.common.project
import gws.web
import gws.types as t


class Config(t.WithTypeAndAccess):
    """Project information action"""
    pass


class InfoParams(t.Params):
    pass


class InfoResponse(t.Response):
    project: gws.common.project.Props
    user: t.Optional[t.UserProps]


class Object(gws.ActionObject):
    def api_info(self, req: t.IRequest, p: InfoParams) -> InfoResponse:
        """Return the project configuration"""

        project = req.require_project(p.projectUid)
        return InfoResponse({
            'project': project.props_for(req.user),
            'user': req.user.props
        })

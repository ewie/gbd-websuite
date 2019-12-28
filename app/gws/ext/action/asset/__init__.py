import os

import gws
import gws.common.template
import gws.config
import gws.server
import gws.tools.job
import gws.tools.mime
import gws.tools.misc
import gws.web.error

import gws.types as t


class Config(t.WithTypeAndAccess):
    """Asset generation action"""
    pass


class GetPathParams(t.Params):
    path: str


class GetResultParams(t.Params):
    jobUid: str


class Object(gws.ActionObject):

    def api_get(self, req: gws.web.AuthRequest, p: GetPathParams) -> t.HttpResponse:
        """Return an asset under the given path and project"""
        return self._serve_path(req, p)

    def http_get_path(self, req: gws.web.AuthRequest, p: GetPathParams) -> t.HttpResponse:
        return self._serve_path(req, p)

    def http_get_download(self, req: gws.web.AuthRequest, p) -> t.HttpResponse:
        return self._serve_path(req, p, True)

    def http_get_result(self, req: gws.web.AuthRequest, p: GetResultParams) -> t.HttpResponse:
        job = gws.tools.job.get_for(req.user, p.jobUid)
        if not job or job.state != gws.tools.job.State.complete:
            raise gws.web.error.NotFound()
        with open(job.result, 'rb') as fp:
            content = fp.read()
        return t.HttpResponse({
            'mime': gws.tools.mime.for_path(job.result),
            'content': content
        })

    def _serve_path(self, req: gws.web.AuthRequest, p: GetPathParams, as_attachment=False):
        spath = str(p.get('path') or '')
        if not spath:
            raise gws.web.error.NotFound()

        site_assets = req.site.assets_root

        project = None
        project_assets = None

        project_uid = p.get('projectUid')
        if project_uid:
            project = req.require_project(project_uid)
            project_assets = project.assets_root

        rpath = None

        if project_assets:
            rpath = _abs_path(spath, project_assets.dir)
        if not rpath and site_assets:
            rpath = _abs_path(spath, site_assets.dir)
        if not rpath:
            raise gws.web.error.NotFound()

        if not as_attachment:

            template_type = gws.common.template.type_from_path(rpath)

            if template_type:
                tpl = self.create_shared_object('gws.ext.template', rpath, t.Config({
                    'type': template_type,
                    'path': rpath
                }))

                context = gws.extend(
                    _default_template_context(req, project),
                    params=p)

                tr = tpl.render(context)

                return t.HttpResponse({
                    'mime': tr.mime,
                    'content': tr.content
                })

        mt = gws.tools.mime.for_path(rpath)

        if not _valid_mime_type(mt, project_assets, site_assets):
            gws.log.error(f'invalid mime path={rpath!r} mt={mt!r}')
            # NB: pretend the file doesn't exist
            raise gws.web.error.NotFound()

        gws.log.info(f'serving {rpath!r} for {spath!r}')

        attachment_name = None

        if as_attachment:
            p = gws.tools.misc.parse_path(spath)
            attachment_name = p['name'] + '.' + gws.tools.mime.extension(mt)

        return t.FileResponse({
            'mime': mt,
            'path': rpath,
            'attachment_name': attachment_name,
        })


def _projects_for_user(user):
    ps = [
        p
        for p in gws.config.root().find_all('gws.common.project')
        if user.can_use(p)
    ]
    return sorted(ps, key=lambda p: p.title)


def _abs_path(path, basedir):
    gws.log.debug(f'trying {path!r} in {basedir!r}')
    p = path.strip('/')

    if p.startswith('.') or '/.' in p:
        gws.log.error(f'dotted path={path!r}')
        return None

    p = os.path.abspath(os.path.join(basedir, p))
    if not os.path.isfile(p):
        gws.log.error(f'not a file path={path!r}')
        return None

    if not p.startswith(basedir):
        gws.log.error(f'invalid path={path!r}')
        return None

    return p


def _default_template_context(req, project):
    return {
        'project': project,
        'projects': _projects_for_user(req.user),
        'request': req,
        'user': req.user,
    }


def _valid_mime_type(mt, project_assets, site_assets):
    if project_assets and project_assets.allowMime:
        return mt in project_assets.allowMime
    if site_assets and site_assets.allowMime:
        return mt in site_assets.allowMime
    if mt not in gws.tools.mime.default_allowed:
        return False
    if project_assets and project_assets.denyMime:
        return mt not in project_assets.denyMime
    if site_assets and site_assets.denyMime:
        return mt not in site_assets.denyMime
    return True

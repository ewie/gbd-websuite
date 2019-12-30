import re

import gws
import gws.common.template
import gws.tools.net

import gws.types as t


class CorsConfig(t.Config):
    allowOrigin: str = '*'
    allowCredentials: bool = False
    allowHeaders: t.Optional[t.List[str]]


#:export
class CorsOptions(t.Data):
    allow_origin: str
    allow_credentials: bool
    allow_headers: t.Optional[t.List[str]]


#:export
class RewriteRule(t.Data):
    match: t.Regex  #: expression to match the url against
    target: str  #: target url with placeholders
    options: t.Optional[dict]  #: additional options


class DocumentRootConfig(t.Config):
    """Base directory for assets"""

    dir: t.DirPath  #: directory path
    allowMime: t.Optional[t.List[str]]  #: allowed mime types
    denyMime: t.Optional[t.List[str]]  #: disallowed mime types (from the standard list)


#:export
class DocumentRoot(t.Data):
    dir: t.DirPath
    allow_mime: t.Optional[t.List[str]]
    deny_mime: t.Optional[t.List[str]]


class Config(t.Config):
    """Site (virtual host) configuration"""

    assets: t.Optional[DocumentRootConfig]  #: assets location and options
    cors: t.Optional[CorsConfig]  #: cors configuration
    errorPage: t.Optional[t.ext.template.Config]  #: error page template
    host: str = '*'  #: host name
    reversedRewrite: t.Optional[t.List[RewriteRule]]  #: reversed rewrite rules
    rewrite: t.Optional[t.List[RewriteRule]]  #: rewrite rules
    root: DocumentRootConfig  #: document root location and options


def document_root(cfg: DocumentRootConfig) -> t.Optional[t.DocumentRoot]:
    if not cfg:
        return None
    return t.DocumentRoot({
        'dir': cfg.get('dir'),
        'allow_mime': cfg.get('allowMime'),
        'deny_mime': cfg.get('denyMime'),
    })


#:export IWebSite
class Object(gws.Object, t.IWebSite):
    def __init__(self):
        super().__init__()
        self.host = ''
        self.ssl = False
        self.error_page: t.ITemplate = None
        self.static_root: t.DocumentRoot = None
        self.assets_root: t.DocumentRoot = None
        self.rewrite_rules: t.List[t.RewriteRule] = []
        self.reversed_rewrite_rules: t.List[t.RewriteRule] = []
        self.cors: t.CorsOptions = None

    def configure(self):
        super().configure()

        self.host = self.var('host', default='*')
        self.static_root = document_root(self.var('root'))
        self.assets_root = document_root(self.var('assets'))

        # config.ssl is populated in the application init
        self.ssl = self.var('ssl')

        self.rewrite_rules = self.var('rewrite', default=[])
        for r in self.rewrite_rules:
            if not gws.tools.net.is_abs_url(r.target):
                # ensure rewriting from root
                r.target = '/' + r.target.lstrip('/')

        self.reversed_rewrite_rules = self.var('reversedRewrite', default=[])
        for r in self.reversed_rewrite_rules:
            r.match = str(r.match).strip('/')
            # we use nginx syntax $1, need python's \1
            r.target = r.target.replace('$', '\\')

        p = self.var('errorPage')
        if p:
            self.error_page = self.create_object('gws.ext.template', p)

        self.cors = CorsOptions({
            'allow_origin': self.var('cors.allowOrigin'),
            'allow_credentials': self.var('cors.allowCredentials'),
            'allow_headers': self.var('cors.allowHeaders'),
        })

    def url_for(self, req, url):
        if gws.tools.net.is_abs_url(url):
            return url

        proto = 'https' if self.ssl else 'http'
        host = req.env('HTTP_HOST') if self.host == '*' else self.host
        base = proto + '://' + host

        u = url.lstrip('/')

        for rule in self.reversed_rewrite_rules:
            m = re.match(rule.match, u)
            if m:
                s = re.sub(rule.match, rule.target, u)
                if gws.tools.net.is_abs_url(s):
                    return s
                return base + s

        return base + '/' + u

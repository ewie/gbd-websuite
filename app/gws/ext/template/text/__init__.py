"""CX templates for Text-Only."""

import gws
import gws.common.template
import gws.tools.vendor.chartreux as chartreux

import gws.types as t


class Config(gws.common.template.Config):
    """text-only template"""
    pass


class Object(gws.common.template.Object):

    def render(self, context, format=None):
        context = context or {}

        context['gws'] = {
            'version': gws.VERSION,
            'endpoint': gws.SERVER_ENDPOINT,
        }

        def err(e, path, line):
            gws.log.warn(f'TEMPLATE: {e.__class__.__name__}:{e} in {path}:{line}')

        text = self.text
        if self.path:
            with open(self.path, 'rt') as fp:
                text = fp.read()

        content = chartreux.render(
            text,
            context,
            path=self.path or '<string>',
            error=err,
        )

        return t.Data({'content': content})

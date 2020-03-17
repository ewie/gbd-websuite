import gws.core.tree
import gws.core.spec
import gws.server.monitor
import gws.types as t

from . import error, spec


#:export IRootObject
class Object(gws.core.tree.RootBase, t.IRootObject):
    def configure(self):
        super().configure()

        self._monitor: gws.server.monitor.Object = self.add_child(gws.server.monitor.Object, {})
        self._validator: gws.core.spec.Validator = spec.validator()
        self.application: t.IApplication = self.add_child('gws.common.application', self.config)

    def validate_action(self, category, cmd, payload):
        cc = self._validator.method_spec(cmd)
        if not cc:
            raise error.DispatchError('not found', cmd)

        cat = cc['category']
        if cat == 'http' and category.startswith('http'):
            cat = category
        if category != cat:
            raise error.DispatchError('wrong command category', category)

        if cc['arg']:
            try:
                payload = self._validator.read_value(payload, cc['arg'], strict=(cat == 'api'))
            except gws.core.spec.Error as e:
                raise error.DispatchError(f'invalid parameters ({e.message})') from e

        return cc['action'], cc['name'], payload

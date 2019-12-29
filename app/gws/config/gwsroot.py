import gws.core.tree
import gws.types.spec
import gws.server.monitor
import gws.types as t

from . import error, spec


#:stub RootObject
class Object(gws.core.tree.RootBase):
    def __init__(self):
        super().__init__()

        self.application: t.ApplicationObject = None

        self._validator: gws.types.spec.Validator = None
        self._monitor: gws.server.monitor.Object = None

    def configure(self):
        super().configure()

        self.application = self.add_child('gws.common.application', self.config)
        self._monitor = self.add_child(gws.server.monitor.Object, {})
        self._validator = spec.validator()

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
            except gws.types.spec.Error as e:
                gws.log.exception()
                raise error.DispatchError('invalid parameters') from e

        return cc['action'], cc['name'], payload

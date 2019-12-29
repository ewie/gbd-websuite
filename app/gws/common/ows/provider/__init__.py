import gws
import gws.types as t


#:stub OwsProviderObject
class Object(gws.Object):
    def __init__(self):
        super().__init__()
        self.operations: t.List[t.OwsOperation] = []
        self.meta: t.MetaData = None
        self.source_layers: t.List[t.SourceLayer] = []
        self.supported_crs: t.List[t.Crs] = []
        self.type: str = ''
        self.url: t.Url = ''
        self.version: str = ''

    def find_features(self, args: t.SearchArgs) -> t.List[t.Feature]:
        pass

    def operation(self, name: str) -> t.OwsOperation:
        for op in self.operations:
            if op.name == name:
                return op

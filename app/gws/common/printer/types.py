import gws.types as t
import gws.tools.job


class PrintBitmapItem:
    data: t.Optional[bytes]
    mode: t.Optional[str]
    width: t.Optional[int]
    height: t.Optional[int]
    url: t.Optional[str]


class PrintItem(t.Data):
    bitmap: t.Optional[PrintBitmapItem]
    features: t.Optional[t.List[t.FeatureProps]]
    subLayers: t.Optional[t.List[str]]
    layerUid: t.Optional[str]
    opacity: t.Optional[float]
    printAsVector: t.Optional[bool]
    style: t.Optional[t.StyleProps]
    svgFragment: t.Optional[t.SvgFragment]


class PrintSection(t.Data):
    center: t.Point
    attributes: t.Optional[t.List[t.Attribute]]
    items: t.Optional[t.List[PrintItem]]


class PrintParams(t.Params):
    items: t.List[PrintItem]
    rotation: int
    scale: int
    format: t.Optional[str]
    templateUid: str
    sections: t.Optional[t.List[PrintSection]]
    quality: int
    mapWidth: t.Optional[int]
    mapHeight: t.Optional[int]


class PrinterQueryParams(t.Params):
    jobUid: str


class PrinterResponse(t.Response):
    jobUid: str = ''
    progress: int = 0
    state: gws.tools.job.State
    otype: str = ''
    oname: str = ''
    url: str = ''

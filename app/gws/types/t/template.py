### Templates, renderers and formats.

from .base import List, Optional, Point, Extent, Size, FilePath
from .data import Config, Data, Props
from .attribute import DataModel
from .object import Object
from .ext import ext
from .feature import Feature
from .map import LayerObject
from .style import StyleProps


class TemplateQualityLevel(Data):
    """Quality level for a template"""

    name: str = ''  #: level name
    dpi: int  #: dpi value


class TemplateConfig(Config):
    type: str  #: template type
    qualityLevels: Optional[List[TemplateQualityLevel]]  #: list of quality levels supported by the template
    dataModel: Optional[DataModel]  #: user-editable template attributes
    path: Optional[FilePath]  #: path to a template file
    text: str = ''  #: template content
    title: str = ''  #: template title
    uid: str = ''  #: unique id


class TemplateProps(Props):
    uid: str
    title: str
    qualityLevels: List[TemplateQualityLevel]
    mapHeight: int
    mapWidth: int
    dataModel: DataModel


class TemplateRenderOutput(Data):
    mimeType: str
    content: str
    path: str


class SvgFragment:
    points: List[Point]
    svg: str


class MapRenderInputItem(Data):
    bitmap: str
    features: List['Feature']
    layer: 'LayerObject'
    sub_layers: List[str]
    opacity: float
    print_as_vector: bool
    style: 'StyleProps'
    svg_fragment: dict


class MapRenderInput(Data):
    out_path: str
    bbox: Extent
    rotation: int
    scale: int
    dpi: int
    map_size_px: Size
    background_color: int
    items: List[MapRenderInputItem]


class MapRenderOutputItem(Data):
    type: str
    image_path: str = ''
    svg_elements: List[str] = []


class MapRenderOutput(Data):
    bbox: Extent
    dpi: int
    rotation: int
    scale: int
    items: List[MapRenderOutputItem]


class TemplateObject(Object):
    data_model: DataModel
    map_size: List[int]
    page_size: List[int]

    def dpi_for_quality(self, quality: int) -> int:
        pass

    def render(self, context: dict, render_output: MapRenderOutput = None,
               out_path: str = None, format: str = None) -> TemplateRenderOutput:
        pass

    def add_headers_and_footers(self, context: dict, in_path: str, out_path: str, format: str) -> str:
        pass


class FormatConfig(Config):
    """Feature format"""

    description: Optional[ext.template.Config]  #: template for feature descriptions
    category: Optional[ext.template.Config]  #: feature category
    label: Optional[ext.template.Config]  #: feature label on the map
    dataModel: Optional[DataModel]  #: attribute metadata
    teaser: Optional[ext.template.Config]  #: template for feature teasers (short descriptions)
    title: Optional[ext.template.Config]  #: feature title


class FormatObject(Object):
    category: TemplateObject
    description: TemplateObject
    label: TemplateObject
    teaser: TemplateObject
    title: TemplateObject

    data_model: DataModel

    def apply(self, feature: 'Feature', context: dict = None):
        """Format a feature."""
        pass
from pydantic import BaseModel, ConfigDict
from shapely import MultiLineString


class LineColorPair(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    color: str = "black"  # TODO: this should be some color datatype.. or Enum!


class TransitShape(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    line_and_color: LineColorPair
    shape: MultiLineString

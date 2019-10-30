from typing import Mapping, NamedTuple

from .serializers import SensorDataSerializer


class Property(NamedTuple):
    key: str
    label: str
    description: str


# Map from property keys to properties "n" is mapped to
# Property("n", "level", "sound pressure level")
DATA_PROPERTIES: Mapping[str, Property] = {
    key: Property(key, field.label, field.help_text)  # type: ignore
    for (key, field) in SensorDataSerializer().fields.items()
}

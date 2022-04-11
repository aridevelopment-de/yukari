from typing import List, Optional, Tuple, Any

from yukari.converters.baseconverter import BaseConverter
from yukari.converters.types import SpacedString


class SpacedStringConverter(BaseConverter):
    """
    Converts multiple spaced strings to an object
    """
    CONVERTER_TYPE = SpacedString

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        if self.function_parameter_index != len(self.function_parameters) - 1:
            return None

        return " ".join(arguments), len(arguments)

    @staticmethod
    def representation(data: str) -> str:
        return f"<{data}>"

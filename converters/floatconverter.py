from typing import List, Optional, Tuple, Any

from yukari.converters.baseconverter import BaseConverter


class FloatConverter(BaseConverter):
    """
    Converts strings to floats.
    """
    CONVERTER_TYPE = float

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        if "." in arguments[0] and arguments[0][int(arguments[0].startswith("-")):].replace(".", "", 1).isdecimal():
            return float(arguments[0]), 1
        else:
            return None

    @staticmethod
    def representation(data: str) -> str:
        return f"<{data}>"

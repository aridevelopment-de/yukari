from typing import List, Optional, Tuple, Any

from yukari.converters.baseconverter import BaseConverter


class IntegerConverter(BaseConverter):
    """
    Converts strings to integers.
    """
    CONVERTER_TYPE = int

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        if arguments[0][int(arguments[0].startswith("-")):].isdecimal():
            return int(arguments[0]), 1
        else:
            return None

    @staticmethod
    def representation(data: str) -> str:
        return f"<{data}>"

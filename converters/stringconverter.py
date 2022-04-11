from typing import List, Optional, Tuple, Any

from yukari.converters.baseconverter import BaseConverter


class StringConverter(BaseConverter):
    """
    Converts strings into string objects.
    """

    CONVERTER_TYPE = str

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        return arguments[0], 1

    @staticmethod
    def representation(data: str) -> str:
        return f"<{data}>"
from typing import List, Optional, Tuple, Any

import discord

from yukari.converters.baseconverter import BaseConverter
from utils.static import client


class UserConverter(BaseConverter):
    """
    Converter for discord.User objects.
    """
    CONVERTER_TYPE = discord.User

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        mention = arguments[0]

        if mention.startswith('<@') and mention.endswith('>'):
            mention = mention[2:-1]

            if mention.startswith('!'):
                return None

            mention = mention[1:]

            if not mention.isdecimal():
                return None

            member_id = int(mention)

            if self.message.guild is not None:
                return None

            user = client.get_user(member_id)

            if user is None:
                return None

            return user, 1

        return None

    @staticmethod
    def representation(data: str) -> str:
        return f"@{data}#0000"
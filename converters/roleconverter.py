from typing import List, Optional, Tuple, Any

import discord

from yukari.converters.baseconverter import BaseConverter


class RoleConverter(BaseConverter):
    """
    Converts strings into role objects.
    """

    CONVERTER_TYPE = discord.Role

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        # Format of roles: <@&role_id>
        mention = arguments[0]

        if mention.startswith('<@&') and mention.endswith('>'):
            mention = mention[3:-1]

            if not mention.isdecimal():
                return None

            role_id = int(mention)

            if self.message.guild.id is None:
                return None

            role = self.message.guild.get_role(role_id)

            if role is None:
                return None

            return role, 1

        return None

    @staticmethod
    def representation(data: str) -> str:
        return f"@{data}"

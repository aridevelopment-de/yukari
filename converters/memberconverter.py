from typing import List, Optional, Tuple, Any

import discord

from yukari.converters.baseconverter import BaseConverter


class MemberConverter(BaseConverter):
    """
    Converter for discord.Member objects.
    """
    CONVERTER_TYPE = discord.Member

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        mention = arguments[0]

        if mention.startswith('<@') and mention.endswith('>'):
            mention = mention[2:-1]

            if mention.startswith('!'):
                # If its a nickname
                mention = mention[1:]

                if not mention.isdecimal():
                    return None

                member_id = int(mention)

                if self.message.guild is None:
                    return None

                member = self.message.guild.get_member(member_id)

                if member is None:
                    return None

                return member, 1

        return None

    @staticmethod
    def representation(data: str) -> str:
        return f"@{data}#0000"
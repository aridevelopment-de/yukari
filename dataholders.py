import dataclasses

import discord
from typing import Union

from yukari.enums import EventType
from utils.static import client


class _EventDataHolder:
    """
    Base Class for Event class holders
    """
    EVENT_TYPE: EventType



class ReactionEmoji:
    """
    Wrapper for a discord emoji (only exists because there are two types of reaction add events)
    """
    def __init__(self, name: str, emoji_id: Union[int, None], animated: bool):
        self._name = name
        self._emoji_id = emoji_id
        self._animated = animated
        self._is_guild = emoji_id is not None

    @property
    def name(self) -> str:
        return self._name

    @property
    def emoji_id(self) -> int:
        return self._emoji_id

    @property
    def animated(self) -> bool:
        return self._animated

    @property
    def is_guild(self) -> bool:
        return self._is_guild

    def __str__(self):
        return f"'<{'a' if self.animated else ''}:{self.name}:{self.emoji_id}>'"

    def __repr__(self):
        return f"<ReactionEmoji name={self.name} emoji_id={self.emoji_id} animated={self.animated} is_guild_emoji={self.is_guild}>"

    def __eq__(self, other):
        return self.name == other.name and self.emoji_id == other.emoji_id and self.animated == other.animated

    def __hash__(self):
        return hash((self.name, self.emoji_id, self.animated))


class ReactionAddEvent(_EventDataHolder):
    """
    Event class data holder for the `on_reaction_add` and `on_raw_reaction_add` event
    """
    EVENT_TYPE = EventType.REACTION_ADD

    def __init__(self, author_id: int, message_id: int, channel_id: int, guild_id: Union[int, None], emoji: ReactionEmoji):
        self.author_id = author_id
        self.message_id = message_id
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.emoji = emoji
        self._is_guild = self.guild_id is not None

    async def get_message(self) -> discord.Message:
        return await self.channel.fetch_message(self.message_id)

    @property
    def author(self) -> Union[discord.Member, discord.User]:
        if self.is_guild:
            return self.guild.get_member(self.author_id)
        else:
            return client.get_user(self.author_id)

    @property
    def channel(self) -> discord.TextChannel:
        return client.get_channel(self.channel_id)

    @property
    def guild(self) -> discord.Guild:
        return client.get_guild(self.guild_id)

    @property
    def is_guild(self) -> bool:
        return self._is_guild

    def __str__(self):
        return f'<ReactionAddEvent author={self.author} message_id={self.message_id} emoji={self.emoji}>'

    def __repr__(self):
        return f'<ReactionAddEvent author={self.author} message_id={self.message_id} emoji={self.emoji}>'

import time
from typing import (
    Any,
    ByteString,
    Callable,
    Dict,
    List,
    Union
)

import discord

from yukari.enums import EventType
from yukari.i18n.registry import get_i18n_registry
from utils.logger import get_logger


class CategoryHeader:
    """
    Object that represents a category
    """

    def __init__(
            self,
            string_node: str,
            emoji: str,
            alias: List[str] = None
    ):
        """
        :param string_node: the displayed title string node (will search in global)
        :param emoji: the displayed emoji for that category
        :param alias: a list of aliases for that category
        """

        self.name = None
        self.string_node = string_node
        self.emoji = emoji
        self.alias = alias

        if not self.alias:
            self.alias = []
        else:
            self.alias = list(map(lambda e: e.lower(), alias))

        self.data = {
            "string": self.string_node,
            "emoji": self.emoji,
            "alias": self.alias
        }

    def set_name(self, name: str):
        """
        :param name: the name of the category
        """
        self.name = name
        self.data["name"] = name

    def get_serializable(self) -> Dict[str, Any]:
        """
        :return: The serializable data of this CategoryHeader
        """
        if self.data.get("name") is None:
            get_logger().critical("CategoryHeader.get_serializable() called before CategoryHeader.set_name()")

        return self.data


class CommandHeader:
    """
    This is the CommandHeader
    It's used for registering commands.
    You only need to return a CommandHeader object in the register() function of your command.
    """
    def __init__(
            self,
            permission_string: ByteString,
            *discord_permissions: discord.permissions,
            alias: List[str] = None,
            command_cooldown: int = None,
            argument_cooldown: Dict[str, int] = None,
            only_for_bot_perm=False,
            replace_everyone_mentions=True,
            maintenance=False,
            alias_command_group=False
    ):
        """

        :param permission_string: Bot Permission string. Use PermissionHelper to combine multiple Bot Permissions or see
                                  Permissions class yourself
        :param discord_permissions: Discord permissions like discord.permissions.manage_channel
        :param alias: a list of alias for the command
        :param command_cooldown: the cooldown in seconds on that command
        :param argument_cooldown: a dict, which keys are arguments and values are seconds. Only works on first argument
        :param only_for_bot_perm: if set to true then there won't be any discord permission checks, only bot permission.
                                Should indicate that this command is only for specific bot permissions
        :param replace_everyone_mentions: whetever the input should be cleaned with @everyone's and @here's
        :param maintenance: if set to True, only GOD Permission can use this command. Should display a red ball in n+help
        :param alias_command_group: indicates whetever this command actually contains multiple commands flagged as alias.
        """

        if argument_cooldown is None:
            argument_cooldown = {}

        if alias is None:
            alias = []
        else:
            alias = list(map(lambda e: e.lower(), alias))

        self.invoke = None

        self.data = {
            "invoke": self.invoke,
            "short_desc": None,
            "category": None,
            "cog_cls": None,
            "required_user_perms": permission_string,
            "required_discord_perms": discord_permissions,
            "only_bot_perm": only_for_bot_perm,
            "alias": alias,
            "cooldown": command_cooldown,
            "arg_cooldowns": argument_cooldown,
            "replace_everyone": replace_everyone_mentions,
            "maintenance": maintenance,
            "alias_command_group": alias_command_group
        }

    def get_serializable(self) -> Dict[str, Any]:
        """
        :return: The serializable data of this CommandHeader
        """

        if self.data["cog_cls"] is None:
            raise RuntimeError("Executable is not set at " + self.invoke)

        if self.data["category"] is None:
            raise RuntimeError("Category is not set at " + self.invoke)

        return self.data

    def set_category(self, category: str) -> None:
        """
        :param category: The category name for the command to set
        :return: None
        """

        self.data["category"] = category

    def set_cog_cls(self, cog_cls: Callable) -> None:
        """
        :param cog_cls: The command extending BaseCommand for the cog
        :return: None
        """

        self.data["cog_cls"] = cog_cls

    def set_invoke(self, invoke: str) -> None:
        """
        :param invoke: The invoke for the command to set
        :return: None
        """

        self.invoke = invoke
        self.data["invoke"] = invoke


class SubCommandHeader:
    """
    Header defining a subcommand
    """
    def __init__(
            self,
            name: Union[None, str],
            position: Union[None, int],
            func: Union[None, Callable]
    ):
        self.name = name
        self.position = position
        self.func = func
        self.invoke = None
        self.alias = []
        self.discord_permissions = []
        self.bot_permissions = None
        self.enforce_bot_permissions = None
        self.string_node_key = None
        self.cooldown = None
        self.convert_int = None
        self.convert_boolean = None
        self._next = []

    def get_all(self) -> List[str]:
        """
        :return: A list of all possible names which can be called from the user
        """
        return [self.name, *self.alias]


class SubcommandWrapper:
    """
    Wrapper for a subcommand function. Will be used inside a decorator
    Implements a SubcommandHeader
    Also keeps track of the position and the cooldown
    """
    def __init__(self, func: Callable, name: str):
        self.func = func

        position = 0

        if name:
            if name.count(".") == 0:
                position = 1
            else:
                position = name.count(". ") + 1

        self.header = SubCommandHeader(
            name=name,
            position=position,
            func=func
        )

        self.cooldowns = {}

    def check_cooldown(self, author_id: int) -> bool:
        """
        :param author_id: the id of the user/member to check the cooldown for
        :return: whetever that subcommand cooldown is still there
        """
        if self.header.cooldown is None:
            return False

        now = time.time()

        return author_id in self.cooldowns and now - self.cooldowns[author_id] <= self.header.cooldown

    async def execute(self, cls, message: discord.Message, lang: str, *args: Any, **kwargs: Dict[str, Any]):
        """
        Executes the subcommand function with regard to the cooldown

        :param cls: the class instance of the subcommand function
        :param message: the message object the user sent
        :param lang: the language of the user
        :param args: any other arguments that should be passed to the subcommand function
        :param kwargs: any other keyword arguments that should be passed to the subcommand function
        :return: The result of the subcommand function, whatever that might be
        """
        if self.header.cooldown is None:
            await self.func(cls, message, lang, *args, **kwargs)
        else:
            now = time.time()

            if not self.check_cooldown(message.author.id):
                self.cooldowns[message.author.id] = now
                await self.func(cls, message, lang, *args, **kwargs)
            else:
                seconds_left = round(self.header.cooldown - (now - self.cooldowns[message.author.id]))
                await message.channel.send(content=get_i18n_registry().get("global").query_string(lang, "command_handler.cooldown", seconds_left))


class EventWrapper:
    def __init__(self, func: Callable, event_type: EventType):
        self.func = func
        self.event_type = event_type

    async def execute(self, cls, *args: Any):
        return await self.func(cls, *args)

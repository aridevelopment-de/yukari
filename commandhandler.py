from __future__ import annotations

import time
from typing import Any, AnyStr, Dict, List, Tuple, Union, Callable

import discord

from yukari.basecommand import BaseCommand
from yukari.baseheaders import CategoryHeader
from yukari.logger import LogLevel, get_logger
from yukari.permissions.permissions import PermissionHelper

command_handler_instance = None
category_handler_instance = None


def get_command_handler() -> CommandHandler:
    """
    Util function to retrieve the current CommandHandler instance by any other class
    So you don't need to import from Tendo.py but from this class Instead
    used to avoid Recursive Imports

    :return: CommandHandler instance that was created
    """
    if command_handler_instance is None:
        get_logger().critical("CommandHandler instance is None")

    return command_handler_instance  # noqa


def get_category_handler() -> CategoryHandler:
    """
    Util function to retrieve the current CategoryHandler instance by any other class
    So you don't need to import from Tendo.py but from this class Instead
    used to avoid Recursive Imports

    :return: CommandHandler instance that was created
    """
    if category_handler_instance is None:
        get_logger().critical("CategoryHandler instance is None")

    return category_handler_instance  # noqa


class CategoryHandler:
    """
    This is the CategoryHandler
    It's job is to keep track of every category
    Mostly used for the help command
    """
    def __init__(self):
        global category_handler_instance

        self.categories = []
        category_handler_instance = self

    def register_category(self, categoryHeader: CategoryHeader) -> None:
        """
        Registers a Category via a CategoryHeader
        :param categoryHeader: The categoryHeader object to register
        :return:
        """

        self.categories.append(categoryHeader.get_serializable())
        get_logger().log(LogLevel.INFO, "Registered category " + categoryHeader.name)

    def has_category(self, name) -> bool:
        """
        :param name: the name of a category
        :return: True if that category exists, otherwise None
        """
        for c in self.categories:
            if c["name"].lower() == name.lower() or name.lower() in c["alias"]:
                return True

        return False

    def get_category(self, name) -> Union[Dict, None]:
        """
        :param name: the name of a category
        :return: the category data if the category exists, otherwise None
        """
        for c in self.categories:
            if c["name"].lower() == name.lower() or name.lower() in c["alias"]:
                return c

        return None

    def get_aliases(self) -> List[AnyStr]:
        """
        Helper function for for n+help

        :return: A list of every alias
        """

        aliases = []

        for category in self.get_categories():
            for alias in category["alias"]:
                aliases.append(alias)

        return aliases

    def get_categories(self, sort=False) -> List[Dict[AnyStr, Any]]:
        """
        :param sort: if True, the categories will be sorted by name
        :return: A list of all categories
        """

        if not sort:
            return self.categories
        else:
            return sorted(self.categories, key=lambda x: x["name"])


class CommandHandler:
    """
    This is the CommandHandler which handles the user input, converts it into commands,
    checks for permissions and cooldowns
    """
    def __init__(self, get_guild_lang: Callable, get_user_lang: Callable, user_exists: Callable, get_user_permission: Callable, prefix: List[str] = None):
        global command_handler_instance

        self.commands = {}
        self.cooldowns = {}
        self.prefix = prefix or ["n+"]

        self.get_guild_lang = get_guild_lang
        self.get_user_lang = get_user_lang
        self.user_exists = user_exists
        self.get_user_permission = get_user_permission

        command_handler_instance = self

    async def run_command(self, message: discord.Message) -> Any:
        """
        This function is called directly in on_message or other message events
        and splits the content into arguments, invoke and if there is an alias then also that alias

        :param message: The message itself
        :return:
            None if the message does not starts with the prefix
            otherwise the result of CommandHandler.__run_command is returned
        """
        prefix = self.prefix[0]

        if message.content.startswith(prefix):
            args = message.content[len(prefix):].split()

            if not args:
                return

            command, *args = args
            args = list(map(lambda e: e.lower(), args))

            alias = None

            if self.is_alias(command):
                alias = command
                command = self.get_command_name_by_alias(alias)

            return await self.__run_command(command, args, message, alias=alias)

        return None

    def get_command_permissions(self, command: AnyStr) -> Tuple[Any, Any, Any]:
        """
        :param command: The command name or alias
        :return: The Bot Permissions, Discord Permissions and the boolean whetever only the bot permission should be checked
        """
        cmd = self.get_command(command)
        return cmd["required_user_perms"], cmd["required_discord_perms"], cmd["only_bot_perm"]

    async def execute_command(self, invoke: AnyStr, arguments: List[AnyStr], message: discord.Message, cog_cls: BaseCommand) -> None:
        """
        This function is the last step before actually executing the command.
        It retrieves the user language and checks for permission.

        :param invoke: The command invoke (can be command name or alias)
        :param arguments: The arguments of the command
        :param message: the message object itself
        :param cog_cls: the command class extending BaseCommand
        :return: None (may send a message TODO: change that)
        """
        lang = self.get_guild_lang(message.guild.id)

        if self.user_exists(message.author.id):
            user_language = self.get_user_lang(message.author.id)

            if lang != user_language:
                lang = user_language

        bot_permission, guild_permission, only_bot_perm = self.get_command_permissions(
            invoke if self.is_command(invoke) else self.get_command_name_by_alias(invoke)
        )
        user_permission = self.get_user_permission(message.author.id)

        # If there are maintenance
        if self.get_command(invoke)["maintenance"]:
            if not PermissionHelper.is_god(user_permission):
                return await message.channel.send(embed=discord.Embed(
                    color=0xff0000,
                    description="maintenance"  # FIXME Strings().search_string(lang, "errors:command_maintenance"))
                ))

        # If the user has god permission
        if PermissionHelper.is_god(user_permission):
            return await cog_cls._execute(arguments, message, invoke, lang=lang)

        if not only_bot_perm:
            # Check if the user has the required discord permissions or the required bot permissions
            # The check only checks if the user has one of the provided discord permissions
            if PermissionHelper.has_discord_permissions(message.author, *guild_permission, optional=True) or (
                    PermissionHelper.has_permissions(user_permission, *PermissionHelper.split_to_single_permissions(bot_permission),
                                                     optional=True)):
                return await cog_cls._execute(arguments, message, invoke, lang=lang)
        else:
            # Check if the user has the required bot permissions ignoring the required discord permissions
            if PermissionHelper.has_permissions(user_permission, *PermissionHelper.split_to_single_permissions(bot_permission),
                                                optional=True):
                return await cog_cls._execute(arguments, message, invoke, lang=lang)

        return await message.channel.send(embed=discord.Embed(
            color=0xff0000,
            description="keine permissions"  # FIXME Strings().search_string(lang, "errors:no_command_perm")
        ))

    async def __run_command(
            self, command: AnyStr,
            arguments: List[AnyStr],
            message: discord.Message,
            alias: AnyStr = None) -> List[Union[bool, None, AnyStr]]:
        """
        This is the second step of the whole command processing process. This function is called after run_command
        It's main job is to check whetever this is a real command and also check for cooldown.
        Calls execute_command if possible

        :param command: The original command name
        :param arguments: The command arguments
        :param message: The message object itself
        :param alias: The alias if there is one else None
        :return:
            [False, None] if the command is not a registered command
            [False, string] if tendo could not execute the command. See string for more details
            [True, None] Tendo could execute the command successfully
        """
        invoke = command

        if not alias:
            if not self.is_command(command):
                return [False, None]
        else:
            invoke = alias

        now = time.time()
        author = message.author
        cog_cls = self.get_command(command)["cog_cls"]

        if self.has_command_cooldown(command, author):
            cooldown = self.get_command_cooldown(command, author)

            if now > cooldown:
                self.remove_command_cooldown(command, author)
                self.add_command_cooldown(command, author)

                await self.execute_command(invoke, arguments, message, cog_cls)
                return [True, None]
            else:
                return [False, f"Bitte warte noch {round(cooldown - now, 1)} Sekunde/n, bevor du den Befehl erneut benutzt!"]
        else:
            self.add_command_cooldown(command, author)
            await self.execute_command(invoke, arguments, message, cog_cls)
            return [True, None]

    def is_command(self, command) -> bool:
        """
        Checks if the command is a registered command
        Does not check for the alias
        :param command: The command name
        :return: the command name is a valid command
        """
        return self.commands.__contains__(command) or self.commands.__contains__(command.lower())

    def is_alias(self, alias) -> bool:
        """
        :param alias: The alias
        :return: the alias does belong to a command
        """
        return any([True if alias.lower() in self.commands[c]["alias"] else False for c in self.commands])

    def get_command(self, invoke: AnyStr) -> Dict[AnyStr, Any]:
        """
        Searches for the command by the name or alias
        :param invoke: command name or alias
        :return: result of CommandHeader.get_serializable
        """
        if self.is_command(invoke) and not self.is_alias(invoke):
            return self.commands.get(invoke) if self.commands.get(invoke) is not None else self.commands.get(invoke.lower())
        else:
            for c in self.commands:
                if invoke.lower() in self.commands[c]["alias"]:
                    return self.commands.get(c)

    def get_aliases(self) -> List[AnyStr]:
        """
        Helper function for n+help

        :return: A list of every alias
        """

        aliases = []

        for command in self.get_commands():
            for alias in self.get_command(command)["alias"]:
                aliases.append(alias)

        return aliases

    def get_commands(self, category_name=None) -> List[AnyStr]:
        """
        :param category_name: The category name
        :return: every command if category is None else every command name in that category
        """

        if category_name is not None:
            return [cmd for cmd in self.commands if self.commands[cmd]["category"] == category_name]
        else:
            return list(self.commands.keys()).copy()

    def get_command_name_by_alias(self, alias: AnyStr) -> Union[AnyStr, None]:
        """
        :param alias: the alias of a command
        :return: the command name if the command was found else None
        """
        for c in self.commands:
            if alias.lower() in self.commands[c]["alias"]:
                return c

        return None

    def register_command(self, cog_cls: BaseCommand, cog_name: str) -> None:
        """
        Registers a command class with a set command header

        :param cog_cls: The CommandClass of the command
        :param cog_name: The command group name
        :return: None
        """
        header = cog_cls._header  # noqa
        invoke = header.invoke

        if self.is_command(invoke):
            get_logger().log(LogLevel.WARNING, invoke + " is already defined as command! Error catched in " + cog_name)
            raise SyntaxWarning(invoke + " is already a command!")

        self.commands[invoke] = header.get_serializable()
        get_logger().log(LogLevel.INFO, f"\tRegistered command {invoke}")

    def add_command_cooldown(self, command: AnyStr, user: Union[discord.Member, discord.User]) -> None:
        """
        Adds the command cooldown from the command to that user

        :param command: command name
        :param user: discord user, can be type of user or member, depends on the channel type
        :return: None
        """
        if not self.cooldowns.__contains__(str(user.id)):
            self.cooldowns[str(user.id)] = {}

        cmd = self.commands.get(command.lower())

        if not cmd["cooldown"]:
            return

        if self.cooldowns[str(user.id)].__contains__(command.lower()):
            self.cooldowns[str(user.id)][command.lower()]["command_cooldown"] = time.time() + cmd["cooldown"]
        else:
            self.cooldowns[str(user.id)][command.lower()] = {
                "command_cooldown": time.time() + cmd["cooldown"]
            }

    def has_command_cooldown(self, command: AnyStr, user: Union[discord.Member, discord.User]) -> bool:
        """
        :param command: The command name
        :param user: discord user, can be type of user or member, depends on the channel type
        :return: whetever that user has a cooldown on that command
        """
        if not self.cooldowns.__contains__(str(user.id)):
            return False

        if not self.cooldowns[str(user.id)].__contains__(command.lower()):
            return False

        if not self.cooldowns[str(user.id)][command.lower()].__contains__("command_cooldown"):
            return False

        return True

    def is_in_cooldown(self, user: Union[discord.Member, discord.User]) -> bool:
        """
        :param user: discord user, can be type of user or member, depends on the channel type
        :return: whetever that discord user has a cooldown (can be command and argument cooldown)
        """
        return self.cooldowns.__contains__(user)

    def get_command_cooldown(self, command: AnyStr, user: Union[discord.Member, discord.User]) -> int:
        """
        :param command: the command name
        :param user: discord user, can be type of user or member, depends on the channel type
        :return: The whole command cooldown
        """
        if not self.has_command_cooldown(command, user) or self.is_in_cooldown(user):
            return 0

        return self.cooldowns[str(user.id)][command.lower()]["command_cooldown"]

    def remove_command_cooldown(self, command: AnyStr, user: Union[discord.Member, discord.User]) -> None:
        """
        Removes a command cooldown from a user

        :param command:
        :param user:
        :return: None
        """
        if self.has_command_cooldown(command, user):
            self.cooldowns[str(user.id)][command].pop("command_cooldown")

            self.clean_cooldown(command, user)

    def clean_cooldown(self, command: AnyStr, user: Union[discord.Member, discord.User]) -> None:
        """
        Cleans every cooldown from a user
        Cleaning means checking if theres e.g. no command cooldown in the list left in order to save some data

        :param command: The command name
        :param user: discord user, can be type of user or member, depends on the channel type
        :return: None
        """
        if self.cooldowns.__contains__(str(user.id)):
            if self.cooldowns[str(user.id)].__contains__(command.lower()):
                if len(self.cooldowns[str(user.id)][command.lower()].keys()) == 0:
                    self.cooldowns[str(user.id)].pop(command.lower())

    def remove_cooldown(self, user: Union[discord.Member, discord.User]) -> None:
        """
        Removes every cooldown from a user

        :param user: discord user, can be type of user or member, depends on the channel type
        :return: None
        """
        if self.cooldowns.__contains__(str(user.id)):
            self.cooldowns.pop(str(user.id))

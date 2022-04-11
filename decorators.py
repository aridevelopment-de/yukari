from yukari.baseheaders import EventWrapper, SubcommandWrapper
from yukari.enums import EventType
from utils.logger import LogLevel, get_logger
from utils.permissions import PermissionHelper, PermissionHolder


def SubCommand(name: str = ""):
    """
    SubCommand decorator for registering a subcommand

    :param name: the name of the subcommand including every other subcommand before that subcommand
                seperated by an exclamation point
                e.g. config.auto_spam.mail
    :return: SubcommandWrapper class containing the function
    """

    def inner(func):
        return SubcommandWrapper(func, name)

    return inner


def Alias(*alias: str):
    """
    Alias decorator used for setting the preferred alias specified in the command header

    :param alias: A list of aliases
    :return: a descriptor
    """

    def inner(func):
        if not isinstance(func, SubcommandWrapper):
            get_logger().critical("Subcommand was not initialized with SubCommand decorator")

        if func.header.name != "":
            func.header.alias = alias
        else:
            get_logger().critical("Cannot set alias on a subcommand being at the first place")

        return func

    return inner


def Invoke(invoke: str):
    """
    Invoke decorator for setting the preferred alias specified in the command header

    :param invoke: The provided command name (invoke)
    :return: a descriptor
    """

    def inner(func):
        if not isinstance(func, SubcommandWrapper):
            get_logger().log(LogLevel.CRITICAL, "Subcommand was not initialized with SubCommand decorator")
            raise RuntimeError("See logger exception")

        func.header.invoke = invoke

        return func

    return inner


def Translation(query: str):
    """
    Translation decorator for setting the string query used in the help command

    :param query: The provided string query for the help command
    :return: a descriptor
    """

    def inner(func):
        if not isinstance(func, SubcommandWrapper):
            get_logger().log(LogLevel.CRITICAL, "Subcommand was not initialized with SubCommand decorator")
            raise RuntimeError("See logger exception")

        func.header.string_node_key = query

        return func

    return inner


def Cooldown(seconds: int):
    """
    Cooldown decorator used to indicate the amount of seconds a user waits between each execution

    :param seconds: the amount of seconds the user has to wait
    :return: a descriptor
    """

    def inner(func):
        if not isinstance(func, SubcommandWrapper):
            get_logger().log(LogLevel.CRITICAL, "Subcommand was not initialized with SubCommand decorator")
            raise RuntimeError("See logger exception")

        func.header.cooldown = seconds

        return func

    return inner


def PermissionUnion(*general_permissions: bytes, enforce_bot_permissions: bool = False):
    """
    Permission decorator used to indicate general permissions
    These include discord permissions and bot permissions

    The CommandHandler will only check if the member has one of the provided discord permission and bot permissions

    :param general_permissions: A list of discord permissions
    :param enforce_bot_permissions: Indicates whetever only bot permissions should be checked
    :return: a descriptor
    """

    def inner(func):
        if not isinstance(func, SubcommandWrapper):
            get_logger().log(LogLevel.CRITICAL, "Subcommand was not initialized with SubCommand decorator")
            raise RuntimeError("See logger exception")

        _bot_permissions = []
        _discord_permissions = []

        # TODO: Add checks if its a valid discord permission (even exists), otherwise throw an error
        for permission in general_permissions:
            if isinstance(permission, PermissionHolder):
                _bot_permissions.append(permission)
            else:
                _discord_permissions.append(permission)

        _bot_permissions = PermissionHelper.create_permission(*_bot_permissions)

        func.header.discord_permissions = _discord_permissions
        func.header.bot_permissions = _bot_permissions
        func.header.enforce_bot_permissions = enforce_bot_permissions

        return func

    return inner


def Event(event_type: EventType):
    """
    Event decorator used for standalone event class bound methods

    :param event_type: The event type
    :return:
    """

    def inner(func):
        return EventWrapper(func, event_type)

    return inner
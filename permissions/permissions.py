from typing import (
    AnyStr,
    ByteString,
    List,
    Union
)

import discord
from discord import Permissions as DiscordPermission


class PermissionHolder(bytes):
    """
    This class is used to differentiate between discord permissions and bot permissions
    """
    pass


class Permission:
    """
    Permission Enum
    Every bit indicates a specific permission
    """
    BOT_ADMIN = PermissionHolder(b'0001')
    BOT_MOD = PermissionHolder(b'0010')
    BOT_VIP = PermissionHolder(b'0100')
    BOT_USER = PermissionHolder(b'1000')

    LIST = (BOT_USER, BOT_VIP, BOT_MOD, BOT_ADMIN)
    GOD = (BOT_ADMIN,)

    ALL = PermissionHolder(b'1111')
    NONE = PermissionHolder(b'0000')


class PermissionHelper:
    """
    Discord Permissions are often not as optional marked because you need to have some perms at the same time
    in order to execute something

    Bot Permissions are different
    They are sorted by the level means if I have bot admin, I have all rights and can do everything
    so most time they are optional

    """

    @classmethod
    def split_to_single_permissions(cls, perm: Union[AnyStr, ByteString, bytes]) -> List[Union[AnyStr, ByteString, bytes]]:
        """
        Splits a permission bit like "1101" into all its permissions like
        ["1000", "0100", "0001"]

        :param perm: provided permission
        :return: A list of every permission
        """
        if isinstance(perm, bytes):
            perm = perm.decode("utf-8")

        new_perms = []
        all_perms = list(map(lambda e: e.decode("utf-8"), Permission.LIST))
        for i, bit in enumerate(list(perm)):
            if bit == "0":
                continue

            bit = "0" * i + bit + ("0" * (len(perm) - (i + 1)))
            idx = all_perms.index(bit)

            new_perms.append(Permission.LIST[idx])

        return new_perms

    @classmethod
    def __has_one_discord_permission(cls, member: discord.Member, *check_perms: DiscordPermission) -> bool:
        """
        This function shouldn't be used from outside.
        Use has_discord_permissions instead!

        :param member: a member
        :param check_perms: list of discord permissions
        :return: whetever that member has ONE of the discord permissions
        """
        user_perms = member.guild_permissions
        return any([perm.flag & user_perms.value == perm.flag for perm in check_perms])  # noqa

    @classmethod
    def has_discord_permissions(cls, member: discord.Member, *check_perms: DiscordPermission, optional=False) -> bool:
        """
        :param member: a discord member
        :param check_perms: a list of discord permissions
        :param optional: if set to True, only one permission of the discord permissions is required,
                        otherwise, all permissions are required!
        :return: whetever that member has every permission of the discord permissions or only one of them
                (depends on optional value)
        """

        if len(check_perms) == 0:
            return True

        if optional:
            return any([cls.__has_one_discord_permission(member, perm) for perm in check_perms])

        return not any([not cls.__has_one_discord_permission(member, perm) for perm in check_perms])

    @classmethod
    def is_god(cls, perm: Union[AnyStr, ByteString, bytes]) -> bool:
        """
        :param perm: a permission string
        :return: checks whetever that permission string has the god permission
        """
        return cls.has_permissions(perm, *Permission.GOD, optional=True)

    @classmethod
    def add(cls, perm1: Union[AnyStr, bytes, ByteString], perm2: Union[AnyStr, bytes, ByteString]) -> Union[AnyStr, ByteString, bytes]:
        """
        Concatenates two permission strings together and returns them

        :param perm1: a permission string
        :param perm2: a permission string
        :return: the concatenated permission string
        """
        return cls.to_permission_string(int(perm1, 2) ^ int(perm2, 2))

    @classmethod
    def has_single_bit_permission(
            cls,
            needed_single_bit_perm: Union[AnyStr, ByteString, bytes],
            perm: Union[AnyStr, ByteString, bytes]
    ) -> bool:
        """
        Checks if the single bit permission is in the user permission
        for example the needed permission is "0100" and the user permission
        is "1101" then this would return true because the 1 in the
        needed permission which overlaps with the 1 in the user permission

        :param needed_single_bit_perm: the needed single bit in a 4 char permission string format
        :param perm: the permission string to check for
        :return: whetever the needed permission bit is available in the permission string
        """

        return int(needed_single_bit_perm, 2) & int(perm, 2) == int(perm, 2)

    @classmethod
    def has_permissions(
            cls,
            permission_string: Union[AnyStr, ByteString, bytes],
            *args: Union[AnyStr, ByteString, bytes],
            optional: bool = False
    ) -> bool:
        """
        Checks if the permission string contains one or all of the following permissions

        :param permission_string:
        :param args:
        :param optional: if set, only one permission of the permission string is required.
                        If not set, all permissions are required!
        :return: False if the permission string is none or the permission string does not contain the required permissions else True
        """

        if permission_string is None:
            return False

        args = list(map(lambda e: e.decode("utf-8"), args))

        if not args:
            return True

        if optional:
            return any([cls.has_single_bit_permission(permission_string, bit.encode("utf-8")) for bit in args])

        return not any([not cls.has_single_bit_permission(permission_string, bit.encode("utf-8")) for bit in args])

    @classmethod
    def create_permission(cls, *args: Union[AnyStr, ByteString, bytes]) -> Union[AnyStr, ByteString, bytes]:
        """
        Creates a permission with single permission Bits like Permission.BOT_ADMIN, Permission.VIP, etc.
        :param args: the single bit permissions
        :return: the new permission string
        """
        string = int(Permission.NONE, 2)

        for permission_string in args:
            string ^= int(permission_string, 2)

        return cls.to_permission_string(string)

    @classmethod
    def to_permission_string(cls, perm_int: Union[AnyStr, ByteString, bytes, int]) -> Union[AnyStr, ByteString, bytes]:
        """
        Converts a type of permission string/int to a permission string

        :param perm_int: the permission integer (integer in the meaning of bits not type)
        :return: a permission string
        """
        return bin(perm_int)[2:].zfill(len(Permission.NONE))

from __future__ import annotations

from typing import Any, List, Optional


class Optionable(dict):
    """
    Base class for option classes
    NOTE: The name Optionable is misleading because it actually means "options"
    """
    def is_set(self, key: str) -> bool:
        """
        :param key: the key to search for
        :return: whetever that key has been set in the dictionary
        """
        return self.__contains__(key)

    def set(self, key: str, value: Any) -> None:  # noqa: A003
        """
        Shorthand for assigning values in a dictionary

        :param key: the key
        :param value: the value
        """
        self[key] = value

    def get_or_none(self, key: str) -> Optional[Any]:
        """
        Returns the result if its a result in the dictionary otherwise None
        FIXME: There is a default parameter in dict.get

        :param key: the key to look for
        :return: the corresponding value or None
        """
        if self.is_set(key):
            return self.get(key)

        return None


class GuildOptions(Optionable):
    """
    Wrapper object for options in a db guild document
    """

    def get_levelroles(self) -> Optional[dict]:
        """
        :return: a dict of levelroles where the key indicates the level and the value the role id
        """
        return self.get_or_none("levelroles")

    def get_join_message(self) -> Optional[str]:
        """
        :return: the join message of a server
        """
        return self.get_or_none("join_msg")

    def get_leave_message(self) -> Optional[str]:
        """
        :return: the leave message of a server
        """
        return self.get_or_none("leave_msg")

    def get_autorole(self) -> Optional[int]:
        """
        :return: the automatic role id of a server
        """
        return self.get_or_none("autorole")

    def get_birthdayrole(self) -> Optional[int]:
        """
        :return: the birthdayrole id of a server
        """
        return self.get_or_none("birthdayrole")

    def get_birthday_channel(self) -> Optional[int]:
        """
        :return: the birthday annoucement channel id of a server
        """
        return self.get_or_none("birthday_channel")

    def get_level_system_activated(self) -> Optional[bool]:
        """
        :return: whetever the level system is activated on that server
        """
        return self.get_or_none("has_level_system")

    def set_levelroles(self, levelroles: Optional[dict]) -> GuildOptions:
        """
        :param levelroles: a dict of levelroles where the key indicates the level and the value the role id
        :return: the updated version of itself
        """
        self.set("levelroles", levelroles)
        return self

    def set_join_message(self, message: Optional[str]) -> GuildOptions:
        """
        :param message: the member join message
        :return: the updated version of itself
        """
        self.set("join_msg", message)
        return self

    def set_leave_message(self, message: Optional[str]) -> GuildOptions:
        """
        :param message: the member leave message
        :return: the updated version of itself
        """
        self.set("leave_msg", message)
        return self

    def set_autorole(self, new_id: Optional[int]) -> GuildOptions:
        """
        :param new_id: the new id for the automatic role
        :return: the updated version of itself
        """
        self.set("autorole", new_id)
        return self

    def set_birthdayrole(self, new_id: Optional[int]) -> GuildOptions:
        """
        :param new_id: the new id for the birthday role
        :return: the updated version of itself
        """
        self.set("birthdayrole", new_id)
        return self

    def set_birthday_channel(self, new_id: Optional[int]) -> GuildOptions:
        """
        :param new_id: the new id for the birthday channel
        :return: the updated version of itself
        """
        self.set("birthday_channel", new_id)
        return self

    def set_level_system_activated(self, activated: bool) -> GuildOptions:
        """
        :param activated: the new state indicating whetever the level system is activated on that server
        :return: the updated version of itself
        """
        self.set("has_level_system", activated)
        return self


class UserOptions(Optionable):
    """
    Wrapper object for options in a db user document
    """

    def get_birthday_announced(self) -> Optional[bool]:
        """
        :return: whetever the birthday of that user already got announced
        """
        return self.get_or_none("birthday_announced")

    def get_warns(self, guild_id: int) -> List[dict]:
        """
        :param guild_id: the id of the guild where the user have been warned in
        :return: a list of dicts containing the values for the keys `time` (str), `author` (id) and `reason` (str)
        """
        data = (self.get_or_none("warns") or {str(guild_id): []})

        if not str(guild_id) in data:
            return []

        return data[str(guild_id)]

    def set_birthday_announced(self, value: bool) -> UserOptions:
        """
        :param value: whetever the birthday got announced or not
        :return: the updated version of itself
        """
        self.set("birthday_announced", value)
        return self

    def add_warn(self, guild_id: int, warn: dict) -> UserOptions:
        """
        :param guild_id: the guild id to add the warn for
        :param warn: a dict containing the values for the keys `time` (str), `author` (id) and `reason` (str)
        :return: the updated version of itself
        """
        warns = self.get_warns(guild_id)
        warns.append(warn)
        self.set_warns(guild_id, warns)

        return self

    def set_warns(self, guild_id: int, warns: List[dict]) -> UserOptions:
        """
        :param guild_id: the guild id to set the warns for
        :param warns: a list of dicts containing the values for the keys `time` (str), `author` (id) and `reason` (str)
        :return: the updated version of itself
        """
        self.set("warns", {str(guild_id): warns})
        return self


class UserProfile(Optionable):
    """
    Wrapper object for the profile in a db user document
    """
    def get_description(self) -> str:
        """
        :return: the user description
        """
        return self.get_or_none("description")

    def get_birthday(self) -> Optional[str]:
        """
        :return: the birthday in the format "%d.%m"
        """
        return self.get_or_none("birthday")

    def get_banner(self) -> Optional[str]:
        """
        :return: the url of the banner (ends in a valid image extension)
        """
        return self.get_or_none("banner")

    def get_reputations(self) -> Optional[int]:
        """
        :return: The amount of reputations the user has
        """
        return self.get_or_none("reputations")

    def get_joined_tendo_since(self) -> str:
        """
        :return: The date the user first interacted with Tendo
        """
        return self.get_or_none("joined_tendo_since")

    def get_socials(self) -> List[List[str]]:
        """
        Returns the list of social media links

        :return: a list of lists, where each list contains the social media type name, the profile name and the url of a social media
        Example: ["Reddit", "AriOnFire", "https://www.reddit.com/user/AriOnFire"]
        """

        return self.get_or_none("social")

    def get_badges(self) -> List:
        """
        :return: a list of badges (not implemented yet)
        """
        return self.get_or_none("badges")

    def set_description(self, new_description: str) -> UserProfile:
        """
        Sets the new description of the user.

        :param new_description: the new description
        :return: the updated version of itself
        """
        self.set("description", new_description)
        return self

    def set_birthday(self, new_birthday: str) -> UserProfile:
        """
        Sets the birthday of the user.

        :param new_birthday: the new birthday in the format of "%d.%m"
        :return: the updated version of itself
        """
        self.set("birthday", new_birthday)
        return self

    def set_banner(self, new_banner: str) -> UserProfile:
        """
        Sets the banner of the user profile.

        :param new_banner: the new banner url. Has to end in a valid image extension.
        :return: the updated version of itself
        """
        self.set("banner", new_banner)
        return self

    def inc_reputation(self, factor: int = 1) -> UserProfile:
        """
        Increases the reputation of a user by the factor given

        :param factor: the factor by which the reputation should be increased (default: 1)
        :return: the updated version of itself
        """
        self.set("reputations", self.get_reputations() + factor)
        return self

    def set_reputations(self, new_reputations: int) -> UserProfile:
        """
        Sets the reputation value of a user

        :param new_reputations: the new reputation value
        :return: the updated version of itself
        """
        self.set("reputations", new_reputations)
        return self

    def set_joined_tendo_since(self, new_joined_tendo_since: str) -> UserProfile:
        """
        Sets the date when a user first interacted with tendo

        :param new_joined_tendo_since: The date in the format of "%d.%m.%Y/%H:%M"
        :return: the updated version of itself
        """
        self.set("joined_tendo_since", new_joined_tendo_since)
        return self

    def add_social(self, new_social: List[str]) -> UserProfile:
        """
        Adds a single social media information to the user profile.

        :param new_social: a list of length 3, where the first element is the social media type name, the second element is the profile name and the third element is the url
        :return: the updated version of itself
        """
        socials = self.get_socials()
        socials.append(new_social)
        self.set_socials(socials)
        return self

    def remove_social(self, social_name: str) -> UserProfile:
        """
        Removes a single social media information from the user profile

        :param social_name: the name of the social media type to remove (e.g. "Reddit")
        :return: the updated version of itself
        """
        socials = self.get_socials()
        socials = [social for social in socials if social[0] != social_name]
        self.set_socials(socials)
        return self

    def set_socials(self, new_socials: List[List[str]]) -> UserProfile:
        """
        Sets the whole social media information of the user profile

        :param new_socials: a list of lists, where each list contains the social media type name, the profile name and the url of a social media
        :return: the updated version of itself
        """
        self.set("socials", new_socials)
        return self

    def set_badges(self, new_badges: List) -> UserProfile:
        """
        Sets the whole badges of the user profile

        :param new_badges: a list containing the badges (not implemented yet)
        :return: the updated version of itself
        """
        self.set("badges", new_badges)
        return self

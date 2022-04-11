import datetime
import os
from typing import Any, Union, Optional

from dotenv import load_dotenv
from pymongo import MongoClient

from yukari.database.holders import GuildOptions, UserOptions, UserProfile
from yukari.permissions.permissions import Permission, PermissionHelper, PermissionHolder
from yukari.logger import get_logger

load_dotenv()

cur_db = None


class Users:
    """
    Wrapper of the Users collection
    Not every key/value pair has their method entry in this Wrapper.
    You may need to call get_users().collection and use methods on that in order to get an entry you want to have.
    Mind that!
    """

    def __init__(self, collection):
        self.collection = collection

    def exists(self, user_id: int) -> bool:
        """
        :param user_id: A user id
        :return: whetever that user exists in our database
        """
        return self.collection.find_one({"id": user_id}) is not None

    def leveling_server_exists(self, user_id: int, guild_id: int) -> Optional[bool]:
        """
        :param user_id: a user id
        :param guild_id: a guild id
        :return: None if the user doesn't exists else whetever that guild exists in the user leveling table
        """
        if not self.exists(user_id):
            return None

        return str(guild_id) in self.collection.find_one({"id": user_id})["leveling"]

    def add_leveling_server(self, user_id: int, guild_id: int) -> None:
        """
        Adds a leveling server into the user leveling table

        :param user_id: the user id
        :param guild_id: the guild id
        :return: None
        """
        if not self.exists(user_id):
            return None

        self.collection.update_one({"id": user_id}, {"$set": {"leveling." + str(guild_id): [0, 0]}})

    def remove_leveling_server(self, user_id: int, guild_id: int) -> None:
        """
        Removes a leveling server from the user leveling table

        :param user_id: the user id
        :param guild_id: the guild id
        :return: None
        """
        if not self.exists(user_id):
            return None

        self.collection.update_one({"id": user_id}, {"$unset": "leveling." + str(guild_id)})

    def remove_leveling_server_from_all(self, guild_id: int) -> None:
        """
        Removes the leveling server from every user leveling table
        Warning: Only use this function if really needed! It may produce lags.

        :param guild_id: the guild id
        :return: None
        """
        self.collection.update_many({"leveling." + str(guild_id): {"$exists": True}}, {"$unset": {"leveling." + str(guild_id): ""}})

    def set_exp(self, user_id: int, guild_id: int, exp: int) -> None:
        """
        Sets the exp from a user

        :param user_id: the user id
        :param guild_id: the guild id
        :param exp: the amount of xp to set
        :return: None
        """
        if not self.exists(user_id):
            return None

        if not self.leveling_server_exists(user_id, guild_id):
            self.add_leveling_server(user_id, guild_id)

        self.collection.update_one({"id": user_id}, {"$set": {"leveling." + str(guild_id) + ".0": exp}})

    def set_level(self, user_id: int, guild_id: int, lvl: int) -> None:
        """
        Sets the level of a given user

        :param user_id: the user id
        :param guild_id: the guild id
        :param lvl: the level to set to
        :return: None
        """
        if not self.exists(user_id):
            return None

        if not self.leveling_server_exists(user_id, guild_id):
            self.add_leveling_server(user_id, guild_id)

        self.collection.update_one({"id": user_id}, {"$set": {"leveling." + str(guild_id) + ".1": lvl}})

    def add_exp(self, user_id: int, guild_id: int, exp: int) -> None:
        """
        Adds xp to a given user

        :param user_id: the user id
        :param guild_id: the guild id
        :param exp: the exp to increase
        :return: None
        """
        if not self.exists(user_id):
            return None

        if not self.leveling_server_exists(user_id, guild_id):
            self.add_leveling_server(user_id, guild_id)

        self.collection.update_one({"id": user_id}, {"$inc": {"leveling." + str(guild_id) + ".0": exp}})

    def inc_level(self, user_id: int, guild_id: int, increase=1) -> None:
        """
        Increases the level of a given user

        :param user_id: the user id
        :param guild_id: the guild id
        :param increase: the amount of level to increase
        :return: None
        """
        if not self.exists(user_id):
            return None

        if not self.leveling_server_exists(user_id, guild_id):
            self.add_leveling_server(user_id, guild_id)

        self.collection.update_one({"id": user_id}, {"$inc": {"leveling." + str(guild_id) + ".1": increase}})

    def get_exp(self, user_id: int, guild_id: int) -> Union[None, int]:
        """
        :param user_id: the user id
        :param guild_id: the guild id
        :return: None if the user doesn't exists else the current xp that user have
        """

        if not self.exists(user_id):
            return None

        if not self.leveling_server_exists(user_id, guild_id):
            self.add_leveling_server(user_id, guild_id)

        return self.collection.find_one({"id": user_id})["leveling"][str(guild_id)][0]

    def get_level(self, user_id: int, guild_id: int) -> Union[None, int]:
        """
        :param user_id: the user id
        :param guild_id: the guild id
        :return: None if the user doesn't exists else the current level that user have
        """
        if not self.exists(user_id):
            return None

        if not self.leveling_server_exists(user_id, guild_id):
            self.add_leveling_server(user_id, guild_id)

        return self.collection.find_one({"id": user_id})["leveling"][str(guild_id)][1]

    def delete_user(self, user_id: int) -> None:
        """
        Deletes a user in the database

        :param user_id: the user id
        :return: None
        """
        if not self.exists(user_id):
            return None

        self.collection.delete_one({"id": user_id})

    def get_language(self, user_id: int) -> Optional[str]:
        """
        :param user_id: The user id
        :return: None if the user doesn't exists else the preferred language of that user
        """
        if not self.exists(user_id):
            return None

        return self.collection.find_one({"id": user_id})["preferred_language"]

    def get_perm(self, user_id: int) -> Union[None, PermissionHolder]:
        """
        :param user_id: the user id
        :return: the permission string of that user in bytes if the user exists otherwise None
        """
        if not self.exists(user_id):
            return None

        return PermissionHolder((self.collection.find_one({"id": user_id})["permissions"]).encode())

    def get_options(self, user_id: int) -> Union[None, UserOptions]:
        """
        :param user_id: the user id
        :return: a UserOptions object working as a wrapper for the database if the user exists otherwise None
        """
        if not self.exists(user_id):
            return None

        return UserOptions(self.collection.find_one({"id": user_id})["options"])

    def set_options(self, user_id: int, options: UserOptions) -> None:
        """
        Sets the updated UserOptions object

        :param user_id: the user id
        :param options: the UserOptions wrapper object
        :return: None
        """
        if not self.exists(user_id):
            return None

        self.collection.update_one({"id": user_id}, {"$set": {"options": options}})

    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        :param user_id: the user id
        :return: a UserProfile object working as a wrapper for the database if the user exists otherwise None
        """
        if not self.exists(user_id):
            return None

        return UserProfile(self.collection.find_one({"id": user_id})["profile"])

    def set_user_profile(self, user_id: int, profile: UserProfile) -> None:
        """
        Sets the updated UserProfile object

        :param user_id: the user id
        :param profile: the UserProfile wrapper object
        :return: None
        """
        if not self.exists(user_id):
            return None

        self.collection.update_one({"id": user_id}, {"$set": {"profile": profile}})

    def insert_default_user(self, user_id: int, guild_id: int = None, preferred_language="de") -> None:
        """
        Inserts a pre-defined user

        :param user_id: the user id
        :param guild_id: a leveling server if given
        :param preferred_language: the preferred language
        :return: None
        """
        if self.exists(user_id):
            return

        leveling_data = {}

        if guild_id:
            leveling_data[str(guild_id)] = [0, 0]
            preferred_language = get_db().get_guilds().get_lang(guild_id)

        self.collection.insert_one({
            "id": user_id,
            "permissions": PermissionHelper.create_permission(Permission.BOT_USER),
            "preferred_language": preferred_language,
            "profile": {
                "description": "Workaround", #FIXME # Strings().search_string(preferred_language, "command.profile:default_desc"),
                "bday": None,
                "banner": None,
                "reputations": 0,
                "joined_tendo_since": datetime.datetime.now().strftime("%d.%m.%Y/%H:%M"),
                "social": [],  # [["Youtube", "url", "profile_name"]]
                "badges": []
            },
            "sterni": 100,
            "tc": 2,
            "leveling": leveling_data,
            "options": {}
        })


class Guilds:
    """
    Wrapper of the Guilds collection
    Not every key/value pair has their method entry in this Wrapper. Mind that!
    """
    def __init__(self, collection):
        self.collection = collection

    def exists(self, guild_id: int) -> bool:
        """
        :param guild_id: a guild id
        :return: whetever that guild exists
        """
        return self.collection.find_one({"id": guild_id}) is not None

    def insert_default(self, guild_id: int, lang="de") -> None:
        """
        Inserts a pre-defined guild

        :param guild_id: the guild id
        :param lang: the language
        :return: None
        """
        self.collection.insert_one({
            "id": guild_id,
            "lang": lang,
            "options": {}
        })

    def get_options(self, guild_id: int) -> Optional[GuildOptions]:
        """
        :param guild_id: The guild id
        :return: A Wrapper for guild options or none if the guild doesnt exists
        """

        if not self.exists(guild_id):
            return None

        return GuildOptions(self.collection.find_one({"id": guild_id})["options"])

    def set_options(self, guild_id: int, options: Union[dict, GuildOptions]) -> None:
        """
        Sets new options for a guild

        :param guild_id: the guild id
        :param options: the new options to be set
        :return: None
        """

        if not self.exists(guild_id):
            return None

        self.collection.update_one({"id": guild_id}, {"$set": {"options": options}})

    def remove_guild(self, guild_id: int) -> None:
        """
        Removes a guild from the database

        :param guild_id: the guild id
        :return: None
        """
        self.collection.delete_one({"id": guild_id})

    def set_lang(self, guild_id: int, lang: str) -> None:
        """
        Sets the language of that guild

        :param guild_id: the guild id
        :param lang: the language
        :return: None
        """
        self.collection.update_one({"id": guild_id}, {"$set": {"lang": lang}})

    def get_lang(self, guild_id: int) -> str:
        """
        :param guild_id: the guild id
        :return: the language of that guild
        """
        return self.collection.find_one({"id": guild_id})["lang"]


class MongoDB:
    """
    Use this class to retrieve any collection you want.
    Also use the function get_db() in order to get an instance of this class (don't create an own one!)
    """
    def __init__(self):
        global cur_db

        self.connection_string = os.environ["DB_CONN"]
        self.mongo_client = MongoClient(self.connection_string)
        self.database = self.mongo_client.get_database("tendo")

        if cur_db is not None:
            get_logger().critical("Database instance already initialized")

        cur_db = self

    def get_collection(self, name: str) -> Any:
        """
        Only use this function if you want to get a collection which does not have it's own Wrapper

        :param name: The collection name
        :return: the collection from that name
        """
        return self.database.get_collection(name)

    def get_users(self) -> Users:
        """
        :return: The Users Wrapper Collection
        """
        return Users(self.get_collection("users"))

    def get_guilds(self) -> Guilds:
        """
        :return: The Guild Wrapper Collection
        """
        return Guilds(self.get_collection("servers"))


def get_db() -> MongoDB:
    """
    Don't create your own instance of the MongoDB class! Use this function in order to get one instance
    Used mainly for avoiding having multiple connections to mongodb class

    :return: An instance of the MongoDB class
    """
    if cur_db is None:
        get_logger().critical("Could not load database")

    return cur_db  # noqa

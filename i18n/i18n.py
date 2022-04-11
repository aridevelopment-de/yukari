import os
import random
from typing import (
    Any,
    Dict,
    List,
    Union
)

import yaml
from dotenv import load_dotenv

from yukari.i18n.registry import get_i18n_registry
from utils.logger import get_logger

load_dotenv()


class KeyNotFoundError(Exception):
    """
    Exception if a Key was not found
    """
    pass


class I18n:
    """
    Class for internationalization
    Can retrieve strings out of yaml files
    TODO: Add caching
    """

    HEADER_KEYWORDS = ("metadata", "help", "subs")

    def __init__(self, path: str, translation_path: str = None, no_register: bool = False):
        path = path.replace("\\", "/")

        if translation_path is None:
            self.translation_path = os.path.dirname(path).replace("\\", "/") + "/i18n/"
        else:
            self.translation_path = translation_path.replace("\\", "/")

        if not no_register:
            namespace = os.path.dirname(path).replace("/".join(__file__.replace("\\", "/").split("/")[:-3]), "")
            get_i18n_registry().register(namespace, self)

    def __retrieve_yaml_data(self, language: str) -> Dict[str, Any]:
        """
        Helper function to retrieve the yaml data
        Will be used in the future for retrieving cached data

        :param language: the language to retrieve
        :return: dict of translations
        """
        try:
            with open(self.translation_path + language + ".yml", "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            get_logger().error("Language file not found: " + self.translation_path + language + ".yml")

    def query_string(self, language: str, query: str, *format_data: Any) -> str:
        data = self.__retrieve_yaml_data(language)
        query = ("subs." + query).split(".") if not query.startswith(self.HEADER_KEYWORDS) else query.split(".")
        string = self.__get_sub(data, query)

        return self.format_string(string, *format_data)

    def query_strings(self, language: str, *queries: str) -> Dict[str, str]:
        """
        Queries multiple strings

        :param language: the language
        :param queries: the string queries to search for
        :return: Multiple resulting strings
        """
        strings = {}

        for query in queries:
            strings[query] = self.query_string(language, query)

        return strings

    def query_string_list(self, language: str, query: str) -> List[str]:
        """
        Queries a list of strings

        :param language: the language
        :param query: the string query to search for
        :return: A list of resulting strings
        """

        query = ("subs." + query).split(".") if not query.startswith(self.HEADER_KEYWORDS) else query.split(".")
        return self.__get_sub(self.__retrieve_yaml_data(language), query)

    def query_random_string_list(self, language: str, query: str, *format_data: Any) -> str:
        """
        Queries a random element from a string list

        :param language: the language
        :param query: the string query to search for
        :param format_data: optional format data
        :return: the resulting string
        """

        string_list = self.query_string_list(language, query)
        element = random.choice(string_list)

        return self.format_string(element, *format_data)

    @staticmethod
    def __get_sub(data: Dict[str, Any], sub_query: List[str]) -> Union[str, list]:
        """
        Helper function to retrieve nested elements in translations

        :param data: the current dictionary consisting of translations (yaml file)
        :param sub_query: the sub query to search for
        :return: the resulting string
        """

        current_value = data

        for idx, query_part in enumerate(sub_query):
            if isinstance(current_value[query_part], str) or isinstance(current_value[query_part], list):
                current_value = current_value[query_part]
                break
            elif isinstance(current_value[query_part], dict):
                current_value = current_value[query_part]
            else:
                raise ValueError(f"The type of the value at '{'.'.join(sub_query[:idx+1])}' is not supported (int or dict expected, got {type(current_value[query_part])})")

        return current_value

    @staticmethod
    def format_string(string: str, *format_data: Any) -> str:
        """
        We use this method to provide other format features in the future
        Currently it only calls `format` on the specified string with the specified arguments
        TODO: Write own format function

        :param string:
        :param format_data:
        :return:
        """

        if not format_data:
            return string

        return string.format(*format_data)  # noqa

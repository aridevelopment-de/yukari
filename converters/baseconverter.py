from typing import List, Tuple, Optional, Any, Dict

import discord


class BaseConverter:
    CONVERTER_TYPE = None

    def __init__(self, function_parameters: Dict, function_parameter_index: int, message: discord.Message):
        """
        Initializes the converter.
        :param function_parameters: The function parameters which represents the subcommand
        :param function_parameter_index: The index of the function parameter which is currently being parsed
        :param message: The original message
        """
        self.function_parameters = function_parameters
        self.function_parameter_index = function_parameter_index
        self.message = message

    def convert(self, arguments: List[str]) -> Optional[Tuple[Any, int]]:
        """
        Converts arguments to another type.
        :param arguments: The arguments to parse
        :return: The parsed data and the relative index to continue iterating if the conversion was successful otherwise None
        """
        pass

    @staticmethod
    def representation(data: str) -> str:
        """
        Returns a string representation of the converter for the help command.
        Example: The MemberConverter might return "@User#0000" here

        :param data: The data which should be converted
        :return: The string representation of the converter
        """
        pass

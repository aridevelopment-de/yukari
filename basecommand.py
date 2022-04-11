import inspect
import itertools
import typing
from typing import List

import discord

from yukari.baseheaders import EventWrapper, SubcommandWrapper, CommandHeader
from yukari.converters import (
    stringconverter,
    integerconverter,
    floatconverter,
    spacedstringconverter,
    memberconverter,
    roleconverter
)
from yukari.utils import EventList, SubCommandList
from yukari.logger import LogLevel, get_logger
from yukari.utils import DefaultValueList


class BaseCommand:
    """
    Extendable base class for all commands.
    TODO: Some subcommands are multiple used e.g.
    - n+profile
    - n+profile @User#0000

    But they basically are one and only one function
    The idea is to have a help registry to manually manipulate such entries for n+help
    """

    _REQUIRED_SUBCOMMAND_PARAMS = [(("self",), inspect._empty), (("message", "msg"), discord.Message), (("lang", "language"), str)]  # noqa
    _CONVERTERS = [
        stringconverter.StringConverter,
        integerconverter.IntegerConverter,
        floatconverter.FloatConverter,
        spacedstringconverter.SpacedStringConverter,
        memberconverter.MemberConverter,
        roleconverter.RoleConverter
    ]

    def __init__(self, invoke: str, command_header: CommandHeader):
        self._header = command_header
        self._header.invoke = invoke
        self._events = EventList()
        self._subcommands = SubCommandList()

        self._register_events()
        self._register_subcommands()

    def _register_events(self):
        for _obj in dir(self):
            _obj = getattr(self, _obj)

            if isinstance(_obj, EventWrapper):
                func = _obj.func

                if isinstance(func, SubcommandWrapper):
                    get_logger().log(
                        LogLevel.CRITICAL,
                        f"Subcommand '{func}' cannot be registered as an event. "
                    )

                    raise RuntimeError("See logger exception")

                self._events.append(_obj)

    def _register_subcommands(self):
        # Iterate through each subcommand function
        # And check typing names and parameters
        for _obj in dir(self):
            _obj = getattr(self, _obj)

            if isinstance(_obj, SubcommandWrapper):
                subcommand_function = _obj.func

                if isinstance(subcommand_function, EventWrapper):
                    get_logger().critical(
                        f"Event '{subcommand_function}' cannot be registered as a subcommand. "
                    )

                function_parameters = inspect.signature(subcommand_function).parameters

                # The first three parameters are always self, message and language
                # The following code makes sure that the parameters are correct
                for idx, parameter_name in enumerate(function_parameters):
                    parameter_type = function_parameters[parameter_name].annotation

                    if idx < len(self._REQUIRED_SUBCOMMAND_PARAMS):
                        required_names, required_type = self._REQUIRED_SUBCOMMAND_PARAMS[idx]

                        if parameter_name not in required_names or parameter_type != required_type:
                            get_logger().critical(
                                f"Wrong argument name or type declaration specified in subcommand {_obj.func} "
                                f"on parameter '{parameter_name}' (type: {parameter_type})\n"
                                f"Should be: {_obj.func.__name__}"
                                f"({', '.join(f'{_name}: {_type}' for _name, _type in self._REQUIRED_SUBCOMMAND_PARAMS)})"
                            )
                    else:
                        break

                # The invoke is not set by default so we set it here
                if not _obj.header.invoke:
                    _obj.header.invoke = self._header.invoke

                # TODO: Check if subcommand has been initialized twice or more
                self._subcommands.append(_obj)

        # Make sure there is a subcommand for the very first invoke (name="", invoke=default)
        # If not, send a warning and create it
        for _obj in dir(self):
            _obj = getattr(self, _obj)

            if isinstance(_obj, SubcommandWrapper):
                if _obj.header.invoke == self._header.invoke:
                    if _obj.header.name == "":
                        break
        else:
            get_logger().warning(f"Command {self._header.invoke} has no subcommand at position 0 with invoke '{self._header.invoke}'. An empty subcommand will be created.")
            empty_subcommand = SubcommandWrapper(lambda *_: 0, "")
            empty_subcommand.header.invoke = self._header.invoke
            setattr(self, "________empty_subcommand________", empty_subcommand)
            self._subcommands.append(empty_subcommand)

        # After missing invokes have been set, declare the next subcommand of a subcommand
        for _obj in dir(self):
            _obj = getattr(self, _obj)

            if isinstance(_obj, SubcommandWrapper):
                if not _obj.header.name == "":
                    last_subcommands = ['', *_obj.header.name.split(".")[:-1]]

                    # We search for the subcommand before the current one so we can create a one way linked list
                    # If the subcommand is further away from the main command (e.g. 'n+test poggers pogchamp', here its pogchamp)
                    # We use the last_subcommands list to search for the full name
                    # Otherwise the latest subcommand must be the main command (indicted by an empty string)
                    last_subcommand_data = self._subcommands.get(
                        fullname=".".join(last_subcommands[1:]) if len(last_subcommands) > 1 else '',
                        invoke=_obj.header.invoke
                    )

                    if last_subcommand_data is None:
                        get_logger().critical(
                            f"Subcommand {_obj.func} does not have a previous subcommand. It cannot be created!"
                        )

                    if _obj.header.string_node_key is None:
                        get_logger().warning(f"Subcommand '{_obj.header.name}' of command '{self._header.invoke}' has no translation key!")

                    # And set the next subcommand of the previous subcommand (like a one way linked list)
                    last_subcommand, _idx = last_subcommand_data
                    last_subcommand.header._next.append(_obj)  # noqa
                    self._subcommands[_idx] = last_subcommand

    async def _execute_subcommand_func(
            self,
            wrapper_before: typing.Optional[SubcommandWrapper],
            subcommand_wrapper: SubcommandWrapper,
            args: List[str],
            message: discord.Message,
            lang: str
    ) -> None:
        """
        Executes the subcommand function
        Also does type checking and type conversion of the input

        :param wrapper_before: The subcommand wrapper before the current subcommand (if any otherwise None)
        :param subcommand_wrapper: The SubcommandWrapper of the current subcommand
        :param args: Arguments to be delivered to the subcommand. Those will be parsed before the subcommand gets executed
        :param message: The discord.Message object
        :param lang: A string representing the language of the user
        :return: None
        """

        # The previous subcommand still is on cooldown
        if wrapper_before is not None and wrapper_before.check_cooldown(message.author.id):
            return

        parsed_arguments = []

        subcommand_function = subcommand_wrapper.func
        function_parameters = dict(inspect.signature(subcommand_function).parameters)

        # Remove the first three parameters (self, message, lang)
        for parameter_data in self._REQUIRED_SUBCOMMAND_PARAMS:
            for parameter_name in parameter_data[0]:
                if parameter_name in function_parameters:
                    function_parameters.pop(parameter_name)
                    break
            else:
                get_logger().error(f"Could not find required parameter(s) '{parameter_data[0]}' in signature")

        # if len(args) < len(function_parameters):
        #    raise RuntimeError("too few parameters provided")

        wait_for_index = 0

        # Convert user input parameters to their respective types
        # TODO: Give the user some feedback when supplying wrong argument types
        # TODO: Complete type checking at the registering process
        # TODO: Optional arguments
        # TODO: Arguments with multiple types
        for idx, parameter_zipped_data in enumerate(itertools.zip_longest(args, function_parameters)):
            if idx < wait_for_index:
                continue

            supplied_argument, parameter_name = parameter_zipped_data

            if parameter_name is None:
                # We have reached the end of the function parameters
                break

            parameter_type = function_parameters[parameter_name].annotation

            # If no type is specified, we just pass it
            if parameter_type == inspect._empty:  # noqa
                parsed_arguments.append(supplied_argument)
            elif not hasattr(parameter_type, '__origin__') and not hasattr(parameter_type, '__args__'):
                # FIXME: This will also accept "param: Optional" or "param: Union" as well
                for converter in self._CONVERTERS:
                    if converter.CONVERTER_TYPE == parameter_type:
                        custom_converter = converter(function_parameters.copy(), idx, message)
                        result = custom_converter.convert(args[idx:])

                        if result is None:
                            get_logger().error(f"Could not convert argument starting at index {idx} to {parameter_type}")
                            break

                        parsed_data, relative_index = result
                        wait_for_index = relative_index + idx
                        parsed_arguments.append(parsed_data)
                        break
                else:
                    parsed_arguments.append(supplied_argument)
            else:
                # Up until Python 3.7, typing supports __args__ and __origin__ in typing objects like Union, Optional, etc
                # But since Python 3.8 there are two functions provided from the typing module: get_origin and get_args
                if parameter_type.__origin__ == typing.Union:
                    if len(parameter_type.__args__) == 2 and type(None) in parameter_type.__args__:
                        # param: Optional[T]
                        # Optional only works at the end of the argument list
                        if idx != len(function_parameters) - 1:
                            get_logger().error(f"Can only place optional argument at the end of function {subcommand_function}")
                            return

                        if supplied_argument is None:
                            parsed_arguments.append(None)
                        else:
                            # Internally Optional[T] is Union[T, None]
                            # We are going to search the optional type besides None
                            expected_type = next(filter(lambda e: e != type(None), parameter_type.__args__))  # noqa: E721

                            # And then just convert it using the list of converters
                            for converter in self._CONVERTERS:
                                if converter.CONVERTER_TYPE == expected_type:
                                    custom_converter = converter(function_parameters.copy(), idx, message)
                                    result = custom_converter.convert(args[idx:])

                                    if result is None:
                                        get_logger().error(f"Could not convert argument starting at index {idx} to {parameter_type}")
                                        break

                                    parsed_data, relative_index = result
                                    wait_for_index = relative_index + idx
                                    parsed_arguments.append(parsed_data)
                                    break
                            else:
                                get_logger().error(f"Could not convert argument starting at index {idx} to {parameter_type}")

        await subcommand_wrapper.execute(self, message, lang, *parsed_arguments)

    async def _execute(self, args: List[str], message: discord.Message, invoke: str, lang: str):
        """
        if no arguments are being supplied
        invoke the default subcommand

        otherwise
        go through every subcommand
        check if the subcommand matches the current argument
        if there are no further subcommands after the current match that match the next argument
        - use the arguments left over and invoke the subcommand
        otherwise continue
        """
        if not args:
            # TODO: Invoke may need to be set to lowercase
            for subcommand_wrapper in self._subcommands:
                header = subcommand_wrapper.header

                if header.name == "" and header.position == 0 and header.invoke == invoke:
                    await self._execute_subcommand_func(None, subcommand_wrapper, args, message, lang)
                    return
        else:
            _position = 1
            previous_subcommands = DefaultValueList()
            _nested_argument = ""

            while args:
                text_argument = args.pop(0)
                _nested_argument += (' .'[bool(_nested_argument)] if _position > 1 else '') + text_argument
                subcommand_search_result = self._subcommands.get(
                    name=_nested_argument.split(".")[-1],
                    position=_position,
                    invoke=invoke
                )

                if subcommand_search_result is None:
                    # If the current argument is not a valid subcommand anymore
                    # we might've encountered a valid subcommand and the current argument is part of that subcommand (its an argument)
                    # Try if the previous argument is a valid subcommand

                    possible_last_subcommand = ['', *_nested_argument.split(".")][-2]
                    possible_subcommand_search_result = self._subcommands.get(
                        name=possible_last_subcommand,
                        position=_position - 1,
                        invoke=invoke
                    )

                    if possible_subcommand_search_result is None:
                        # If the possible search is still none, we couldn't find any possible subcommand
                        # TODO: Return error to user
                        get_logger().log(
                            LogLevel.WARNING,
                            "Error in parsing arguments for subcommand " + self._header.get_serializable()["invoke"]
                        )

                        raise RuntimeWarning("See logger warning")

                    # Otherwise run the subcommand
                    subcommand_argument, _ = possible_subcommand_search_result

                    # Include the current popped argument because we already tried searching it up as a subcommand
                    # but the search failed
                    return await self._execute_subcommand_func(
                        previous_subcommands.get(-1, None),
                        subcommand_argument,
                        [text_argument, *args],
                        message,
                        lang
                    )
                else:
                    subcommand_argument, _ = subcommand_search_result

                    if not subcommand_argument.header._next:  # noqa
                        return await self._execute_subcommand_func(
                            previous_subcommands.get(-1, None),
                            subcommand_argument,
                            args,
                            message,
                            lang
                        )
                    elif args:
                        # FIXME
                        for possible_subcommand in subcommand_argument.header._next:  # noqa
                            if possible_subcommand.header.name.split(".")[-1] == args[0]:
                                # If we found another subcommand, the whole while loop has to jump one iteration over
                                break
                        else:
                            # Otherwise, break the current while loop and execute the current subcommand
                            return await self._execute_subcommand_func(
                                previous_subcommands.get(-1, None),
                                subcommand_argument,
                                args,
                                message,
                                lang
                            )

                    previous_subcommands.append(subcommand_argument)
                    _position += 1

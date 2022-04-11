from typing import List

from yukari.baseheaders import EventWrapper, SubcommandWrapper
from yukari.enums import EventType


class EventList(list):
    """
    Custom list containing event functions
    """
    def gets(self, event_type: EventType) -> List[EventWrapper]:
        """
        :param event_type: the event type to search for
        :return: a list of event functions with that matching event type
        """
        return [(idx, event_wrapper) for idx, event_wrapper in enumerate(self) if event_wrapper.event_type == event_type]


class SubCommandList(list):
    """
    Custom list containing subcommand functions
    """
    def get(self, fullname: str = None, name: str = None, position: int = None, invoke: str = None) -> SubcommandWrapper:
        """
        This function queries using the specified parameters
        A mix of the following parameters is allowed:
        - fullname, invoke
        - name, position
        - name, position, invoke
        
        :param fullname: The full path of the subcommand (e.g. "pog.pogchamp.poggers")
        :param name: the short name of the subcommand (e.g. "poggers")
        :param position: the position of the short name
        :param invoke: the invoke of the subcommand
        :return: the subcommand wrapper for the search queries
        """
        for idx, _func in enumerate(self):
            header = getattr(_func, "header")

            if fullname is not None and invoke is not None:
                if fullname in header.get_all() and header.invoke == invoke:
                    return _func, idx
            elif name is not None and position is not None:
                if any(possible_name.split(".")[-1] == name for possible_name in header.get_all()) and header.position == position:
                    if invoke is not None:
                        if header.invoke == invoke:
                            return _func, idx
                    else:
                        return _func, idx

        return None

    def gets_from_position(self, position: int) -> List[SubcommandWrapper]:
        """
        Searches subcommands via their short name position

        :param position: the position of the short name from the subcommand
        :return: a list of subcommands matching that criteria
        """
        subcommands = []

        for idx, _func in enumerate(self):
            header = getattr(_func, "header")

            if header.position == position:
                subcommands.append((_func, idx))

        return subcommands

    def count_subcommands(self, fullname: str, position: int, invoke: str) -> int:
        """
        Counts subcommands with the following parameters
        FIXME: position isnt needed because fullname is already supplied
        
        :param fullname: the fullname of the subcommand
        :param position: the short name position of the subcommand
        :param invoke: the invoke of the subcommand
        :return: the amount of existing subcommands
        """
        count = 0

        for _func in self:
            header = getattr(_func, "header")

            if fullname in header.get_all() and header.position == position and header.invoke == invoke:
                count += 1

        return count

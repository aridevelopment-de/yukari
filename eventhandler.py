from typing import Any

from yukari.commandhandler import get_command_handler
from yukari.enums import EventType


class EventHandler:
    @staticmethod
    async def dispatch_event(event_type: EventType, *data: Any):
        """
        Dispatches a discord event to the commands which registered for it.
        :param event_type: The type of the event to dispatch
        :param data: The data passed to the event function
        :return:
        """
        command_handler = get_command_handler()

        for command_invoke in command_handler.commands:
            command_group_class = command_handler.commands[command_invoke]["cog_cls"]

            for _, event_wrapper in command_group_class._events.gets(event_type):
                await event_wrapper.execute(command_group_class, *data)

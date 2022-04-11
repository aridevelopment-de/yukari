from __future__ import annotations

import asyncio
from typing import Any

import discord
import emoji

from yukari.commandhandler import get_command_handler
from yukari.dataholders import ReactionEmoji, ReactionAddEvent
from yukari.enums import EventType
from yukari.logger import get_logger

event_handler_instance = None

def get_event_handler() -> 'EventHandler':
    return event_handler_instance  # noqa


class EventHandler:
    def __init__(self):
        global event_handler_instance

        self.event_injections = {}

        event_handler_instance = self

    async def dispatch_event(self, event_type: EventType, *data: Any):
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

        [await event_function(*data) for event_function in self.event_injections.get(event_type, [])]

    def on_event(self, event_type: EventType):
        """
        Decorator for injecting a function into the event handling process.

        :param event_type: The type of the event to inject
        :return: The decorated function
        """
        def inner(func):
            self._inject_event(event_type, func)
            return func

        return inner

    def _inject_event(self, event_type: EventType, event_function_coroutine):
        """
        Injects a custom function into the event handling process.

        :param event_type: The type of the event to inject
        :param event_function_coroutine: The coro to execute when the event is dispatched
        :return: None
        """
        if not asyncio.iscoroutinefunction(event_function_coroutine):
            get_logger().critical(f"{event_function_coroutine} is not a coroutine function")

        event_list = self.event_injections.get(event_type, [])
        event_list.append(event_function_coroutine)
        self.event_injections[event_type] = event_list

    def register_events(self, client: discord.Client):
        """
        Registers all the necessary events

        :param client: the discord client
        :return: None
        """

        @client.event
        async def on_reaction_add(reaction, user):
            if emoji.is_emoji(str(reaction.emoji)):
                reaction_emoji = ReactionEmoji(
                    emoji.demojize(str(reaction.emoji)),
                    None,
                    False
                )
            else:
                reaction_emoji = ReactionEmoji(
                    reaction.emoji.name,
                    reaction.emoji.id,
                    reaction.emoji.animated
                )

            guild_id = None

            if hasattr(reaction, "guild"):
                if reaction.guild.id is not None:
                    guild_id = reaction.guild.id

            reaction_add_event = ReactionAddEvent(
                user.id,
                reaction.message.id,
                reaction.message.channel.id,
                guild_id,
                reaction_emoji,
                client
            )

            await self.dispatch_event(EventType.REACTION_ADD, reaction_add_event)

        @client.event
        async def on_raw_reaction_add(payload):
            reaction_emoji = ReactionEmoji(
                payload.emoji.name,
                payload.emoji.id,
                payload.emoji.animated
            )

            reaction_add_event = ReactionAddEvent(
                payload.user_id,
                payload.message_id,
                payload.channel_id,
                payload.guild_id,
                reaction_emoji,
                client
            )

            await self.dispatch_event(EventType.REACTION_ADD, reaction_add_event)

from enum import auto, Enum


class EventType(Enum):
    """
    Enum for event types.
    """
    MESSAGE_SEND = auto()
    MESSAGE_EDIT = auto()

    REACTION_ADD = auto()
    REACTION_REMOVE = auto()

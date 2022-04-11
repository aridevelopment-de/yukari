from __future__ import annotations

from typing import TYPE_CHECKING

from utils.logger import get_logger

if TYPE_CHECKING:
    from yukari.i18n.i18n import I18n


i18n_registry_instance = None

def get_i18n_registry() -> 'I18nRegistry':
    """
    There should be only one registry at a time.
    Instantiating another will result in an error
    
    :return: the i18n registry instance
    """
    if i18n_registry_instance is None:
        raise RuntimeError("I18nRegistry not initialized")

    return i18n_registry_instance  # noqa


class I18nRegistry:
    """
    Registry for i18n instances.
    """
    def __init__(self):
        global i18n_registry_instance

        if i18n_registry_instance is not None:
            get_logger().critical("I18nRegistry already initialized")

        i18n_registry_instance = self
        self.instances = {}

    def register(self, namespace: str, i18n: I18n):
        """
        Register an i18n instance.
        :param namespace: the namespace of the i18n instance (e.g. "commands.other.help")
        :param i18n: the i18n instance
        :return: None
        """
        namespace = namespace.strip("/").replace("/", ".")

        if namespace in self.instances:
            get_logger().critical("Namespace '{}' already registered".format(namespace))

        self.instances[namespace] = i18n

    def get(self, namespace: str) -> I18n:
        """
        Retrieves an i18n instance.
        :param namespace: the namespace of the i18n instance (e.g. "commands.other.help")
        :return: the i18n instance
        """
        if namespace not in self.instances:
            get_logger().critical("No translation for namespace '{}'".format(namespace))

        return self.instances[namespace]

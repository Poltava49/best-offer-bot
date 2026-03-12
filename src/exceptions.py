"""Custom exceptions for the application."""


class MessageHandlerBotError(Exception):
    """Exception raised for errors in the message handlers."""


class DatabaseConnectionError(Exception):
    """Exception raised for errors in the database connect."""

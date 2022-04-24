"""Module containing custom exceptions for easy-email-downloader."""


class NonExistentMailboxError(Exception):
    """Raised if the mailbox does not exist."""


class NoMessagesFoundError(Exception):
    """Raised if no messages are found in the mailbox."""


class MalformedEmailError(Exception):
    """Raised if email is malformed."""

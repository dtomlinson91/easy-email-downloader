"""Module containing utils functions for easy-email-downloader."""
from __future__ import annotations

import contextlib
import email
import imaplib
import re
from email.header import decode_header
from email.message import Message
from typing import Any, List, Tuple

from easy_email_downloader.common import get_imap_instance
from easy_email_downloader.exceptions import NoMessagesFoundError, NonExistentMailboxError
from easy_email_downloader.models import Attachment, Email, EmailConfig, EmailFilter


def download_emails(
    email_config: EmailConfig,
    email_filter: EmailFilter = EmailFilter(),
) -> List[Email]:
    """
    Download emails from an IMAP server.

    Args:
        email_config (EmailConfig): An instance of `EmailConfig` containing user credentials for an IMAP server.
        email_filter (EmailFilter, optional): An instance of `EmailFilter` with any user filters. Defaults to EmailFilter().

    Raises:
        NoMessagesFoundError: Raised if no messages are found in the selected mailbox.

    Returns:
        List[Email]: A list of `Email` objects containing the downloaded emails.
    """
    # get imap instance
    imap = get_imap_instance(
        host=email_config.host,
        email_address=email_config.email_address,
        password=email_config.password,
    )

    # get messages for mailbox
    _, _messages = imap.select(email_config.mailbox)

    # check mailbox exists
    check_mailbox(_messages)

    # create search filter
    _search_filter = f"({create_search_filter(email_filter)})"

    # search for messages matching filter
    _, messages = imap.search(None, _search_filter)

    # split messages into a list
    messages = messages[-1].split(b" ")

    # emails by default are oldest first - reverse to get most recent first
    if not email_filter.oldest_first:
        messages.reverse()

    # if no messages for inbox raise error
    if len(messages) == 1 and messages[0] == b"":
        raise NoMessagesFoundError(f"No messages found in mailbox {email_config.mailbox}")

    # verify total messages in mailbox is <= total messages to download
    messages_to_download_verified = (
        min(len(messages), email_filter.messages_to_download)
        if email_filter.messages_to_download > 0
        else len(messages)
    )

    # fetch the message
    return fetch_messages(email_filter, imap, messages, messages_to_download_verified)


def fetch_messages(
    email_filter: EmailFilter,
    imap: imaplib.IMAP4_SSL,
    messages: Any,
    messages_to_download_verified: int,
) -> List[Email]:
    """
    Fetch messages from an IMAP server.

    Args:
        email_filter (EmailFilter): The user email filter.
        imap (imaplib.IMAP4_SSL): A connected `imaplib.IMAP4_SSL` instance.
        messages (Any): A list of bytes from an `imaplib.IMAP4_SSL.search` containing integers of messages
            in the mailbox.
        messages_to_download_verified (int): The number of messages to download.

    Returns:
        List[Email]: A list of `Email` objects containing the downloaded emails.
    """
    downloaded_emails: List[Email] = []
    for _message in messages[:messages_to_download_verified]:
        # fetch the message
        _, message = imap.fetch(str(_message.decode("utf-8")), ("RFC822"))

        # create an Email() object from the downloaded message
        for response in message:
            if isinstance(response, tuple):
                email_object = Email()
                msg = email.message_from_bytes(response[-1])  # noqa pylint(unsubscriptable-object)
                (
                    email_object.subject,
                    email_object.sender,
                    email_object.date,
                ) = get_subject_and_sender(msg)

                if msg.is_multipart():
                    email_object = get_multipart_email(msg=msg, email_object=email_object)
                else:
                    email_object = get_non_multipart_email(msg=msg, email_object=email_object)

                downloaded_emails.append(email_object)

        # delete the message on the IMAP server if the flag is set
        if email_filter.delete_after_download:
            imap.store(str(_message.decode("utf-8")), "+FLAGS", "\\Deleted")
            imap.expunge()

    return downloaded_emails


def create_search_filter(email_filter: EmailFilter) -> str:
    """
    Create a search filter using the `subject` and `sender`.

    If neither the `subject` nor `sender` are defined will return a filter for all messages.

    Args:
        email_filter (EmailFilter): The `EmailFilter` instance.

    Returns:
        str: An IMAP filter as a string.
    """
    _search_filter = ""
    if email_filter.subject:
        _search_filter += f'HEADER Subject "{email_filter.subject}" '
    if email_filter.sender:
        _search_filter += f'(HEADER FROM "{email_filter.sender}") '
    if not email_filter.subject and not email_filter.sender:
        _search_filter += "ALL"
    return _search_filter


def get_non_multipart_email(msg: Message, email_object: Email) -> Email:
    """
    Get the `content_type` and `body` of a `Message` and attach to the `email_instance`.

    Args:
        msg (Message): The `Message` object for an email.
        email_object (Email): The `Email` instance.

    Returns:
        Email: The `email_object` with the `content_type` and `body`.
    """
    content_type = msg.get_content_type()
    if content_type in ["text/plain", "text/html"]:
        email_object.content_type = content_type
        email_object.body = msg.get_payload(decode=True).decode()
    return email_object


def get_multipart_email(msg: Message, email_object: Email) -> Email:
    """
    Get each part of a multipart `Message` and attach to the `email_object`.

    This function will walk over each of a `Message` and get the `content_type`, `body` and `attachments` and set
    the attribute on the `email_object`.

    Args:
        msg (Message): The `Message` object for an email.
        email_object (Email): The `Email` instance.

    Returns:
        Email: The `email_object` with the `content_type`, `body` and `attachments`.
    """
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        email_part = None
        with contextlib.suppress(AttributeError, UnicodeDecodeError):
            email_part = part.get_payload(decode=True).decode()
        if (
            content_type in ["text/plain", "text/html"]
            and "attachment" not in content_disposition
            and email_part is not None
        ):
            email_object.content_type = content_type
            email_object.body = email_part
        elif "attachment" in content_disposition:
            email_object = get_attachment(part=part, email_object=email_object)
    return email_object


def get_attachment(part: Message, email_object: Email) -> Email:
    """
    Get the attachment as bytes from an email part and append to `email_object.attachments`.

    Args:
        part (Message): The part of a multipart email.
        email_object (Email): The `Email` instance.

    Returns:
        Email: The `email_object` with the attachment appended to `email_object.attachments` as bytes.
    """
    email_object.attachments.append(Attachment(filename=part.get_filename(), contents=part.get_payload(decode=True)))
    return email_object


def get_subject_and_sender(msg: Message) -> Tuple[str, str, str]:
    """
    Get the subject, sender and date of a message.

    Args:
        msg (Message): The message object.

    Returns:
        Tuple[str, str, str]: Return the subject, sender, date as strings.
    """
    # get subject
    subject = sender = date = None
    _subject, _subject_encoding = decode_header(msg["Subject"])[0]
    if isinstance(_subject_encoding, bytes):
        subject = _subject.decode(_subject_encoding)
    else:
        subject = str(_subject)

    # get sender
    _sender, _sender_encoding = decode_header(msg.get("From"))[0]
    if isinstance(_sender_encoding, bytes):
        sender = _sender.decode(_sender_encoding)
    else:
        sender = str(_sender)

    # get date
    _date, _date_encoding = decode_header(msg.get("Date"))[0]
    if isinstance(_date_encoding, bytes):
        date = _date.decode(_date_encoding)
    else:
        date = str(_date)

    return (subject, sender, date)


def check_mailbox(messages: List[bytes | None]):
    """
    Check if user provided mailbox exists.

    Args:
        messages (List[bytes | None]): The result from `imap.select`. Contains a byte encoded integer containing
            the number of messages in the selected mailbox.

    Raises:
        NonExistentMailboxError: Raised if the selected mailbox does not exist.
    """
    if messages[0] is not None:
        _mailbox = messages[0].decode(encoding="utf-8")
        non_existent_mailbox = re.search(r"(?P<message>Mailbox\sdoesn\'t\sexist)", _mailbox)
        if isinstance(non_existent_mailbox, re.Match):
            raise NonExistentMailboxError(non_existent_mailbox["message"])

"""Module containing base models for easy-email-downloader."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from easy_email_downloader.common import get_imap_instance


@dataclass
class Email:
    """
    An easy-email-downloader Email.

    This dataclass represents a downloaded email from an IMAP server.

    Attachments are stored as a list of `bytes` and can be saved to disk using `open(filename, "wb")` as needed.

    Attributes:
        sender (str): The sender in the form `first_name last_name <email_address>`.
        subject (str): The email subject.
        date (str): The date the email was sent.
        body (str): The content of the email. This is either in plaintext or as HTML.
        attachments (List[Optional[Attachment]]): A list of attachments as
            [Attachment][easy_email_downloader.models.Attachment] objects. If no attachments this is an empty list.
        content_type (str): The content type. Either `text/plain` or `text/html`.
    """

    sender: str = field(default_factory=lambda: "")
    subject: str = field(default_factory=lambda: "")
    date: str = field(default_factory=lambda: "")
    body: str = field(default_factory=lambda: "")
    attachments: List[Optional[Attachment]] = field(default_factory=lambda: [])
    content_type: str = field(default_factory=lambda: "")


@dataclass
class EmailConfig:
    """
    A dataclass representing user config to connect to an IMAP server.

    If the mailbox is unknown `EmailConfig.list_mailboxes` will return a list of mailboxes on the IMAP server.

    Attributes:
        host (str): The host of the IMAP server.
        email_address (str): The email address to login as.
        password (str): The password.
        mailbox (str): The mailbox to download emails from.
        port (int): The IMAP port of the server.
    """

    host: str
    email_address: str
    password: str
    mailbox: str = field(default_factory=lambda: "")
    port: int = 993

    def list_mailboxes(self) -> List[str]:
        """
        List all mailboxes.

        Args:
            host (str): The IMAP server host.
            email_address (str): The email address.
            password (str): The email password.

        Returns:
            List[str]: A list of mailboxes from the IMAP server.
        """
        imap = get_imap_instance(self.host, self.email_address, self.password)
        mailboxes = imap.list()
        return [mailbox.decode(encoding="utf-8") for mailbox in mailboxes[-1] if isinstance(mailbox, bytes)]


@dataclass
class EmailFilter:
    """
    A dataclass used to store user options to filter emails on the IMAP server before downloading.

    `subject` and `sender` are optional and any combination of the two can be used. If both are left out then all
    emails are downloaded.

    Filtering emails by `subject` is implemented differently on each IMAP server. Exact strings often won't match.

    Care should be taken with `delete_after_download` - if set to True the email will be removed from the IMAP server.

    Attributes:
        subject (str | None, optional): The subject to filter by. Defaults to None.
        sender (str | None, optional): The sender email address to filter by. Defaults to None.
        messages_to_download (int, optional): The number of emails to download. If -1 will download all. Defaults to -1.
        oldest_first (bool, optional): Whether to download emails starting with the oldest first. Defaults to False.
        delete_after_download (bool, optional): Whether to delete the emails after successfully downloading. Defaults to False.
    """

    subject: str | None = None
    sender: str | None = None
    messages_to_download: int = -1
    oldest_first: bool = False
    delete_after_download: bool = False


@dataclass
class Attachment:
    """
    A dataclass used to represent an attatchment in an email.

    Attributes:
        filename (str | None, optional): The filename of the attachment. Defaults to None.
        contents (bytes | None, optional): The contents of the attachment in bytes. Defaults to None.
    """

    filename: str | None = None
    contents: bytes | None = None

"""Module containing common functions for easy-email-downloader."""
import imaplib


def get_imap_instance(host: str, email_address: str, password: str, port: int = 993) -> imaplib.IMAP4_SSL:
    """
    Get a connected imap instance using user credentials.

    Args:
        host (str): The host URL of the imap server. E.g `mail.example.com`
        email_address (str): The email address to login as.
        password (str): The password.
        port (int, optional): The imap port to use. Defaults to 993.

    Returns:
        imaplib.IMAP4_SSL: The connected imap instance.
    """
    imap = imaplib.IMAP4_SSL(host=host, port=port)
    imap.login(user=email_address, password=password)
    return imap

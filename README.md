# easy-email-downloader 📨

![PyPI](https://img.shields.io/pypi/v/easy-email-downloader)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/easy-email-downloader)
![PyPI - Downloads](https://img.shields.io/pypi/dm/simple-email-sender)

`easy-email-downloader` is a no nonsense and easy way to download emails from an IMAP server in Python with no
3rd party dependencies.

## Uses

- Extract data/logs etc. from email content for further parsing or saving to disk.
- Calculate general statistics from your inbox (who's sending me the most etc.)
- Get a list of all senders so you can identify who to unsubsribe from.
- Automatically download attachments (receipts/statements etc.) and save to disk.
- Archive content of emails for personal use.

See the installation & examples below.

Pull requests/ideas/suggestions are welcome 👍🏻

## Installation

### PyPI

```bash
pip install easy-email-downloader
```

### From Source

#### Using [Poetry](https://python-poetry.org)

👍🏻 recommended

Clone the repository and run:

```bash
poetry install
```

#### setuptools

Clone the repository and run in a virtual environment:

```bash
python setup.py install
```

## Usage

To download emails from an IMAP server:

```python
from easy_email_downloader import EmailFilter, EmailConfig, download_emails

email_config = EmailConfig(
    host="mail.example.com",
    email_address="example@example.com",
    password="somepassword",
    mailbox="INBOX",
    port=993,
)

# The EmailFilter itself and all of its fields are optional. Sensible defaults are chosen if left out.
email_filter = EmailFilter(
    subject="daily report",  # subject filtering is server specific - full string matches often won't work
    sender="someone@gmail.com",
    messages_to_download=1,  # setting this to -1 will download all emails
    oldest_first=False,  # whether to retrive the oldest emails first
    delete_after_download=False,  # be careful setting this to True - emails are permanently removed!
)

downloaded_emails = download_emails(
    email_config=email_config,
    email_filter=email_filter,
)

for downloaded_email in downloaded_emails:
    print(f"sender: {downloaded_email.sender}")
    print(f"date: {downloaded_email.date}")
    print(f"subject: {downloaded_email.subject}")
    print(f"content_type: {downloaded_email.content_type}")
    print(f"body: {downloaded_email.body[:50]}")
    for attachment in downloaded_email.attachments:
        print(f"filename: {attachment.filename}")
```

Which produces:

```
sender: Daniel Tomlinson <dtomlinson@panaetius.co.uk>
date: Sat, 23 Apr 2022 20:55:31 +0100
subject: Download me using easy-email-sender
content_type: text/html
body: Successfully downloaded using easy-email-sender!
filename: hello.jpg
```

See below for more information on `EmailFilter`, `EmailConfig`, `download_emails` or see the docstrings.
### EmailConfig

Create your `EmailConfig` instance:

If you know the mailbox you want to download from:

```python
email_config = EmailConfig(
    host="mail.example.com", email_address="example@example.com", password="somepassword", mailbox="INBOX", port=993
)
```

If you don't know the mailbox to download from, use `EmailConfig.list_mailboxes`

```
email_config = EmailConfig(
    host="mail.example.com", email_address="example@example.com", password="somepassword", port=993
)
user_mailboxes = email_config.list_mailboxes()
```

This will return a list of strings of all the mailboxes in the user's account.

`EmailConfig` supports the following arguments:

```
Attributes:
    host (str): The host of the IMAP server.
    email_address (str): The email address to login as.
    password (str): The password.
    mailbox (str): The mailbox to download emails from.
    port (int): The IMAP port of the server.
```

### EmailFilter

Create an `EmailFilter` instance:

```python
email_filter = EmailFilter(
    subject="daily report",
    sender="someone@gmail.com",
    messages_to_download=1,
    oldest_first=False,
    delete_after_download=False,
)
```

`subject` and `sender` are optional. Either both, one or none of `subject` and `sender` can be set. If neither are
provided all emails in the mailbox will be searched for.

`EmailFilter` supports the following arguments:

```
Attributes:
    subject (str | None, optional): The subject to filter by. Defaults to None.
    sender (str | None, optional): The sender email address to filter by. Defaults to None.
    messages_to_download (int, optional): The number of emails to download. If -1 will download all. Defaults to -1.
    oldest_first (bool, optional): Whether to download emails starting with the oldest first. Defaults to False.
    delete_after_download (bool, optional): Whether to delete the emails after successfully downloading. Defaults to False.
```

🚨 Be careful with `delete_after_download` - be sure you want to delete the email before you run it. This calls
`imaplib.IMAP4_SSL.expunge` which **permanently** deletes the email from the server.

### download_emails

Download emails using the `EmailConfig` and `EmailFilter`:

```python
downloaded_emails = download_emails(
    email_config=email_config,
    email_filter=email_filter,
)
```

This returns a list of `Email` objects.

The available attributes on an `Email` object are:

```
Attributes:
    sender (str): The sender in the form `first_name last_name <email_address>`.
    subject (str): The email subject.
    date (str): The date the email was sent.
    body (str): The content of the email. This is either in plaintext or as HTML.
    attachments (List[Optional[Attachment]]): A list of attachments as
        [Attachment][easy_email_downloader.models.Attachment] objects. If no attachments this is an empty list.
    content_type (str): The content type. Either `text/plain` or `text/html`.
```

Attachments are stored as `Attachment` objects containing the `filename` and `contents` (in bytes).

These can be saved to disk:

```
for attachment in downloaded_emails.attachments:
    with open(f"/some/path/{attachment.filename}", mode="wb") as attachment_contents:
        attachment_contents.write(attachment.contents)
```

## TODO

- ~~Extend attatchment logic to get filename of attatchment on server.~~ ✅
  - ~~Useful to save attatchments to disk automatically without the user having to implement `file.open(mode="wb")`.~~ ✅
- CLI to download emails to json/csv etc.
  - Should include a Dockerfile and an image published to Dockerhub.
- Tests 🥱.

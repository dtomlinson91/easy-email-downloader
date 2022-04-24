from easy_email_downloader import EmailFilter, EmailConfig, download_emails


email_config = EmailConfig(
    host="mail.panaetius.io", email_address="notifications@panaetius.io", password="***REMOVED***", port=993
)
email_filter = EmailFilter(
    # subject="Recently Added Movies",
    # sender="dmot7291@gmail.com",
    messages_to_download=-1,
    oldest_first=False,
    delete_after_download=False,
)

user_mailboxes = email_config.list_mailboxes()
# print(json.dumps(user_mailboxes, indent=2))

email_config.mailbox = "INBOX"
downloaded_emails = download_emails(
    email_config=email_config,
    email_filter=email_filter,
)

for downloaded_email in downloaded_emails:
    print(f"sender: {downloaded_email.sender}")
    print(f"date: {downloaded_email.date}")
    print(f"subject: {downloaded_email.subject}")
    print(f"content_type: {downloaded_email.content_type}")
    print(f"body: {downloaded_email.body[:50]}...")
    print(f"attachments: {downloaded_email.attachments[:50]}...")

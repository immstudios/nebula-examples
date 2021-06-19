# Sending e-mails

Nebula allows sending e-mails using its internal `send_mail` function. Internally, it is used for password reset, but you may use it in your tools and worker services for reporting, notifications etc.

SMTP server must be properly configured to send messages:

```python
data["settings"]["smtp_host"] = "smtp.example.com"
data["settings"]["smtp_port"] = 465
data["settings"]["smtp_ssl"] = True
data["settings"]["smtp_user"] = "smtp-user"
data["settings"]["smtp_pass"] = "your-smtp-password"
data["settings"]["mail_from"] = "Nebula <noreply@example.com>"
```

Then, you may for example configure an action to send a notification to the user, who started the job after it is finished by adding a script to the `<success>` block of the action config file.

```xml
<success><![CDATA[

email = None
if job.id_user:
    user = User(job.id_user)
    if user["email"]:
        email = user["email"]

if email:
    logging.info(f"Sending notification to {email}")
    body = markdown2email(f"""
Asset **{job.asset["title"]}**
has been succesfully transcoded.

*Sincerely*

*Your nebula*""")
    send_mail(email, "Your file is ready", body)

]]></success>
```

First argument of the `send_mail` function is an email address or list of addresses, subject follows. The last argument is the body.

You may provide either raw text or use `markdown2email` function to create rich formated message using Markdown syntax.


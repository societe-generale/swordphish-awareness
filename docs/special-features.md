# Special Features

## Autolock account

For security reason, a mechanism locking automatically unused account
has been developed.

When an account is created and the user never logged in, the account is
automatically disabled after a certain amount of time and a mail is sent
to the user.

When an account is not used during a customizable amount of time, it's
automatically blocked and a mail is also sent to the user.

It can be customized using the following parameters in the settings.py
file:

```python
# After AUTOLOCK_DELAY days of inactivity account will be blocked
AUTOLOCK_DELAY = 180

# Mail sent when an account is auto locked
AUTOLOCK_TEMPLATE = u"""Hello %s

You have an active account on Swordphish but you never logged in.

As a security measure, your account has been locked. If you need it reply this mail!

Best regards,

Swordphish administrators
"""

# AUTOLOCK_NEVER_USED_DELAY days after creation an account will be locked if not used
AUTOLOCK_NEVER_USED_DELAY = 30

# Mail sent when an account is never used
AUTOLOCK_NEVER_USED_TEMPLATE = u"""Hello %s

You have an active account on Swordphish but didn't use during the last %s days.

As a security measure, your account has been locked. If you need it reply this mail!

Best regards,

Swordphish administrators
"""
```

## Autoclean

To prevent the accumulation of campaigns results and targets lists in
time, we've developed an autoclean feature which automatically deletes
the lists and the campaigns results after a customizable amount of time.

It can be customized using the following parameters in the settings.py
file:

```python
# After AUTOCLEAN_DELAY days the campaigns / targets will be automatically deleted
AUTOCLEAN_DELAY = 90

# The day of the week when the auto delete is performed
AUTOCLEAN_DAY = "saturday"
```

## Special mail header

A special header is automatically added in the phishing mails sent by
swordphish.

The name of this header can be customized in settings.py file, by
default the value is:

```python
PHISHING_MAIL_HEADER = "X-Swordphish-Awareness-Campaign"
```

The header contains the target-id between brackets, ex:

```
    X-Sworphish-Awareness-Campaign: [0916e333-ad79-4102-a220-13dbd7ad4195]
```

You can use this to extract automatically the ID and count the mail as
reported using a plugin in your mail client using the report API (see
below).

## Report API

The report API allows to mark the mail as "reported" programmatically.
It's used at Société Générale in our Outlook plugin. When the mail is
detected as swordphish campaign by the plugin using the customized
header, the plugin then sends an HTTP GET request to this URL to count
the mail as reported.

The URL is structured like this:

```
    https?://swordphish_hostname/result/report/<target-id>
```

Example:

```
    https?://swordphish_hostname/result/report/0916e333-ad79-4102-a220-13dbd7ad4195
```

## Phishing domain feed

A json feed listing all the phishing domains is available on the
following URL:

```
    https?://swordphish_hosntame/2985836c7501af76a0bdd92f1d120cd2/domains_feed
```

This feature can be useful to integrate this feed in your security
monitoring tools automatically (SIEM) so your security teams (SOC /
CERT) will know if this suspicious domain is linked to a phishing
awareness campaign.

# What is Swordphish?

Swordphish is a platform allowing to create and manage fake phishing campaigns.

The goal of Swordphish is to raise your users' awareness regarding phishing in a secure way.

We believe that it's totally utopian to reach the goal of zero click on a phishing campaign, but we are confident we can
reduce the number of victims and overall increase the number of reports sent to security teams by training people using
this kind of tool.

Identifying security contacts may be hard in a big structure, that's why we developed Swordphish and a button embedded
in the mail client to help our users to report suspicious mail to security teams just with a simple click. No more
hunting on the intranet looking for that security contact, just click and it's done!

This choice seriously improved our visibility on what our users are receiving, and we decided to release it to the
community!

Swordphish can be used to train people identifying suspicious mails, and it can help checking that people report
correctly the mails to security teams.

![screenshot](https://github.com/societe-generale/swordphish-awareness/blob/master/docs/images/00-global-swordphish.png?raw=true)

## Installation

Detailed installation instructions can be found in the
[documentation](https://societe-generale.github.io/swordphish-awareness/setup/installation/).

## Docker images

Swordphish has a `docker-compose` script to get up and running test and dev environment very fast. Full
instructions [here](https://github.com/societe-generale/swordphish-awareness/tree/master/docker)

## Technical Specs

Swordphish is a Python application that relies on the following technologies:

* Django for the web framework
* Celery for background tasks
* PostgreSQL for the database
* Bootstrap for the web framework

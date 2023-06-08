# hang_backend

Contains the Hang social media web app server-side code.
It is currently being hosted on Fly.io at <https://hang-backend.fly.dev/>.

## Features

See
our [Software Design Document](https://docs.google.com/document/d/1KqFwbiebzT0QTHF0ToAmrpIA2fmafQMht8qQp-a-gWc/edit?usp=sharing).

## Installation

Ensure that Python 3 is installed.

To set up the backend server, assuming the repository has already been downloaded locally, navigate to the current 
folder (`backend/hang_backend`) and execute the following commands within a 
Python [virtual environment](https://docs.python.org/3/library/venv.html).

```bash
touch hang_backend/.env
echo "DJANGO_ENV=development" >> hang_backend/.env
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
```

To start the server, run the following commands:

```bash
python3 manage.py runserver
```

## Known Bugs

- Many API methods lack error handling when input is malformed.
- Sending an email verification token doesn't work on certain Wi-Fi networks, such as that of my school.
- Methods that use the Google Authentication API or the Google Calendar API have a tendency to take a lot of
  time/resources.

## Support

Please contact the developer at [pchen1@ocdsb.ca](), for any support or questions.

## Sources

### Documentation

| Source                                                                                                                                                         | Description                                         |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| [1]T. Christie, “Home - Django REST framework,” Django-rest-framework.org, 2011. https://www.django-rest-framework.org/ (accessed Jun. 07, 2023).              | Learn how to use Django Rest Framework              |
| [2]“Using OAuth 2.0 to Access Google APIs,” Google Developers, Nov. 12, 2018. https://developers.google.com/identity/protocols/OAuth2 (accessed Jun. 7, 2023). | Learn how to use the Google API for authentication. |
| [3]“Google Calendar API Overview,” Google Developers. https://developers.google.com/calendar/api/guides/overview (accessed Jun. 7).                            | Learn how to use the Google Calendar API.           |
| [4]“Django Channels — Channels 4.0.0 documentation,” channels.readthedocs.io. https://channels.readthedocs.io/en/stable/                                       | Learn how to use Django Channels for WebSockets.    |                                                                                |

### Code Snippets

| Source                                                                                                                                              | Description                                              |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| [5] ChatGPT, https://chat.openai.com/chat (accessed Jun. 7, 2023).                                                                                  | Used to solve various miscellaneous problems + debugging |

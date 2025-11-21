from slack_bolt.async_app import AsyncApp

from glados_slack.events.message import message_handler
from glados_slack.events.home_event import app_home_opened


EVENTS = [
    {
        "name": "message",
        "handler": message_handler,
    },
    {
        "name": "app_home_opened",
        "handler": app_home_opened,
    }
]


def register_events(app: AsyncApp):
    for event in EVENTS:
        app.event(event["name"])(event["handler"])

from slack_bolt.async_app import AsyncApp

from glados_slack.actions.hello_world import hello_world_handler
from glados_slack.actions.settings import ignore_thread_messages_handler, tone_change_handler

ACTIONS = [
    {
        "id": "hello_world",
        "handler": hello_world_handler,
    },
    {
        "id": "ignore_thread_messages_setting",
        "handler": ignore_thread_messages_handler,
    },
    {
        "id": "change_tone",
        "handler": tone_change_handler,
    }
]


def register_actions(app: AsyncApp):
    for action in ACTIONS:
        app.action(action["id"])(action["handler"])

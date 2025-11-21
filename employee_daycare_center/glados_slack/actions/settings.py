from glados_slack.tables import UserSettings
from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient


async def ignore_thread_messages_handler(ack: AsyncAck, respond: AsyncRespond, client: AsyncWebClient, body: dict):
    from glados_slack.env import logging
    userSettings = await UserSettings.select().where(UserSettings.slack_id == body["user"]["id"])
    userSettings = userSettings[0]
    if userSettings["ignore"]:
        UserSettings.update({"ignore": False}).where(UserSettings.slack_id == body["user"]["id"])
    else:
        UserSettings.update({"ignore": True}).where(UserSettings.slack_id == body["user"]["id"])

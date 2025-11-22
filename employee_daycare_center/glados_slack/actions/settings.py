from glados_slack.tables import UserSettings
from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient


async def ignore_thread_messages_handler(ack: AsyncAck, respond: AsyncRespond, client: AsyncWebClient, body: dict):
    await ack()
    userSettings = await UserSettings.select().where(UserSettings.slack_id == body["user"]["id"])
    userSettings = userSettings[0]
    if userSettings["ignore"]:
        await UserSettings.update({"ignore": False}).where(UserSettings.slack_id == body["user"]["id"]).run()
    else:
        await UserSettings.update({"ignore": True}).where(UserSettings.slack_id == body["user"]["id"]).run()

async def tone_change_handler(ack: AsyncAck, respond: AsyncRespond, client: AsyncWebClient, body: dict):
    await ack()
    userSettings = await UserSettings.select().where(UserSettings.slack_id == body["user"]["id"])
    userSettings = userSettings[0]
    newvalue = "Neutral"
    match body["actions"][0]["selected_option"]["value"]:
        case "light": newvalue = "Light"
        case "deep": newvalue = "Deep"
        case "standard": newvalue = "Standard"
        case "standard_02": newvalue = "Standard_02"
        case "neutral": newvalue = "Neutral"

    await UserSettings.update({"tone": newvalue}).where(UserSettings.slack_id == body["user"]["id"]).run()

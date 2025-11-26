from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.config import config
from glados_slack.tables import UserSettings

async def ignore_handler(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
):
    await ack()
    userSettings = await UserSettings.select().where(UserSettings.slack_id == performer)
    userSettings = userSettings[0]
    if userSettings["ignore"]:
        await UserSettings.update({"ignore": False}).where(UserSettings.slack_id == performer).run()
        await respond("Successfully toggled from True to False")
    else:
        await UserSettings.update({"ignore": True}).where(UserSettings.slack_id == performer).run()
        await respond("Successfully toggled from False to True")

async def style_handler(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
    style: str
):
    await ack()
    userSettings = await UserSettings.select().where(UserSettings.slack_id == performer)
    userSettings = userSettings[0]
    values = ["Light", "Deep", "Standard", "Standard_02", "Neutral"]
    errormsg = "Wrong tone ! Please provide on of those:"
    for v in values:
        errormsg += f"\n `{v}`"
    if style in values:
        await UserSettings.update({"tone": style}).where(UserSettings.slack_id == performer).run()
        await respond(f"Successfully changed to {style} !")
    else:
        await respond(errormsg)

from slack_bolt.async_app import AsyncSay
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.tables import CurrentHuddles, UserSettings

async def message_handler(client: AsyncWebClient, say: AsyncSay, body: dict):
    event = body["event"]
    if "thread_ts" in event.keys():
        is_tracked = await CurrentHuddles.exists().where(CurrentHuddles.thread_ts == event['thread_ts'])
        if is_tracked:
            userid = event["user"]
            text = event["text"]
            await say(f"User {userid} said: {text}")
    else:
        pass

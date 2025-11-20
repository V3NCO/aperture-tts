from slack_bolt.async_app import AsyncSay
from slack_sdk.web.async_client import AsyncWebClient
import logging
from piccolo.query import Select
from glados_slack.tables import CurrentHuddles

async def message_handler(client: AsyncWebClient, say: AsyncSay, body: dict):
    # event = body["event"]
    # user = event["user"]
    # text = event["text"]
    # logging.info(text)
    # await say(f'Body is : {body}')
    await CurrentHuddles.exists().where(CurrentHuddles.name == 'Pythonistas')
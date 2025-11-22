from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.config import config
from glados_slack.tables import CurrentHuddles

async def leave_handler(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
):
    await ack()
    from glados_slack.env import env

    if CurrentHuddles.exists().where(CurrentHuddles.channel_id == channel):
        await env.http.post("http://localhost:7171/leave")
        await CurrentHuddles.delete().where(CurrentHuddles.channel_id == channel).run()
        await respond("Left huddle successsfully !")
    else:
        await respond("I am not in any huddle going on in this channel !")

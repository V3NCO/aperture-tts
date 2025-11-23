from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.config import config
from glados_slack.tables import CurrentHuddles
from glados_slack.huddle_process_manager import destroy_huddle

async def leave_handler(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
):
    await ack()
    from glados_slack.env import logger
    huddleexists = await CurrentHuddles.exists().where(CurrentHuddles.channel_id == channel)
    if huddleexists:
        try:
            await destroy_huddle(channel)
            await CurrentHuddles.delete().where(CurrentHuddles.channel_id == channel).run()
            await respond("Left huddle successfully !")
        except Exception as e:
            logger.error(f"Failed to leave huddle: {e}")
            await respond(f"Failed to leave huddle: {e}")
    else:
        await respond("I am not in any huddle going on in this channel !")

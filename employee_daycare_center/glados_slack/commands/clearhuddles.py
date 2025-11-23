from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.tables import CurrentHuddles
from glados_slack.huddle_process_manager import get_huddle_manager

async def clear_huddle_handle(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
    huddle_channel: str,
):
    from glados_slack.env import logger
    if huddle_channel == "C000ALL":
        await CurrentHuddles.delete(force=True).run()
        try:
            manager = get_huddle_manager()
            await manager.shutdown_all()
        except Exception as e:
            logger.error(f"Error shutting down huddle processes: {e}")

        await respond("All huddles cleared successfully !")
    else:
        huddleexists = await CurrentHuddles.exists().where(CurrentHuddles.channel_id == huddle_channel)
        if huddleexists:
            try:
                manager = get_huddle_manager()
                await manager.destroy_huddle(huddle_channel)
            except Exception as e:
                logger.error(f"Error destroying huddle process: {e}")

            await CurrentHuddles.delete().where(CurrentHuddles.channel_id == huddle_channel).run()

            await respond(f"Huddle from channel <#{huddle_channel}|> cleared successfully")
        else:
            await respond("There is no huddle for that channel")

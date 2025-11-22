from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.tables import CurrentHuddles

async def clear_huddle_handle(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
    huddle_channel: str,
):
    if huddle_channel == "C000ALL":
        await CurrentHuddles.delete(force=True).run()
        await respond("All huddles cleared successfully !")
    else:
        huddleexists = await CurrentHuddles.exists().where(CurrentHuddles.channel_id == huddle_channel)
        if huddleexists:
            await CurrentHuddles.delete().where(CurrentHuddles.channel_id == huddle_channel)
            await respond(f"Huddle from channel <#{huddle_channel}|> cleared successfully")
        else:
            await respond("There is no huddle for that channel")

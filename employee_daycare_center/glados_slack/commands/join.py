from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.config import config
from glados_slack.tables import CurrentHuddles
from glados_slack.huddle_process_manager import get_or_create_huddle, destroy_huddle

async def join_handler(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
):
    await ack()
    from glados_slack.env import env, logger
    rowexists = await CurrentHuddles.exists().where(CurrentHuddles.channel_id == channel)
    logger.info(rowexists)
    if not rowexists:
        payload = {
                "token": config.slack.userbot_token,
                "channel_id": channel,
                "region": "us-east-2" # Yes we are hardcoding us-east-2 because it's always us-east; just like it's always DNS :p
        }
        headers = {"Cookie": f"d={config.slack.userbot_d};"}
        huddle = await env.http.post("https://slack.com/api/rooms.join", data=payload, headers=headers)
        response = await huddle.json()
        logger.info(response)

        if not response.get("ok"):
            logger.error(f"Slack API error: {response.get('error')}")
            await respond(f"Failed to join huddle: {response.get('error')}")
            return

        try:
            hp = await get_or_create_huddle(channel)
            await hp.call("join", {
                "meeting": response["call"]["free_willy"]["meeting"],
                "attendee": response["call"]["free_willy"]["attendee"]
            })
            await CurrentHuddles.insert(CurrentHuddles(channel_id=response['huddle']['channels'][0], thread_ts=response['huddle']['thread_root_ts'])).run()
            await respond(f"Joined huddle in <#{response['huddle']['channels'][0]}|> :3c:")
        except Exception as e:
            logger.error(f"Failed huddle join : {e}")
            await destroy_huddle(channel)
            await respond(f"Failed to join the huddle; Please report this error to the maintainer: {e}")
    else:
        await respond("I am already in this huddle :neodog_pat:")

from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.tables import CurrentHuddles
import os
from IPython.display import Audio

async def soundboard_handler(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
    sound: str
):
    from glados_slack.env import env, logger
    songdir = os.path.join(os.path.dirname(__file__), '../../sounds')
    sounds = os.listdir(songdir)
    current = sound+".wav"
    if current in sounds and sound != "no_sound_selected_error":
        is_tracked = await CurrentHuddles.exists().where(CurrentHuddles.channel_id == channel)
        if is_tracked:
            logger.debug("Channel is tracked")
            audio = Audio(os.path.join(songdir, current)).data
            logger.debug("Grabbed Audio")
            await env.http.post("http://localhost:7171/play-audio", data=audio, headers={"Content-Type": "audio/wav"})
            logger.debug("Sent request to Huddle Handler")
        else:
            await respond("There is no huddle in this channel!")
    elif sound == "no_sound_selected_error":
        available_sounds = ""
        for sound in sounds:
            available_sounds += f"\n`{sound.removesuffix('.wav')}`"
        await respond(f"Please select a song ! The available songs are : {available_sounds}")
    elif current not in sounds:
        available_sounds = ""
        for sound in sounds:
            available_sounds += f"\n`{sound.removesuffix('.wav')}`"
        await respond(f"Incorrect song! Here are the available songs : {available_sounds}")

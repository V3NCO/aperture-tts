from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.tables import CurrentHuddles
from glados_slack.huddle_process_manager import get_or_create_huddle
import os
import base64

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

            audio_path = os.path.join(songdir, current)
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            logger.debug("Grabbed Audio")

            try:
                hp = await get_or_create_huddle(channel)
                await hp.call("play_audio", {"audioBase64": audio_base64})
                logger.debug("sent audio to Huddle process")
            except Exception as e:
                logger.error(f"failed to play audio: {e}")
                await respond(f"failed to play audio: {e}")
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

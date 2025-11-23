from piccolo.query.proxy import ResponseType
from slack_bolt.async_app import AsyncSay
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.tables import CurrentHuddles, UserSettings
from blockkit import Message, Markdown
from blockkit.core import Table, RawText
from glados_slack.config import config
import re
import os
import json
from IPython.display import Audio
from pydub import AudioSegment
from io import BytesIO

async def message_handler(client: AsyncWebClient, say: AsyncSay, body: dict):
    from glados_slack.env import env, logger
    event = body["event"]
    userid = event["user"]
    text = event["text"]
    logger.debug("Received message; Checking")
    if "thread_ts" in event.keys():
        is_tracked = await CurrentHuddles.exists().where(CurrentHuddles.thread_ts == event['thread_ts'])
        if is_tracked:
            logger.debug("Thread is tracked")
            userSaved = await UserSettings.exists().where(UserSettings.slack_id == userid)
            if not userSaved:
                logger.debug("User wasn't saved; saving and messaging")
                await UserSettings.insert(UserSettings(slack_id=userid, tone="Neutral", ignore=False)).run()
                msg = (Message()
                    .add_block(Markdown(text=f"*Hi <@{userid}>*! :glados: I'm sending you this because you sent a message in a huddle thread I'm tracking..."))
                    .add_block(Markdown(text="So. I'm gonna read out your message in the huddle because that's my default behaviour but you can ask me to ignore your messages with `/glados ignore`"))
                    .add_block(Markdown(text="Here is the info I am storing about you (It's the only data I'll ever have about you)."))
                    .add_block(Table(rows=[[RawText("Slack ID"), RawText("Tone"), RawText("Ignore")], [RawText(userid), RawText("Neutral"), RawText("False")]]))
                    .add_block(Markdown(text=f"Also if you need help dm <@{config.slack.maintainer_id}>"))
                    .build()
                )
                await client.chat_postMessage(channel=userid, **msg)
            userSettings = await UserSettings.select().where(UserSettings.slack_id == userid)
            userSettings = userSettings[0]
            logger.debug("Checking if ignored")
            if not userSettings["ignore"]:
                logger.debug("User not ignored : Starting logic")
                audiotrack = AudioSegment.empty()
                pattern1 = re.compile(r"(\[[A-Z]+\])")
                cleanfile = os.path.join(os.path.dirname(__file__), '../../clean.json')

                cleaning = text
                cleaner = json.load(open(cleanfile, "r"))
                for i in cleaner["match"]:
                    cleaning = cleaning.replace(i, cleaner["match"][i])

                if pattern1.search(cleaning):
                    parts = pattern1.split(cleaning)
                    matches = [bool(pattern1.fullmatch(p)) for p in parts]
                    audioparts = []
                    for i, part in enumerate(parts):
                        if matches[i]:
                            soundname = part.removeprefix("[").removesuffix("]").lower()
                            songdir = os.path.join(os.path.dirname(__file__), '../../sounds')
                            sounds = os.listdir(songdir)
                            current = soundname+".wav"
                            if current in sounds:
                                # audio_data = Audio(os.path.join(songdir, current)).data
                                audio = AudioSegment.from_file(os.path.join(songdir, current), format="wav")
                                audioparts.append(audio)
                            else:
                                pass
                        else:
                            if part:
                                tts = await env.http.get("http://localhost:7272/tts", json={"text": part, "tone": userSettings["tone"]})
                                audio_data = await tts.read()
                                audio = AudioSegment.from_file(BytesIO(audio_data), format="wav")
                                audioparts.append(audio)
                    half_silence = AudioSegment.silent(duration=300)
                    for i in audioparts:
                        audiotrack += i
                        audiotrack += half_silence
                    buffer = BytesIO()
                    audiotrack.export(buffer, format="wav")
                    audiotrack = buffer.getvalue()
                else:
                    tts = await env.http.get("http://localhost:7272/tts", json={"text": cleaning, "tone": userSettings["tone"]})
                    audiotrack = await tts.read()
                await env.http.post("http://localhost:7171/play-audio", data=audiotrack, headers={"Content-Type": "audio/wav"})
        else:
            logger.debug("Thread is not tracked")
    else:
        pass

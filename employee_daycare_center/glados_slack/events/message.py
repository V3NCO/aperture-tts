from slack_bolt.async_app import AsyncSay
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.tables import CurrentHuddles, UserSettings
from blockkit import Message, Markdown
from blockkit.core import Table

async def message_handler(client: AsyncWebClient, say: AsyncSay, body: dict):
    event = body["event"]
    userid = event["user"]
    text = event["text"]
    if "thread_ts" in event.keys():
        is_tracked = await CurrentHuddles.exists().where(CurrentHuddles.thread_ts == event['thread_ts'])
        if is_tracked:
            userSaved = await UserSettings.exists().where(UserSettings.slack_id == userid)
            if userSaved:
                userSettings = await UserSettings.select().where(UserSettings.slack_id == userid)
                userSettings = userSettings[0]
                if not userSettings["ignore"]:
                    await say("Non Ignored user talked!")
        else:
            await UserSettings.insert(UserSettings(slack_id=userid, tone="Neutral", ignore=False)).run()
            msg = (Message()
                    .add_block(Markdown(text=f"*Hi <@{userid}>*! :glados: I'm sending you this because you sent a message in a huddle thread I'm tracking..."))
                    .add_block(Markdown(text="So. I'm gonna read out your message in the huddle because that's my default behaviour but you can ask me to ignore your messages with `/glados ignore`"))
                    .add_block(Markdown(text="Here is the info I am storing about you (It's the only data I'll ever have about you)."))
                    .add_block(Table(rows=[["Slack ID", str(userid)], ["Tone", "Neutral"], ["Ignore", "False"]]))
                    .add_block(Markdown(text="Also if you need help dm <@U08L7671TDG>"))
                    .build()
            )
            await client.chat_postMessage(channel=userid, **msg)

    else:
        pass

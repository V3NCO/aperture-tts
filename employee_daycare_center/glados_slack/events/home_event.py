from collections import UserDict
from slack_sdk.web.async_client import AsyncWebClient
from blockkit import Home, Header, Section, Checkboxes, Option
from glados_slack.config import config
from glados_slack.tables import UserSettings


async def app_home_opened(client: AsyncWebClient, body: dict):
    from glados_slack.env import logger
    try:
        settings= await UserSettings.select().where(UserSettings.slack_id == body["event"]["user"])
        checked = []
        if settings[0]["ignore"]:
            checked = [Option("Ignore")]
        await client.views_publish(
            user_id=body["event"]["user"],
            view=Home()
                .add_block(Header("App Settings"))
                .add_block(Section("Ignore thread messages: ", accessory=Checkboxes("ignore_thread_messages_setting", [Option("Ignore")], checked)))
                .build()
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

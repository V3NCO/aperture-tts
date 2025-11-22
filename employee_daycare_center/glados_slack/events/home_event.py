from collections import UserDict
from slack_sdk.web.async_client import AsyncWebClient
from blockkit import Home, Header, Section, Checkboxes, Option, StaticSelect
from glados_slack.tables import UserSettings


async def app_home_opened(client: AsyncWebClient, body: dict):
    from glados_slack.env import logger
    try:
        settings= await UserSettings.select().where(UserSettings.slack_id == body["event"]["user"])
        checked = []
        if settings[0]["ignore"]:
            checked = [Option("Ignore", "ignore")]
        tone_selected = Option("Neutral", "neutral")
        match settings[0]["tone"]:
            case "Standard": tone_selected = Option("Standard", "standard")
            case "Standard_02": tone_selected = Option("Standard 02", "standard_02")
            case "Neutral": tone_selected = Option("Neutral", "neutral")
            case "Deep": tone_selected = Option("Deep", "deep")
            case "Light": tone_selected = Option("Light", "light")

        await client.views_publish(
            user_id=body["event"]["user"],
            view=Home()
                .add_block(Header("App Settings"))
                .add_block(Section("Ignore thread messages: ", accessory=Checkboxes("ignore_thread_messages_setting", [Option("Ignore", "ignore")], checked)))
                .add_block(Section("Tone settings: ", accessory=StaticSelect(action_id="change_tone", options=[Option("Neutral", "neutral"), Option("Deep", "deep"), Option("Light", "light"), Option("Standard", "standard"), Option("Standard 02", "standard_02")], initial_option=tone_selected)))
                .build()
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

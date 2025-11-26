from glados_slack.tables import CurrentHuddles
from glados_slack.config import config
from glados_slack.huddle_process_manager import destroy_huddle


async def huddle_cleaner():
    from glados_slack.env import env, logger
    huddles = await CurrentHuddles.objects()

    for i in huddles:
        payload = {
                "token": config.slack.userbot_token,
                "huddle_id": i.huddle_id,
                "region": "us-east-2" # Yes we are hardcoding us-east-2 because it's always us-east; just like it's always DNS :p
        }
        headers = {"Cookie": f"d={config.slack.userbot_d};"}
        huddle = await env.http.post("https://slack.com/api/huddles.get", data=payload, headers=headers)
        response = await huddle.json()
        if len(response['huddle']['participants']) <= 1:
            try:
                await destroy_huddle(i.channel_id)
                await CurrentHuddles.delete().where(CurrentHuddles.channel_id == i.channel_id).run()
            except Exception as e:
                logger.error(f"Failed to leave huddle: {e}")

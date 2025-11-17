from slack_bolt.async_app import AsyncAck
from slack_bolt.async_app import AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from glados_slack.config import config

async def join_handler(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    channel: str,
    performer: str,
):
    await ack()
    from glados_slack.env import env

    payload = {
            "token": config.slack.userbot_token,
            "channel_id": channel,
            "region": "us-east-2" # Yes we are hardcoding us-east-2 because it's always us-east; just like it's always DNS :p
    }
    headers = {"Cookie": f"d={config.slack.userbot_d};"}
    huddle = await env.http.post("https://blahaj.enterprise.slack.com/api/rooms.join", data=payload, headers=headers)
    response = await huddle.json()
    print(response)
    await respond(f"Joining huddle in <#{response['huddle']['channels'][0]}|>")
    await env.http.post("http://localhost:7171/join", json={"meeting": response["call"]["free_willy"]["meeting"], "attendee": response["call"]["free_willy"]["meeting"]})

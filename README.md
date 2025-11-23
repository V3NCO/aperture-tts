# Aperture TTS

## Set-up a development environment

1. Setup the basic project
```
git clone https://github.com/V3NCO/aperture-tts.git
git submodule init && git submodule update
nix develop
uv sync
```
2. Create a slack bot with this manifest :
```json
{
    "display_information": {
        "name": "Aperture Science GLaDOS Dev Module"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": true,
            "messages_tab_enabled": false,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "GLaDOSBotDev",
            "always_online": false
        },
        "shortcuts": [
            {
                "name": "Hello World!",
                "type": "global",
                "callback_id": "hello_world",
                "description": "Hi there"
            }
        ],
        "slash_commands": [
            {
                "command": "/glados",
                "description": "The master command for Aperture Science GLaDOS TTS!",
                "should_escape": true
            },
            {
                "command": "/dev-glados",
                "description": "Aperture Science is currently working on GLaDOS; Please standby for further information!",
                "should_escape": true
            }
        ]
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "channels:history",
                "channels:join",
                "chat:write",
                "chat:write.customize",
                "commands",
                "groups:history",
                "im:write",
                "im:read",
                "mpim:read",
                "mpim:write"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "bot_events": [
                "app_home_opened",
                "message.channels",
                "message.groups"
            ]
        },
        "interactivity": {
            "is_enabled": true
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": true,
        "token_rotation_enabled": false
    }
}
```
3. Copy the `.env.example` file to `.env` and fill in the values

4. Copy the `employee_daycare_center/.env.sample` file to `employee_daycare_center/.env` and fill in the values

5. Setup the database (Assuming you have a PostgreSQL server with the db created running with the URL in `employee_daycare_center/.env`)
```
cd employee_daycare_center
source .venv/bin/activate
piccolo migrations new glados_slack --auto
piccolo migrations forwards glados_slack
```

6. Run the services (for now it's scuffed)
```
source .venv/bin/activate
uv run main.py
```
```
cd employee_daycare_center
source .venv/bin/activate
app
```
```
cd employee_daycare_center/glados_slack/callhandler
node Huddle.js
```

7. Copy `employee_daycare_center/clean.json.sample` to `employee_daycare_center/clean.json`

8. Create `employee_daycare_center/sounds` and put sound effects in with the format `soundname.wav`; they will be autodetected
## Roadmap
- [x] Better setting up guide
- [ ] Multiple Huddles
- [x] Replace text with stuff tts can read
- [x] User settings ect
- [x] Sound insertions with like *sound*
- [x] Soundboard
- [ ] Discord support
- [ ] Alternate voice? :eyes:

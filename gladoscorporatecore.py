import os
from employee_daycare_center.app import app
from slack_bolt.adapter.socket_mode import SocketModeHandler


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

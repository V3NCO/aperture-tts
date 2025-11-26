from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from glados_slack.tasks.huddle_leave import huddle_cleaner
from glados_slack.config import config


def register_tasks():
    scheduler = AsyncIOScheduler(timezone=config.timezone)
    scheduler.add_job(
        huddle_cleaner,
        "interval",
        minutes=1,
        max_instances=1,
        next_run_time=datetime.now(),
    )

    scheduler.start()

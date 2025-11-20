from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar


ID = "2025-11-20T19:38:50:966394"
VERSION = "1.30.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="glados_slack", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="CurrentHuddles",
        tablename="current_huddles",
        column_name="channel_id",
        db_column_name="channel_id",
        params={"length": 40},
        old_params={"length": 10},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    manager.alter_column(
        table_class_name="UserSettings",
        tablename="user_settings",
        column_name="slack_id",
        db_column_name="slack_id",
        params={"length": 40},
        old_params={"length": 20},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    return manager

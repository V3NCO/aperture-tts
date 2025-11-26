from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2025-11-26T22:00:17:173963"
VERSION = "1.30.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="glados_slack", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="CurrentHuddles",
        tablename="current_huddles",
        column_name="huddle_id",
        db_column_name="huddle_id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 40,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": True,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager

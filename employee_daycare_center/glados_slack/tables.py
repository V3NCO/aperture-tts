# An example of how to create a table. Read the docs for more info: https://piccolo-orm.readthedocs.io/
from piccolo.table import Table
from piccolo.columns import Text, Varchar, Boolean
# class Person(Table):
#     slack_id = Varchar(length=20, index=True)
#     age = Integer()
class CurrentHuddles(Table):
    channel_id = Varchar(length=40, index=True)
    thread_ts = Text()
    huddle_id = Varchar(length=40, index=True)
class UserSettings(Table):
    slack_id = Varchar(length=40, index=True)
    tone = Text()
    ignore = Boolean(default=False)

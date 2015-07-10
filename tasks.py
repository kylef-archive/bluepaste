from invoke import run, task


@task
def migrate():
    from bluepaste.models import User, Blueprint, Revision
    User.create_table()
    Blueprint.create_table()
    Revision.create_table()


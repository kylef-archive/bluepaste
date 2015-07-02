from invoke import run, task


@task
def migrate():
    from bluepaste.models import Blueprint, Revision
    Blueprint.create_table()
    Revision.create_table()


import jwt
from invoke import run, task


@task
def migrate():
    from bluepaste.models import User, Blueprint, Revision
    User.create_table()
    Blueprint.create_table()
    Revision.create_table()


@task
def generate_token(email):
    """
    Generates a valid access token for the given email address.
    """
    from bluepaste.config import JWT_ALGORITHM, JWT_KEY
    encoded = jwt.encode({'email': email}, JWT_KEY, algorithm=JWT_ALGORITHM)
    print('Token for {}: {}'.format(email, encoded))


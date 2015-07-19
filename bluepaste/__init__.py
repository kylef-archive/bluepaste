import os
import hashlib
import logging
from rivr import MiddlewareController, ErrorWrapper, Router
from rivr.views.static import StaticView
from rivr.wsgi import WSGIHandler
from rivr_jinja import JinjaMiddleware, JinjaView
from jinja2 import Environment, FileSystemLoader
from bluepaste.models import database
from bluepaste.resources import router
from bluepaste.middleware import SecureMiddleware, BrowserIDMiddleware
from bluepaste.config import *
import rivr


logger = logging.getLogger('rivr.request')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logger.addHandler(console)


app = Router(
    (r'^static/(?P<path>.*)$', StaticView.as_view(document_root='bluepaste/static/')),
    (r'^.*$', router),
)

# Jinja 2
def gravatar(email, size=100, rating='g', default='retro', force_default=False):
    url = "https://secure.gravatar.com/avatar/"
    hashemail = hashlib.md5(email).hexdigest()
    return "{url}{hashemail}?s={size}&d={default}&r={rating}".format(
        url=url, hashemail=hashemail, size=size,
        default=default, rating=rating)

jinja_environment = Environment(loader=FileSystemLoader('bluepaste/templates'))
jinja_environment.filters['gravatar'] = gravatar


middleware = MiddlewareController.wrap(app,
    SecureMiddleware(),
    database,
    JinjaMiddleware(jinja_environment),
    BrowserIDMiddleware(audience=AUDIENCE, jwt_key=JWT_KEY),
)

middleware = ErrorWrapper(middleware,
    custom_404=JinjaView.as_view(template_name='404.html', environment=jinja_environment)
)

wsgi = WSGIHandler(middleware)


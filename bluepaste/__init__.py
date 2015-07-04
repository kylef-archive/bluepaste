from rivr import MiddlewareController
from rivr.wsgi import WSGIHandler
from rivr_jinja import JinjaMiddleware
from jinja2 import Environment, FileSystemLoader
from bluepaste.models import database
from bluepaste.resources import router
import rivr

jinja_environment = Environment(loader=FileSystemLoader('bluepaste/templates'))
app = MiddlewareController.wrap(router,
    rivr.DebugMiddleware(),
    database,
    JinjaMiddleware(jinja_environment),
)
wsgi = WSGIHandler(app)


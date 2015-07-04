from rivr import MiddlewareController, Router
from rivr.views.static import StaticView
from rivr.wsgi import WSGIHandler
from rivr_jinja import JinjaMiddleware
from jinja2 import Environment, FileSystemLoader
from bluepaste.models import database
from bluepaste.resources import router
import rivr


app = Router(
    (r'^static/(?P<path>.*)$', StaticView.as_view(document_root='bluepaste/static/')),
    (r'^.*$', router),
)

jinja_environment = Environment(loader=FileSystemLoader('bluepaste/templates'))
middleware = MiddlewareController.wrap(app,
    rivr.DebugMiddleware(),
    database,
    JinjaMiddleware(jinja_environment),
)
wsgi = WSGIHandler(middleware)


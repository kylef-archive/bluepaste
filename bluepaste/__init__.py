import logging
from rivr import MiddlewareController, ErrorWrapper, Router
from rivr.views.static import StaticView
from rivr.wsgi import WSGIHandler
from rivr_jinja import JinjaMiddleware, JinjaView
from jinja2 import Environment, FileSystemLoader
from bluepaste.models import database
from bluepaste.resources import router
import rivr


logger = logging.getLogger('rivr.request')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logger.addHandler(console)


app = Router(
    (r'^static/(?P<path>.*)$', StaticView.as_view(document_root='bluepaste/static/')),
    (r'^.*$', router),
)

jinja_environment = Environment(loader=FileSystemLoader('bluepaste/templates'))
middleware = MiddlewareController.wrap(app,
    database,
    JinjaMiddleware(jinja_environment),
)

middleware = ErrorWrapper(middleware,
    custom_404=JinjaView.as_view(template_name='404.html', environment=jinja_environment)
)

wsgi = WSGIHandler(middleware)


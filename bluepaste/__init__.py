from rivr import DebugMiddleware
from rivr.wsgi import WSGIHandler
from bluepaste.models import database
from bluepaste.resources import router


app = DebugMiddleware.wrap(database(router))
wsgi = WSGIHandler(app)


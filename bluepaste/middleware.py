from browserid import verify
import jwt

from rivr.http import Response, ResponseRedirect, ResponseNotFound
from rivr.middleware.base import Middleware
from bluepaste.models import User


class SecureMiddleware(Middleware):
    def process_request(self, request):
        proto = request.headers.get('X_FORWARDED_PROTO')
        if proto == 'http':
            return ResponseRedirect('https://bluepaste.herokuapp.com{}'.format(request.path))



class BrowserIDMiddleware(Middleware):
    audience = None

    login_success_url = '/'
    login_failure_url = '/'
    logout_redirect_url = '/'

    login_url = '/browserid/login'
    logout_url = '/browserid/logout'

    jwt_algorithm = 'HS256'
    jwt_key = None

    def login(self, request):
        data = verify(request.POST['assertion'], self.audience)

        if data and 'email' in data:
            email = data['email']
            user, created = User.create_or_get(email=email)

            response = ResponseRedirect(self.login_success_url)
            encoded = jwt.encode({'email': user.email}, self.jwt_key, algorithm=self.jwt_algorithm)
            response.set_cookie('jwt', encoded, secure=True)
            return response

        return ResponseRedirect(self.login_failure_url)

    def logout(self, request):
        response = ResponseRedirect(self.logout_redirect_url)
        response.delete_cookie('jwt')
        return response

    def process_request(self, request):
        request.browserid_middleware = self

        if 'jwt' in request.COOKIES:
            encoded = request.COOKIES['jwt']
            payload = jwt.decode(encoded, self.jwt_key, algorithms=[self.jwt_algorithm])
            request.browserid = payload['email']
            request.user = User.get(email=request.browserid)
        else:
            request.browserid = None
            request.user = None

        if request.path == self.login_url:
            return self.login(request)
        elif request.path == self.logout_url:
            return self.logout(request)



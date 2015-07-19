import datetime
from hashlib import sha1
from rivr import Response
from rivr_rest import Router, Resource
from rivr_rest_peewee import PeeweeResource
from rivr_jinja import JinjaResponse
from bluepaste.models import database, User, Blueprint, Revision, EXPIRE_CHOICES, EXPIRE_DEFAULT


class BlueprintMixin(object):
    def get_blueprint(self):
        raise NotImplemented

    def get_revision(self):
        raise NotImplemented

    def get_context_data(self):
        return {
            'blueprint': self.get_blueprint(),
            'revision': self.get_revision(),
        }

    def html_provider(self):
        return JinjaResponse(self.request, template_names=['revision.html'], context=self.get_context_data())

    def blueprint_markdown_provider(self):
        return Response(self.get_revision().content, content_type='text/vnd.apiblueprint+markdown')

    def blueprint_ast_provider(self):
        return Response(self.get_revision().ast_json, content_type='application/vnd.apiblueprint.ast.raw+json')


class RevisionResource(PeeweeResource, BlueprintMixin):
    model = Revision
    uri_template = '/{blueprint}/{slug}'

    def get_parameters(self):
        revision = self.get_object()
        return {
            'slug': revision.slug[:8],
            'blueprint': revision.blueprint.slug[:8],
        }

    def get_query(self):
        slug = self.parameters['slug']
        blueprint_slug = self.parameters['blueprint']

        return self.model.select().join(Blueprint).where(
            Blueprint.slug.startswith(blueprint_slug),
            Blueprint.expires > datetime.datetime.now(),
        ).filter(
            Revision.slug.startswith(slug),
        )

    def get_blueprint(self):
        return self.get_object().blueprint

    def get_revision(self):
        return self.get_object()

    def content_type_providers(self):
        providers = super(RevisionResource, self).content_type_providers()
        providers.update({
            'text/vnd.apiblueprint+markdown': self.blueprint_markdown_provider,
            'application/vnd.apiblueprint.ast.raw+json': self.blueprint_ast_provider,
            'text/html': self.html_provider,
        })

        return providers


class BlueprintResource(PeeweeResource, BlueprintMixin):
    model = Blueprint
    uri_template = '/{slug}'
    slug_uri_parameter = 'slug'
    slug_field = 'slug'

    revisions = RevisionResource

    def get_parameters(self):
        obj = self.get_object()
        return {
            'slug': obj.slug[:8],
        }

    def get_query(self):
        slug = self.parameters['slug']
        return self.model.select().filter(Blueprint.slug.startswith(slug), Blueprint.expires >= datetime.datetime.now())

    def get_blueprint(self):
        return self.get_object()

    def get_revision(self):
        return self.get_object().revisions[0]

    def content_type_providers(self):
        providers = super(BlueprintResource, self).content_type_providers()
        providers.update({
            'text/vnd.apiblueprint+markdown': self.blueprint_markdown_provider,
            'application/vnd.apiblueprint.ast.raw+json': self.blueprint_ast_provider,
            'text/html': self.html_provider,
        })

        return providers

    def post(self, request):
        blueprint = self.get_object()
        if request.content_length == 0:
            return Response(status=400)

        content_type = request.headers.get('CONTENT_TYPE', None)

        if content_type == 'text/vnd.apiblueprint+markdown':
            content = request.body.read(request.content_length)
            message = ''
        else:
            content = request.POST.get('blueprint', '')
            message = request.POST.get('message', '')
            if len(content) == 0:
                return Response(status=400)

        revision = blueprint.create_revision(message, content)
        resource = self.revisions(obj=revision)
        resource.request = request
        response = resource.get(request)

        if response.status_code == 200:
            response.status_code = 201

        return response


class RootResource(Resource):
    uri_template = '/'

    def content_type_providers(self):
        def html_provider():
            with open('bluepaste/static/polls-api.md', 'r') as fp:
                blueprint = fp.read()

            return JinjaResponse(self.request, template_names=['index.html'], context={
                'default_blueprint': blueprint,
                'expire_choices': EXPIRE_CHOICES,
                'expire_default': EXPIRE_DEFAULT,
            })

        providers = super(RootResource, self).content_type_providers()
        providers.update({
            'text/html': html_provider,
        })

        return providers

    def post(self, request):
        if request.content_length == 0:
            return Response(status=400)

        content_type = request.headers.get('CONTENT_TYPE', None)
        message = 'Initial blueprint'

        if content_type == 'text/vnd.apiblueprint+markdown':
            content = request.body.read(request.content_length)
            expires = EXPIRE_DEFAULT
        else:
            content = request.POST.get('blueprint', '')
            if len(content) == 0:
                return Response(status=400)
            expires = request.POST.get('expires', EXPIRE_DEFAULT)
            message = request.POST.get('message', message)

        expires = datetime.datetime.now() + \
            datetime.timedelta(seconds=int(expires))

        slug = sha1(datetime.datetime.now().isoformat() + content).hexdigest()
        blueprint = Blueprint.create(slug=slug, expires=expires,
                author=request.user)
        revision = blueprint.create_revision(message, content)
        resource = BlueprintResource(obj=blueprint)
        resource.request = request
        response = resource.get(request)

        if response.status_code == 200:
            response.status_code = 302
            response.headers['Location'] = resource.get_uri()

        return response


router = Router(
    RootResource,
    BlueprintResource,
    RevisionResource,
)


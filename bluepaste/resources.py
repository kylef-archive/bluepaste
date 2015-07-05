import datetime
from hashlib import sha1
from rivr import Response
from rivr_rest import Router, Resource
from rivr_rest_peewee import PeeweeResource
from rivr_jinja import JinjaResponse
from bluepaste.models import database, Blueprint, Revision, EXPIRE_CHOICES, EXPIRE_DEFAULT


class RevisionResource(PeeweeResource):
    model = Revision
    uri_template = '/{blueprint}/{slug}'

    def get_parameters(self):
        revision = self.get_object()
        return {
            'slug': revision.slug[:8],
            'blueprint': revision.blueprint.slug,
        }

    def get_query(self):
        slug = self.parameters['slug']
        blueprint_slug = self.parameters['blueprint']

        return self.model.select().filter(
            Revision.slug.startswith(slug),
            blueprint__slug=blueprint_slug,
            blueprint__expires__gt=datetime.datetime.now(),
        )

    def content_type_providers(self):
        def blueprint_markdown_provider():
            return Response(self.get_object().content, content_type='text/vnd.apiblueprint+markdown')

        def html_provider():
            return JinjaResponse(self.request, template_names=['revision.html'], context={'revision': self.get_object()})

        providers = super(RevisionResource, self).content_type_providers()
        providers.update({
            'text/vnd.apiblueprint+markdown': blueprint_markdown_provider,
            'text/html': html_provider,
        })

        return providers


class BlueprintResource(PeeweeResource):
    model = Blueprint
    uri_template = '/{slug}'
    slug_uri_parameter = 'slug'
    slug_field = 'slug'

    revisions = RevisionResource

    def get_query(self):
        return self.model.select().filter(Blueprint.expires >= datetime.datetime.now())

    def content_type_providers(self):
        def blueprint_markdown_provider():
            return Response(self.get_object().revisions[0].content, content_type='text/vnd.apiblueprint+markdown')

        def html_provider():
            return JinjaResponse(self.request, template_names=['blueprint.html'], context={'blueprint': self.get_object()})

        providers = super(BlueprintResource, self).content_type_providers()
        providers.update({
            'text/vnd.apiblueprint+markdown': blueprint_markdown_provider,
            'text/html': html_provider,
        })

        return providers

    def post(self, request):
        blueprint = self.get_object()
        if request.content_length == 0:
            return Response(status=400)

        content_type = request.headers.get('CONTENT_TYPE', None)

        if content_type == 'text/vnd.apiblueprint+markdown':
            content = request.body.read(request.content_length)
        else:
            content = request.POST.get('blueprint', '')
            if len(content) == 0:
                return Response(status=400)


        revision = blueprint.create_revision(content)
        response = self.revisions(obj=revision).get(request)

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

        if content_type == 'text/vnd.apiblueprint+markdown':
            content = request.body.read(request.content_length)
            expires = EXPIRE_DEFAULT
        else:
            content = request.POST.get('blueprint', '')
            if len(content) == 0:
                return Response(status=400)
            expires = request.POST.get('expires', EXPIRE_DEFAULT)

        expires = datetime.datetime.now() + \
            datetime.timedelta(seconds=int(expires))

        slug = sha1(datetime.datetime.now().isoformat() + content).hexdigest()[:8]
        blueprint = Blueprint.create(slug=slug, expires=expires)
        revision = blueprint.create_revision(content)
        revision_resource = RevisionResource(obj=revision)
        response = revision_resource.get(request)

        if response.status_code == 200:
            response.status_code = 302
            response.headers['Location'] = revision_resource.get_uri()

        return response


router = Router(
    RootResource,
    BlueprintResource,
    RevisionResource,
)


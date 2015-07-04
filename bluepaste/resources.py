from datetime import datetime
from hashlib import sha1
from rivr import Response
from rivr_rest import Router, Resource
from rivr_rest_peewee import PeeweeResource
from rivr_jinja import JinjaResponse
from bluepaste.models import database, Blueprint, Revision


class RevisionResource(PeeweeResource):
    model = Revision
    uri_template = '/{blueprint}/{slug}'

    def get_parameters(self):
        revision = self.get_object()
        return {
            'slug': revision.slug,
            'blueprint': revision.blueprint.slug,
        }

    def get_object(self):
        if not self.obj:
            blueprint_slug = self.parameters['blueprint']
            slug = self.parameters['slug']
            self.obj = self.get_query().filter(
                slug=slug,
                blueprint__slug=blueprint_slug
            ).get()

        return self.obj

    def content_type_providers(self):
        def blueprint_markdown_provider():
            return Response(self.get_object().content, content_type='text/vnd.apiblueprint+markdown')

        providers = super(RevisionResource, self).content_type_providers()
        providers.update({
            'text/vnd.apiblueprint+markdown': blueprint_markdown_provider,
        })

        return providers


class BlueprintResource(PeeweeResource):
    model = Blueprint
    uri_template = '/{slug}'
    slug_uri_parameter = 'slug'
    slug_field = 'slug'

    revisions = RevisionResource

    def content_type_providers(self):
        def blueprint_markdown_provider():
            return Response(self.get_object().revisions[0].content, content_type='text/vnd.apiblueprint+markdown')

        providers = super(BlueprintResource, self).content_type_providers()
        providers.update({
            'text/vnd.apiblueprint+markdown': blueprint_markdown_provider,
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
            return JinjaResponse(self.request, template_names=['index.html'], context={})

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
        else:
            content = request.POST.get('blueprint', '')
            if len(content) == 0:
                return Response(status=400)

        slug = sha1(datetime.now().isoformat() + content).hexdigest()[:8]
        blueprint = Blueprint.create(slug=slug)
        revision = blueprint.create_revision(content)
        response = BlueprintResource(obj=blueprint).get(request)

        if response.status_code == 200:
            response.status_code = 201

        return response


router = Router(
    RootResource,
    BlueprintResource,
    RevisionResource,
)


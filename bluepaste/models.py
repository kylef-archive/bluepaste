import datetime
import json
from hashlib import sha1
import requests
import peewee
from rivr_peewee import Database
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer
from pygments_markdown_lexer.lexer import MarkdownLexer


database = Database()


EXPIRE_CHOICES = (
    (600,        'In 10 minutes'),
    (3600,       'In one hour'),
    (3600*24,    'In one day'),
    (3600*24*7,  'In one week'),
    (3600*24*14, 'In two weeks'),
    (3600*24*30, 'In one month'),
)

EXPIRE_DEFAULT = 3600*24*14


class User(database.Model):
    email = peewee.CharField(unique=True)


class Blueprint(database.Model):
    slug = peewee.CharField(max_length=40, unique=True)
    expires = peewee.DateTimeField()
    author = peewee.ForeignKeyField(User, related_name='blueprints', null=True)

    def create_revision(self, content):
        created_at = datetime.datetime.now()
        slug_content = '{}\n{}'.format(created_at.isoformat(), content)
        slug = sha1(slug_content).hexdigest()
        return Revision.create(blueprint=self, slug=slug, content=content)

    @property
    def last_revision(self):
        return self.revisions[0]


class Revision(database.Model):
    blueprint = peewee.ForeignKeyField(Blueprint, related_name='revisions')
    slug = peewee.CharField(max_length=40, unique=True)
    content = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-created_at',)
        indexes = (
            (('blueprint', 'slug'), True),
        )

    def __str__(self):
        return self.content

    @property
    def highlighted_content(self):
        return highlight(self.content, MarkdownLexer(), HtmlFormatter())

    @property
    def ast(self):
        if not hasattr(self, '_ast'):
            self._ast = requests.post('https://api.apiblueprint.org/parser', data=self.content).json()['ast']

        return self._ast

    @property
    def highlighted_ast(self):
        ast = json.dumps(self.ast, sort_keys=True, indent=2, separators=(',', ': '))
        return highlight(ast, JsonLexer(), HtmlFormatter())

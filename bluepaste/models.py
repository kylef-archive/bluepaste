import datetime
from hashlib import sha1
import peewee
from rivr_peewee import Database


database = Database()


class Blueprint(database.Model):
    slug = peewee.CharField(max_length=32, unique=True)

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
    slug = peewee.CharField(max_length=32, unique=True)
    content = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-created_at',)
        indexes = (
            (('blueprint', 'slug'), True),
        )

    def __str__(self):
        return self.content


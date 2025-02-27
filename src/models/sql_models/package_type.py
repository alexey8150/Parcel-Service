from tortoise import fields, models


class PackageType(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.TextField(null=False)

    packages = fields.ReverseRelation['Package']

    class Meta:
        table = "package_type"

    def __str__(self):
        return self.name

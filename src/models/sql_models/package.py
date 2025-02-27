from tortoise import fields, models

from .package_type import PackageType


class Package(models.Model):
    id: int = fields.IntField(primary_key=True)
    name: str = fields.TextField(null=False)
    weight: float = fields.FloatField(null=False)
    content_price: float = fields.FloatField(null=False)
    shipping_price: float = fields.FloatField(null=True)
    is_calculated: bool = fields.BooleanField(null=False, default=False)
    user_uuid: str = fields.TextField(null=False)
    transport_company: int = fields.IntField(null=True)

    type: fields.ForeignKeyRelation[PackageType] = fields.ForeignKeyField(
        "models.PackageType",
        related_name="packages")

    class Meta:
        table = "package"

    def __str__(self):
        return self.name

    async def to_dict(self):
        type_data = {"id": self.type.id, "name": self.type.name} if self.type else None

        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
            "content_price": self.content_price,
            "shipping_price": self.shipping_price,
            "is_calculated": self.is_calculated,
            "user_uuid": self.user_uuid,
            "transport_company": self.transport_company,
            "type": type_data
        }

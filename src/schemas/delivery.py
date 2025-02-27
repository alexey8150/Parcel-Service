from pydantic import BaseModel, conint


class DeliveryCompanySchema(BaseModel):
    company_id: conint(ge=1)

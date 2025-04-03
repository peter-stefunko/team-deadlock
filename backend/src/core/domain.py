from pydantic import BaseModel, ConfigDict


class CustomDomainBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

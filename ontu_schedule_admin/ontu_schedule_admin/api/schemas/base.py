import pydantic
from ninja import Schema as APISchema  # noqa: F401


class Schema(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        from_attributes=True,
    )

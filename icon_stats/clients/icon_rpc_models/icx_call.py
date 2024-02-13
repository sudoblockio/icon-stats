from pydantic import BaseModel, ConfigDict


class GenericIcxCallModel(BaseModel):
    """
    We don't know the response of icx_call so this is a generic response used unless a
     model has been given.
    """

    model_config = ConfigDict(
        extra="allow",
    )

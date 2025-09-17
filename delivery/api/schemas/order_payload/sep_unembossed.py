from pydantic import BaseModel, constr


class ClientCodePayload(BaseModel):
    client_code: constr(min_length=1, max_length=256)

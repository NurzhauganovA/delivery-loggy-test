from pydantic import BaseModel, constr



class CardPayload(BaseModel):
    pan: constr(min_length=16, max_length=16)


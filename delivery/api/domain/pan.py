from pydantic import BaseModel, constr


class Pan(BaseModel):
    value: constr(min_length=16, max_length=16)

    class Config:
        frozen = True

    def get_suffix(self) -> str:
        return self.value[-4:]

    def get_masked(self) -> str:
        return self.value[:4] + '*' * 8 + self.value[-4:]

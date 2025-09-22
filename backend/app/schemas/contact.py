from pydantic import BaseModel

class ContactBase(BaseModel):
    name: str
    phone: str

class ContactCreate(ContactBase):
    pass

class ContactRead(ContactBase):
    id: int

    class Config:
        orm_mode = True
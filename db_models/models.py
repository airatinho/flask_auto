from pydantic import BaseModel
from datetime import date

class DilerVal(BaseModel):
    name: str
    address: str

class CarVal(BaseModel):
    name: str
    sold: bool
    year_of_manufacture: date #здесь можно поставить валидацию на дату, или просто строку чтобы было легче жить
    color: str
    broken: bool
    price: int
    num_owners: int
    diler_id:int
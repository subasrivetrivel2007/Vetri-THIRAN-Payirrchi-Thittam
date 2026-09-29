from pydantic import BaseModel, Field, field_validator
class ItemNeed(BaseModel):
    name: str = Field(min_length=1,max_length=80)
    quantity: int = Field(default=1,ge=1,le=100)
class HomeRequest(BaseModel):
    budget: float = Field(gt=0,le=100000000)
    currency: str = Field(default='INR',min_length=3,max_length=3)
    rooms: list[str] = Field(min_length=1,max_length=8)
    style: str = Field(default='Modern',max_length=80)
    items: list[ItemNeed] = Field(default_factory=lambda:[ItemNeed(name='Lighting')],max_length=20)
    preferences: str = Field(default='',max_length=1000)
    @field_validator('currency')
    @classmethod
    def upper_currency(cls,v): return v.upper()
class PartyRequest(BaseModel):
    budget: float = Field(gt=0,le=100000000)
    currency: str = Field(default='INR',min_length=3,max_length=3)
    guests: int = Field(ge=1,le=10000)
    event_type: str = Field(min_length=1,max_length=80)
    venue: str = Field(default='Not decided',max_length=120)
    preferences: str = Field(default='',max_length=1000)
    @field_validator('currency')
    @classmethod
    def upper_currency(cls,v): return v.upper()
class JewelryRequest(BaseModel):
    budget: float = Field(gt=0,le=100000000)
    currency: str = Field(default='INR',min_length=3,max_length=3)
    occasion: str = Field(min_length=1,max_length=80)
    style: str = Field(default='Elegant',max_length=80)
    outfit_description: str = Field(default='',max_length=1000)
    @field_validator('currency')
    @classmethod
    def upper_currency(cls,v): return v.upper()

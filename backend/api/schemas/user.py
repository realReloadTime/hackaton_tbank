from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UsernameRequest(UserBase):
    pass


class UserTickerResponse(BaseModel):
    user_id: int
    ticker_id: int

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    user_id: int
    preferences: Optional[List[UserTickerResponse]]

    class Config:
        from_attributes = True


class AddPreferenceRequest(BaseModel):
    user_id: int
    ticker_id: int


class DeletePreferenceRequest(BaseModel):
    username: str
    ticker_id: int

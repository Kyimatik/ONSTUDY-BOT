from pydantic import BaseModel, Field
from typing import Optional

class UserCheck(BaseModel):
    user_id : int


class ChannelCheckResponse(BaseModel):
    is_member: bool
    
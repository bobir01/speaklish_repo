from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """User model
    :param id: user id in database = None
    :param fullname: user full name
    :param username: user username = None
    :param user_id: user id in telegram
    :param joined_at: date of registration = now()
    :param is_active: user status

    """
    id: Optional[int] = None
    fullname: str
    username: Optional[str] = None
    user_id: int
    joined_at: datetime = datetime.now()
    is_active: bool = True
    referral: Optional[str] = None
    phone: Optional[str] = None

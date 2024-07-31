import json
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, UUID4, ConfigDict
from typing import Optional


class Session(BaseModel):
    """Session model used for storing session data in the database and caching
    :param id: id pk in the database
    :type id: int = Field(None, alias='id')
    :param user_id: id of the user who started the session
    :type user_id: int = Field(..., alias='user_id')
    :param session_id: unique session id
    :type session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='session_id')
    :param total_audio_length: total length of the audio recorded by the user
    :type total_audio_length: int = Field(0, alias='total_audio_length')
    :param used_tokens: number of tokens used by the user
    :type used_tokens: int = Field(0, alias='used_tokens')
    :param final_prompt: final prompt of the session
    :type final_prompt: Optional[str] = Field(None, alias='final_prompt')
    :param model_answer: model answer of the session
    :type model_answer: Optional[str] = Field(None, alias='model_answer')
    :param stop_reason: reason for stopping the session
    :type stop_reason: Optional[str] = Field(None, alias='stop_reason')
    :param finish_state: state of the session
    :type finish_state: Optional[str] = Field(None, alias='finish_state')
    :param finished_at: datetime when the session was finished
    :type finished_at: Optional[datetime] = Field(None, alias='finished_at')
    :param created_at: datetime when the session was created
    :type created_at: datetime = Field(default_factory=datetime.now, alias='created_at')
    """
    id: Optional[int] = Field(None, alias='id')
    user_id: int = Field(..., alias='user_id')
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias='session_id')
    total_audio_length: int = Field(0, alias='total_audio_length')
    used_tokens: int = Field(0, alias='used_tokens')
    final_prompt: Optional[str] = Field(None, alias='final_prompt')
    model_answer: Optional[str] = Field(None, alias='model_answer')
    stop_reason: Optional[str] = Field(None, alias='stop_reason')
    finish_state: Optional[str] = Field(None, alias='finish_state')
    finished_at: Optional[datetime] = Field(None, alias='finished_at')
    created_at: datetime = Field(default_factory=datetime.now, alias='created_at')

    model_config = ConfigDict(protected_namespaces=(), )

    def bulk_update(self, **kwargs):
        """updaet multiple param at once and return the updated model"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'total_audio_length':
                    setattr(self, key, getattr(self, key) + value)
                    continue
                if key == 'used_tokens':
                    setattr(self, key, getattr(self, key) + value)
                    continue
                if key == 'final_prompt':
                    setattr(self, key, json.dumps(value))
                    continue
                setattr(self, key, value)
        if getattr(self, 'finished_at') is None:
            self.finished_at = datetime.now()

        return self


class Feedback(BaseModel):
    id: Optional[int] = Field(None, alias='id')
    user_id: int = Field(..., alias='user_id')
    user_feedback: str = Field(..., alias='user_feedback')
    is_positive: Optional[bool] = Field(None, alias='is_positive')
    session_id: str = Field(..., alias='session_id')
    created_at: datetime = Field(default_factory=datetime.now, alias='created_at')

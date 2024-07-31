from __future__ import annotations

from typing import List, Dict
from django.conf import settings




class PromptProcessor:
    """
    Process transcript and questions to get prompt for OpenAI
    combined with examiner messages
    :NOTE: there is no pronunciation assessment in the transcript
    """

    def __init__(self, short: bool = False):
        self.messages = None
        self.user_txt = ""
        self.system_txt = settings.SYSTEM_TEXT
        self.data = {'part_1': [], 'part_2': None, 'part_3': []}
        self.current_section = 'part_1'

    @property
    def prepared(self):
        """prepared messages for OpenAI"""
        self.messages = [
            {'role': 'system',
             'content': self.system_txt},
            {'role': 'user',
             'content': self.user_txt},
        ]
        return self.messages



    def set_examiner_message(self, msg: str):
        """set examiner messages"""
        self.user_txt += f'Examiner: {msg}\n'

    def add_pronunciation_assessment(self, assessment: Dict[str, float], mispronounced_words: List[str]):

        pass


    def set_candidate_message(self, msg: str):
        """set candidate messages"""
        self.user_txt += f'Candidate: {msg}\n'

    def set_messages(self, examiner_msg: str, candidate_msg: str):
        """set examiner and candidate messages both"""
        pass

    def add_part_header(self, part: int):
        """add part header and updates current section too"""
        pass

from __future__ import annotations

from typing import List, Dict

from schemas import RecognitionResult
from loader import config


class PromptProcessor:
    """
    Process transcript and questions to get prompt for OpenAI
    combined with examiner messages
    :NOTE: there is no pronunciation assessment in the transcript
    """

    def __init__(self, short: bool = False):
        self.encoder = None
        self.messages = None
        self.user_txt = ""
        self.system_txt = config.system_text if not short else config.system_text_short
        self.data = {"part_1": [], "part_2": None, "part_3": []}
        self.current_section = "part_1"

    @property
    def prepared(self):
        pass

    @property
    def tokens(self):
        pass

    def add_pronunciation_assessment(self, assessment: RecognitionResult | dict):
        pass


    def set_examiner_message(self, msg: str):
        """set examiner messages"""
        self.user_txt += f"Examiner: {msg}\n"

    def set_candidate_message(self, msg: str):
        """set candidate messages"""
        self.user_txt += f"Candidate: {msg}\n"

    def set_messages(self, examiner_msg: str, candidate_msg: str):
        """set both examiner and candidate messages"""
        pass


    def add_part_header(self, part: int):

        pass


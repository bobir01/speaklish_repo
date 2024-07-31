from pydantic import BaseModel
from typing import List, Optional


class Word(BaseModel):
    Word: str
    Offset: int
    Duration: int
    Confidence: float
    AccuracyScore: float
    ErrorType: str

    @property
    def mispronounced(self):
        """Returns True if the word is mispronounced"""
        return self.ErrorType == 'Mispronunciation'

    @property
    def reference_url(self):
        """Returns the url to the word definition"""
        return "https://www.oxfordlearnersdictionaries.com/definition/english/" + self.Word.lower()

    @property
    def a_tag(self):
        """Returns the html a tag for the word definition"""
        return f"<a href='{self.reference_url}'>{self.Word}</a>"


class NBestItem(BaseModel):
    Confidence: float
    Lexical: str
    ITN: str
    MaskedITN: str
    Display: str
    AccuracyScore: float
    FluencyScore: float
    CompletenessScore: float
    PronScore: float
    Words: List[Word]

    def get_mispronounced(self):
        return [word for word in self.Words if word.mispronounced]


class RecognitionResult(BaseModel):
    RecognitionStatus: str
    Offset: int
    Duration: int
    NBest: List[NBestItem]
    DisplayText: str

    def get_mispronounced(self) -> Optional[List[Word]]:
        return self.NBest[0].get_mispronounced()

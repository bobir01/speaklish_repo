import json
import os
import time
from typing import List, Dict
from django.conf import settings




def calculate_pronunciation_score(pronunciation_result):
    # Calculate pronunciation score
    pronunciation_score = 0
    accuracy_score = 0
    fluency_score = 0
    prosody_score = 0
    completeness_score = 0

    length = len(pronunciation_result)
    skipper = 0
    for result in pronunciation_result:
        if not hasattr(result, 'pronunciation_score'):
            skipper += 1
            continue
        pronunciation_score += result.pronunciation_score
        accuracy_score += result.accuracy_score
        fluency_score += result.fluency_score
        prosody_score += result.prosody_score
        completeness_score += result.completeness_score

    length -= skipper
    pronunciation_score = round(pronunciation_score / length, 2)
    accuracy_score = round(accuracy_score / length, 2)
    fluency_score = round(fluency_score / length, 2)
    prosody_score = round(prosody_score / length, 2)
    completeness_score = round(completeness_score / length, 2)

    return {
        "pronunciation_score": pronunciation_score,
        "accuracy_score": accuracy_score,
        "fluency_score": fluency_score,
        "prosody_score": prosody_score,
        "completeness_score": completeness_score
    }


def get_mispronounced_words(pronunciation_result):
    # Get mispronounced words
    mispronounced_words = []
    skipper = 0
    for result in pronunciation_result:
        if not hasattr(result, 'words'):
            skipper += 1
            continue
        for word in result.words:
            if word.error_type == 'Mispronunciation':
                mispronounced_words.append(word.word)
    return set(mispronounced_words)


# please refer to Reading sample to get pronunciation/accuracy/fluency/prosody score.
def pronunciation_assessment(audio_filename: str, topic: str = None) -> Dict:
    """
    pronunciation assessment
    :param audio_filename: audio file path
    :param topic: optional topic

    :return: Dict = {
        'pronunciation_score': float,
        'mispronounced_words': List[str],
        'content_result': Dict
        }

    """
    pass

from rest_framework import serializers
from typing import Dict, Any


def validate_audio_attrs(attrs: Dict[str, Any]):
    voice_audio = attrs.get("voice_audio")
    if voice_audio is None:
        raise serializers.ValidationError("'voice_audio' is required")
    file_name = voice_audio.name
    file_ext = file_name.split('.')[-1]
    if file_ext not in ['mp3', 'wav', 'ogg']:
        raise serializers.ValidationError("File %s extension is not valid" % file_ext)
    size = voice_audio.size / 1024 / 1024
    if size > 20:
        raise serializers.ValidationError("File %s size is not valid, must be less than 20" % round(size, 2))
    return attrs

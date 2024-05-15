"""
    Можно использовать чтобы послушать как STT воспринимает планируемое триггер слово
"""

from whisper_mic import WhisperMic

mic = WhisperMic()
result = mic.listen()
print(result)

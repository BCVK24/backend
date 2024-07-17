import json
import os
import numpy as np
import subprocess

from io import BytesIO
from typing import List, Tuple

from pydub import AudioSegment
from pyannote.audio import Pipeline
from fuzzywuzzy import process


RUSSIAN_VOCABULARY = {letter: index + 1 for index, letter in enumerate("абвгдежзийклмнопрстуфхцчшщъыьэюя")}


def audiosegment_to_numpy(audiosegment: AudioSegment) -> np.ndarray:
    """Convert AudioSegment to numpy array."""
    samples = np.array(audiosegment.get_array_of_samples())
    if audiosegment.channels == 2:
        samples = samples.reshape((-1, 2))

    samples = samples.astype(np.float32, order="C") / 32768.0
    return samples


def segment_audio(
    audio_path: str,
    pipeline: Pipeline,
    max_duration: float = 22.0,
    min_duration: float = 15.0,
    new_chunk_threshold: float = 0.2,
) -> Tuple[List[np.ndarray], List[List[float]]]:

    audio = AudioSegment.from_wav(audio_path)
    audio_bytes = BytesIO()
    audio.export(audio_bytes, format="wav")
    audio_bytes.seek(0)

    sad_segments = pipeline({"uri": "filename", "audio": audio_bytes})

    segments = []
    curr_duration = 0
    curr_start = 0
    curr_end = 0
    boundaries = []
    
    for segment in sad_segments.get_timeline().support():
        start = max(0, segment.start)
        end = min(len(audio) / 1000, segment.end)
        if (
            curr_duration > min_duration and start - curr_end > new_chunk_threshold
        ) or (curr_duration + (end - curr_end) > max_duration):
            audio_segment = audiosegment_to_numpy(
                audio[curr_start * 1000 : curr_end * 1000]
            )
            segments.append(audio_segment)
            boundaries.append([curr_start, curr_end])
            curr_start = start

        curr_end = end
        curr_duration = curr_end - curr_start

    if curr_duration != 0:
        audio_segment = audiosegment_to_numpy(
            audio[curr_start * 1000 : curr_end * 1000]
        )
        segments.append(audio_segment)
        boundaries.append([curr_start, curr_end])

    return segments, boundaries


def convert_wav(speech_filename):
    new_filename = f'{os.path.basename(speech_filename).split(".")[0]}_patched.wav'
    command = ['ffmpeg', '-i', speech_filename, '-ac', '1', '-ar', '16000', new_filename, '-y']

    subprocess.run(command)
    
    return new_filename

def filter(forced_alignments: list[str, float, float]) -> list[str, float, float, bool]:
        """Метод для фильтрации размеченных токенов с временными метками, пока 
        рассматриваются 3 кейса: некоторые мусорные слова, матные и повторяющиеся. Параметр
        is_trash означает нужно ли удалять данный токен"""
        
        with open("wordlist/bad_words.json", "r") as file:
            bad_words = file.read()
            bad_words = json.loads(bad_words)
 
        waste_words = ['ну', 'типа', 'кста', 'типо', 'блин', 'че', 'чё', "аааа",
                    "ээээ",
                    "нуууу",
                    "короче",
                    "типа",
                    "блин",
                    "жесть"]
        
        marked_tokens = []
        prev_word = ''
        
        for token_with_time in forced_alignments:
            is_trash = False
            # 1 case - waste words
            similiar_waste = process.extractOne(token_with_time[0], waste_words)
            
            if int(similiar_waste[-1]) > 95:
                is_trash = True
            
            # 2 case - ban words
            is_trash = token_with_time[0] in bad_words.keys()
                
            # 3 case - repeat words
            if token_with_time[0] == prev_word:
                is_trash = True
            
            prev_word = token_with_time[0]
            marked_tokens.append([token_with_time[0], token_with_time[1], token_with_time[2], is_trash])

        return marked_tokens

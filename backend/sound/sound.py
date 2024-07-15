import numpy as np
from scipy.signal import medfilt
import wave
import io


def average(data, kernel_size):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[kernel_size:] - cumsum[:-kernel_size]) / kernel_size


async def sound_filtration(sound_data: bytes) -> bytes:
    with wave.open(io.BytesIO(sound_data)) as sound:
        params = sound.getparams()
        data = np.frombuffer(sound.readframes(params.nframes), dtype=np.int16)

        result = medfilt(data, 3)
        result = np.pad(result, (0, len(data) - len(result)))
        result = result.astype(np.int16)

    ret = io.BytesIO()

    with wave.open(ret, 'wb') as rt:
        rt.setparams(params)
        rt.writeframes(result.tobytes())

    ret.seek(0)

    return ret.read()


async def get_road(data: bytes):

    wav_file = wave.open(io.BytesIO(data), 'rb')

    signal = wav_file.readframes(-1)
    if wav_file.getsampwidth() == 1:
        signal = np.array(np.frombuffer(signal, dtype='UInt8') - 128, dtype=np.int8)
    elif wav_file.getsampwidth() == 2:
        signal = np.frombuffer(signal, dtype=np.int16)

    deinterleaved = [signal[idx::wav_file.getnchannels()] for idx in range(wav_file.getnchannels())]

    wav_file.close()

    return average(deinterleaved[0], 128).tolist()[::64]
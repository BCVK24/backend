from asr_inference import ASRInference
from utils import convert_wav, filter

model_config = {
            'model_weights': '../ml/ctc_model_weights.ckpt',
            'device': 'cuda', 'batch_size': 1, 'model_type': 'tiny',
            'model_config': 'conf/ctc_model_config.yaml'}
SPEECH_FILE = "data_for_tests/test_60.wav"
speech = convert_wav(SPEECH_FILE)

asr = ASRInference('GigaAM', model_config)
alignments = asr.forced_align(speech)
alignments_filter = filter(alignments)

print(alignments)
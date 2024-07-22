from .asr_inference import ASRInference
from .utils import convert_wav, filter

model_config = {
            'model_weights': '../ml/ctc_model_weights.ckpt',
            'device': 'cuda', 'batch_size': 1, 'model_type': 'tiny',
            'model_config': '/home/ubuntu/backend/backend/worker/ML/conf/ctc_model_config.yaml'}

asr = ASRInference('GigaAM', model_config)
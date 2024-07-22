from .asr_inference import ASRInference
from .filter_abstract import FilterAbstract
from .utils import convert_wav


# SPEECH_FILE = "/media/disk2/ml_rewrite/misc.mp3"
# speech = convert_wav(SPEECH_FILE)

# Получение выравнивания с помощью ASR-модели
model_config = {
            'model_weights': '/media/disk2/ml/ctc_model_weights.ckpt',
            'device': 'cuda', 'batch_size': 1, 'model_type': 'CTC',
            'model_config': '/home/ubuntu/backend/backend/worker/ML/conf/ctc_model_config.yaml'}

asr = ASRInference('GigaAM', model_config)
# alignments = asr.forced_align(speech)

# Фильтрация выравнивания с помощью BERT-модели
filter_model_config = {'model_path': '/media/disk2/ruslan_models/ruBert-base_again_100epoch_without_punctuation/checkpoint-215200', 
                       'device': 'cuda'}

bert = FilterAbstract(model_name='cointegrated/rubert-tiny2',
                      model_config=filter_model_config)

# alignments_filter = bert.filter(alignments)

# Вывод результата фильтрации
# print(alignments_filter)


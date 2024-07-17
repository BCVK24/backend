from .schemas import ResultRead
from ..recordings.schemas import RecordingRead


class ResultRel(ResultRead):
    source: RecordingRead

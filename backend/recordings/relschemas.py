from .schemas import RecordingRead
from ..users.schemas import UserRead
from ..results.schemas import ResultRead
from ..tags.schemas import TagRead


class RecordingRel(RecordingRead):
    creator: UserRead
    tags: list[TagRead]
    results: list[ResultRead]

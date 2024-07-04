from .schemas import UserRead
from ..recordings.schemas import RecordingRead


class UserRel(UserRead):
    recordings: list[RecordingRead]

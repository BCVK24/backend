from fastapi import APIRouter, Form, Depends
from ..users.router import oauth2_scheme
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.dependencies import get_session
from ..tags.models import Tag
from ..users.router import get_user_id

from ..recordings.models import Recording
from ..recordings.router import ClientS3


router = APIRouter(prefix='/model', tags=['model'])


@router.post('/')
async def model_get_tags(recording_id: int = Form(), token: str = Depends(oauth2_scheme),
                         session: AsyncSession = Depends(get_session)):
    user_id = get_user_id(token)

    recording = await session.scalar(Recording.get_by_id(recording_id))
    recording_bytes = ClientS3.get_file(recording.url)

    tag_list = []
    # GET TAG LIST FROM MODEL

    # GET TAG LIST FROM MODEL
    return tag_list

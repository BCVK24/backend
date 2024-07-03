# API routes
from fastapi import APIRouter, Form, UploadFile, File


# ROUTER INIT
router = APIRouter()

# SEND FILE TO S3
async def SendToS3(SendFile: bytes):
    return '...'

# GET USER ID
async def GetUserId(Token: str):
    return 0

# GET FILE FROM S3
async def GetFileUrlFromS3(FileId: int, UserId: int):
    return "..."

# SOUND FILTRATION
async def SoundFiltration(FileUrl: str):
    return 0

# GET FILE
@router.get('/RecordingFile')
async def GetFile(VkToken: str = Form(), FileId: int = Form()):
    url = GetFileUrlFromS3(FileId, await GetUserId(VkToken))
    return url

# POST FILE
@router.post('/RecordingFile')
async def PostFile(AudioFile: UploadFile = File(), VkToken: str = Form()):
    url = await SendToS3(await AudioFile.read())
    UId = await GetUserId(VkToken)
    return 0

# CHANGE FILE
@router.put('/RecordingFile')
async def PutFile(VkToken: str = Form(), FileId: int = Form()):
    FileBytes = SoundFiltration(await GetFileUrlFromS3(FileId, await GetUserId(VkToken)))
    return 0
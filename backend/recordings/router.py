# API routes
from fastapi import APIRouter, Form, UploadFile, File

# ROUTER INIT
router = APIRouter()

# GET FILE
@router.get('/RecordingFile')
async def GetFile(VkToken: str = Form(), FileId: int = Form()):
    return 0

# POST FILE
@router.post('/RecordingFile')
async def PostFile(File: UploadFile = File(), VkToken: str = Form()):
    Write = open(File.filename, 'wb')
    Write.write(await File.read())
    Write.close()
    return 0

# CHANGE FILE
@router.put('/RecordingFile')
async def PutFile(VkToken: str = Form(), FileId: int = Form()):
    return 0
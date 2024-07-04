from fastapi import FastAPI
from .recordings.router import router as recording_router
from .users.router import router as user_router
from .results.router import router as result_router


app = FastAPI()


app.include_router(recording_router)
app.include_router(result_router)
app.include_router(user_router)
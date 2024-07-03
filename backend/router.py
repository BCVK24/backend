# MAIN ROUTER
from fastapi import FastAPI
from .recordings.router import router as RecordingRoiter

# INIT FASTAPI
app = FastAPI()

# INIT ROUTERS
app.include_router(RecordingRoiter)
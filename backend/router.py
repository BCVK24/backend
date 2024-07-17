from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .recordings.router import router as recording_router
from .users.router import router as user_router
from .results.router import router as result_router
from .tags.router import router as tag_router
from .worker.router import router as broker_router
from .config import settings


app = FastAPI(lifespan=broker_router.lifespan_context)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
#    allow_origin_regex=rf"https://{settings.HOST_ID}-.*\.wormhole\.vk-apps\.com/",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(broker_router)
app.include_router(recording_router)
app.include_router(result_router)
app.include_router(user_router)
app.include_router(tag_router)

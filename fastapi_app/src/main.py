from fastapi import FastAPI

from fastapi_app.src.router import router

app = FastAPI()
app.include_router(router)

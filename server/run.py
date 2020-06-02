import fastapi
from services import router

app = fastapi.FastAPI()
app.include_router(router)

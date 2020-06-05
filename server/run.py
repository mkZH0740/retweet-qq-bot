import fastapi
from services import router

app = fastapi.FastAPI(debug=True)
app.include_router(router)

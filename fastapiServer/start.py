from fastapi import FastAPI
import services.screenshot.service as screenshot_service
import services.database.service as database_service
import services.addtranslation.service as add_transaltion_service


app = FastAPI(debug=True)
app.include_router(screenshot_service.router, tags=['screenshot'])
app.include_router(database_service.router, tags=['database'])
app.include_router(add_transaltion_service.router, tags=['add_translation'])
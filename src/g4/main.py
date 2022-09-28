"""This is our main entry point"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from g4.mongo import Mongo
from g4.config import Settings

# from .routers import router as g3_router
# from .config import settings

# define the app which is the entry point for uvicorn... `uvicorn g4.app:app --reload --port 8000`
app = FastAPI(
    title="G4: Generalized Germline Gene Gateway",
    description="The germline gene gateway api hosts validated immunoglobulin gene segment data",
    version="0.0.1",
    openapi_url="/api/v1",
)


@app.on_event("startup")  # type: ignore
async def startup_db_client() -> None:
    """Connect to the database when API starts"""
    settings = Settings()

    # hold the mongo client, database, and collection in state variable
    app.state.mongo = Mongo(use_async=True, settings=settings)
    app.state.client = app.state.mongo.get_client()
    app.state.database = app.state.mongo.get_database()
    app.state.collection = app.state.mongo.get_collection()


@app.on_event("shutdown")  # type: ignore
async def shutdown_db_client() -> None:
    app.state.client.close()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "G4 is working"}


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return PlainTextResponse(str(exc), status_code=422)


# app.include_router(g3_router, tags=["G3"], prefix="/api/v1")

from fastapi import FastAPI

from api.routers import tasks

app = FastAPI(
    title="vaja API",
    description="Voice AI Assistant — task management API",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok"}


app.include_router(tasks.router)
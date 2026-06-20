from fastapi import FastAPI

import api.modules.tasks  # noqa: F401
from api.core import router as users_router
from api.modules import REGISTRY

app = FastAPI(
    title="vaja API",
    description="Voice AI Assistant",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok"}


app.include_router(users_router.router)

for module in REGISTRY:
    app.include_router(module.router)

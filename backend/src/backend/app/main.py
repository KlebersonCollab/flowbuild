from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.components.builtins import register_all_builtins


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup: ensure all builtin components are registered
    register_all_builtins()
    yield
    # Shutdown logic if needed


# Ensure builtins are populated at startup
register_all_builtins()

app = FastAPI(
    title="FlowBuild Automation Engine",
    description="Decoupled workflow builder and async execution runtime",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for local Vue 3 development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def main():
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

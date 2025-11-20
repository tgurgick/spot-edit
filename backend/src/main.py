"""FastAPI application setup for Spot Edit."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .api.routes import router
from .api.middleware import error_handling_middleware, logging_middleware


# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print("Starting Spot Edit API...")
    print(f"Storage directory: {os.path.abspath('storage')}")

    yield

    # Shutdown
    print("Shutting down Spot Edit API...")


# Create FastAPI application
app = FastAPI(
    title="Spot Edit API",
    description="AI-powered document editing with spot-targeting capabilities",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8080",  # Alternative frontend port
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handling_middleware)

# Include API routes
app.include_router(router, prefix="/api")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "spot-edit-api",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Spot Edit API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

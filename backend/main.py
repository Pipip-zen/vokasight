from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.database import init_sqlite_db
from backend.app.api.health import router as health_router
from backend.app.api.modules import router as modules_router
from backend.app.api.inspections import router as inspections_router

# Initialize Database
init_sqlite_db()

# Initialize FastAPI App
app = FastAPI(
    title="VokaSight Inspection Engine API",
    description="Vision-Based Automated Hardware & Soldering Defect Inspection Engine for Mobile Apps (Flutter/React Native) & Web",
    version="2.0.0"
)

# Enable CORS for Mobile Apps & Web Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router, tags=["Health"])
app.include_router(modules_router, prefix="/api/v1", tags=["Practicum Modules"])
app.include_router(inspections_router, prefix="/api/v1", tags=["Hardware Inspection"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

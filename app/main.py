from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from .astrology import get_planet_positions
from .scheduler import create_scheduler
from app.api.routes import device_router
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function controls app startup and shutdown.
    """
    scheduler = create_scheduler()
    scheduler.start()
    print("✅ Scheduler started")

    try:
        yield
    finally:
        scheduler.shutdown()
        print("🛑 Scheduler stopped")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

app = FastAPI(
    title="Astrology API",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    return {"message": "Hello"}

app.include_router(device_router)

@app.get("/astro")
def astro(
    year: int = Query(...),
    month: int = Query(...),
    day: int = Query(...),
    hour: float = Query(..., description="Decimal hour, e.g., 8.49"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        data = get_planet_positions(year, month, day, hour, lat, lon)
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

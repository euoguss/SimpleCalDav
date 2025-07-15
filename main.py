from fastapi import FastAPI
from src.api.v1.endpoints import calendar

app = FastAPI()

app.include_router(calendar.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

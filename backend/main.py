from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import categories, devices, habits, stats, tasks

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DashDone API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router)
app.include_router(tasks.router)
app.include_router(categories.router)
app.include_router(habits.router)
app.include_router(stats.router)


@app.get("/health")
def health():
    return {"status": "ok"}

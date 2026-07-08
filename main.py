from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dash-z6b655.example.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_headers(request: Request, call_next):

    start = time.time()

    response = await call_next(request)

    process_time = time.time() - start

    response.headers["X-Request-ID"] = str(uuid.uuid4())

    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response

@app.get("/stats")
def stats(values: str):
    numbers = [int(x) for x in values.split(",")]
    count = len(numbers)
    total = sum(numbers)
    minimum = min(numbers)
    maximum = max(numbers)
    mean = total / count
    return {
    "email": "24f3002972@ds.study.iitn.ac.in",
    "count": count,
    "sum": total,
    "min": minimum,
    "max": maximum,
    "mean": mean
    }

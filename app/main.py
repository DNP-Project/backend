from fastapi import FastAPI, Request
import uvicorn

from app.router import router as rpc_router

import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
    force=True,
)

file_handler = RotatingFileHandler(
    "app.log", maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
)
logging.getLogger().addHandler(file_handler)

app = FastAPI(title="Phonebook JSON‑RPC Service")

app.include_router(rpc_router, prefix="/rpc")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.getLogger("http").info("HTTP %s %s", request.method, request.url.path)
    response = await call_next(request)
    logging.getLogger("http").info("HTTP %s -> %s", request.method, response.status_code)
    return response


# app/main.py
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=5000, reload=True)  # pragma: no cover


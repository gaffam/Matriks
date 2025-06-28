"""Simple FastAPI server exposing the LLM as an HTTP endpoint."""

from fastapi import FastAPI, HTTPException, Header, UploadFile, File, WebSocket
from pydantic import BaseModel
import os
import asyncio
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram

from ask_llm import LLMClient
from config import load_config
from fastapi.openapi.utils import get_openapi
from jose import JWTError, jwt

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[os.getenv("RATE_LIMIT", "10/minute")],
    storage_uri="memory://",
)
middleware = [Middleware(SlowAPIMiddleware, limiter=limiter)]
app = FastAPI(title="ProAIforma API", version="2.0", middleware=middleware)
Instrumentator().instrument(app).expose(app)

# Prometheus custom counter and histogram
REQUEST_COUNT = Counter("api_requests", "Total API requests", ["endpoint"])
LLM_RESPONSE_TIME = Histogram("llm_response_seconds", "LLM response time")

# Default model path can be overridden when starting the server
MODEL_PATH = "models/finetuned-mistral.gguf"
llm_client: LLMClient | None = None
API_TOKEN = os.environ.get("API_TOKEN")
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable not set")
CFG = load_config()


def verify_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return bool(payload)
    except JWTError:
        return False


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ProAIforma API",
        version="2.0",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://example.com/logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


class Query(BaseModel):
    prompt: str


@app.on_event("startup")
def _load_model() -> None:
    global llm_client
    llm_client = LLMClient(MODEL_PATH)


@app.post("/ask")
async def ask(query: Query, authorization: str | None = Header(default=None), x_api_key: str | None = Header(default=None)) -> dict[str, str]:
    REQUEST_COUNT.labels(endpoint="ask").inc()
    if API_TOKEN and x_api_key != API_TOKEN and authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    token_parts = authorization.split() if authorization else []
    token = token_parts[1] if len(token_parts) == 2 else ""
    if authorization and not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    assert llm_client is not None
    with LLM_RESPONSE_TIME.time():
        answer = await asyncio.to_thread(llm_client.ask, query.prompt)
    return {"answer": answer}


@app.post("/bulk_ask")
async def bulk_ask(queries: list[Query], authorization: str | None = Header(default=None), x_api_key: str | None = Header(default=None)) -> list[str]:
    REQUEST_COUNT.labels(endpoint="bulk_ask").inc()
    if API_TOKEN and x_api_key != API_TOKEN and authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    token_parts = authorization.split() if authorization else []
    token = token_parts[1] if len(token_parts) == 2 else ""
    if authorization and not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    assert llm_client is not None
    results = []
    for q in queries:
        with LLM_RESPONSE_TIME.time():
            results.append(await asyncio.to_thread(llm_client.ask, q.prompt))
    return results


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), lang: str | None = None) -> dict[str, str]:
    from speech_client import transcribe

    with open("/tmp/upload.wav", "wb") as fh:
        fh.write(await file.read())
    text = await asyncio.to_thread(transcribe, "/tmp/upload.wav", lang=lang)
    return {"text": text}


@app.post("/speak")
async def speak_text(query: Query) -> None:
    from voice_response import speak

    await asyncio.to_thread(speak, query.prompt, lang=CFG.get("language", "tr"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    assert llm_client is not None
    while True:
        data = await websocket.receive_text()
        REQUEST_COUNT.labels(endpoint="ws").inc()
        response = await asyncio.to_thread(llm_client.ask, data)
        await websocket.send_text(response)

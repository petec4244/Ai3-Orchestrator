from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from ai3core.engine import Ai3Core
from ai3core.settings import CORS_ORIGINS


app = FastAPI(title="Ai3 Orchestrator API v2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    prompt: str


@app.post("/run")
async def run_non_streaming(request: RunRequest):
    """Non-streaming orchestration endpoint."""
    engine = Ai3Core()
    result = await engine.run(request.prompt, stream=False)
    return result


@app.post("/stream/run")
async def run_streaming(request: RunRequest):
    """Server-Sent Events streaming endpoint."""
    engine = Ai3Core()

    async def event_generator():
        events = []

        async def collect_event(event: dict):
            events.append(event)

        # Run orchestration with event collection
        task = asyncio.create_task(engine.run(request.prompt, stream=True))

        # Mock event stream for demonstration
        # In production, engine.run would yield events via callback
        await asyncio.sleep(0.1)

        # Emit sample events
        sample_events = [
            {"type": "plan", "status": "started"},
            {"type": "plan", "status": "completed", "task_count": 3},
            {"type": "task_start", "task_id": "t1", "description": "Generate introduction"},
            {"type": "decision", "task_id": "t1", "provider": "anthropic-claude"},
            {"type": "task_artifact", "task_id": "t1", "artifact": {"content": "Sample intro"}},
            {"type": "task_verified", "task_id": "t1", "verification": {"status": "passed"}},
            {"type": "assemble_start"},
            {"type": "final", "output": "Final assembled output"},
            {"type": "stats", "stats": {"task_count": 3, "total_cost": 0.05}}
        ]

        for event in sample_events:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.2)

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.1"}

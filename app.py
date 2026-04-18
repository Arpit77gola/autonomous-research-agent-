import os
import asyncio
import json
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Autonomous Research Agent")

# ── request/response models ──────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str
    email: str = ""


class EmailRequest(BaseModel):
    query: str
    report: str
    email: str


# ── SSE streaming research ────────────────────────────────────────────────────

async def run_research_stream(query: str) -> AsyncGenerator[str, None]:
    """Run the research pipeline and stream log lines + final report as SSE."""
    import sys
    import io
    from graph.state import ResearchState
    from graph.graph import research_graph

    log_lines = []

    # Capture stdout so we can stream prints to the browser
    class StreamCapture(io.TextIOBase):
        def __init__(self, queue: asyncio.Queue):
            self.queue = queue
        def write(self, text):
            if text.strip():
                self.queue.put_nowait(text.strip())
            return len(text)
        def flush(self):
            pass

    queue: asyncio.Queue = asyncio.Queue()
    capture = StreamCapture(queue)
    old_stdout = sys.stdout
    sys.stdout = capture

    loop = asyncio.get_event_loop()

    async def _invoke():
        initial_state = ResearchState(query=query)
        return await loop.run_in_executor(
            None,
            lambda: research_graph.invoke(initial_state, {"recursion_limit": 50}),
        )

    task = asyncio.create_task(_invoke())

    while not task.done() or not queue.empty():
        try:
            line = queue.get_nowait()
            yield f"data: {json.dumps({'type': 'log', 'text': line})}\n\n"
        except asyncio.QueueEmpty:
            await asyncio.sleep(0.05)

    sys.stdout = old_stdout

    try:
        result = await task
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'text': str(e)})}\n\n"
        return

    report = result.get("final_report", "")
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in query[:50])
    pdf_path  = os.path.join(os.getenv("OUTPUT_DIR", "output"), f"{safe_name}.pdf")

    yield f"data: {json.dumps({'type': 'report', 'text': report, 'pdf': safe_name})}\n\n"
    yield "data: [DONE]\n\n"


# ── routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("ui/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/research")
async def research(query: str):
    return StreamingResponse(
        run_research_stream(query),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/download/{safe_name}")
async def download_pdf(safe_name: str):
    pdf_path = os.path.join(os.getenv("OUTPUT_DIR", "output"), f"{safe_name}.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf",
                            filename=f"{safe_name}.pdf")
    return {"error": "PDF not found"}


@app.post("/send-email")
async def send_email(req: EmailRequest):
    if not req.email:
        return {"ok": False, "msg": "No email provided"}
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in req.query[:50])
    pdf_path  = os.path.join(os.getenv("OUTPUT_DIR", "output"), f"{safe_name}.pdf")
    from utils.email_sender import send_report_email
    ok = send_report_email(
        to_email  = req.email,
        subject   = f"Research Report: {req.query}",
        report_md = req.report,
        pdf_path  = pdf_path if os.path.exists(pdf_path) else None,
    )
    return {"ok": ok, "msg": "Email sent!" if ok else "Failed — check .env credentials"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
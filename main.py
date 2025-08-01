from sse_starlette import EventSourceResponse
from fasthtml.common import *
import asyncio
from datetime import datetime

# Application
hdrs = [
    Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js")
]
app, rt = fast_app(hdrs=hdrs, htmx=False, surreal=False, live=False)

@app.get("/")
def home():
    return (
        Title("fastHTML w/ sse_starlette"),
        Main(cls="container")(
            Header(H1("FastHTML + Datastar + sse-starlette")),
            Main(
                H2("SSE Examples"),
                Article(
                    P("SSE: patch elements"),
                    Button(data_on_click="@get('/stream')")("SSE Stream demo"),
                    Span(id="stream")("Initial Content"),
                ),
                Article(
                    Header(
                        Nav(
                            P("SSE: patch signals"),
                            Span("FPS: ", Kbd(data_text="$fps")("0"))
                        )
                    ),
                    Span(Kbd(data_text="$currentTime")("Loading time...")),
                    Footer(
                        Button(data_on_click="@get('/time-signals')")("Live Time Signals"),
                        Button(data_on_click="window.location.reload()")("Stop Clock"),
                    )
                )
            )
        )
    )


@app.get("/stream")
async def stream_updates(request):
    async def event_generator():
        for i in range(10):
            content = Span(id='stream')(f"Update {i}")
            yield {
                "event": "datastar-patch-elements",
                "data": f"elements {to_xml(content)}"
            }
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())

@app.get("/time-signals")
async def time_signals(request):
    async def event_generator():
        last_time, frame_count, current_fps = datetime.now(), 0, 0.0
        while True:
            now = datetime.now()
            frame_count += 1
            elapsed = (now - last_time).total_seconds()
            if elapsed >= 1.0: current_fps, last_time, frame_count = frame_count / elapsed, now, 0
            yield {
                "event": "datastar-patch-signals",
                "data": f"signals {{'currentTime': '{now:%I:%M:%S.%f %p}', 'fps': '{current_fps:.1f}'}}"
            }
            await asyncio.sleep(0.01)
    return EventSourceResponse(event_generator())

serve()

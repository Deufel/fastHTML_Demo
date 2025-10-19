from sse_starlette import EventSourceResponse
from fasthtml.common import *
import asyncio
from datetime import datetime
import uvicorn

# Application
hdrs = [
    Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js")
]
app, rt = fast_app(hdrs=hdrs, htmx=False, surreal=False, live=False)

@app.get("/")
def home():
    return (
        Title("FastHTML SSE Rate Limit Test"),
        Main(cls="container")(
            Header(H1("🚀 FastHTML + SSE Rate Limit Tester")),
            Main(
                H2("Load Test Controls"),
                Article(cls="card")(
                    Label("Signals/Second:"),
                    Input(type="range", id="rps", min="1", max="1000", value="100", 
                          data_on_change="@patch('/set-rps', {{rps: $rps}} )"),
                    Span(id="rps-display")("100"),
                    Button(data_on_click="@get('/time-signals')")("🔥 START TEST"),
                    Button(data_on_click="window.location.reload()")("Stop"),
                ),
                Article(cls="card")(
                    H3("📊 Live Stats"),
                    Div(id="stats")("FPS: 0 | Latency: 0ms"),
                ),
                Article(cls="card")(
                    H3("🏃‍♂️ Run wrk2 Test"),
                    Pre(cls="code")(
                        Kbd("wrk2 -t12 -c200 -d30s -R1000 'http://localhost:5001/'"),
                        Br(), 
                        Small("Tests 1000 RPS for 30s with 200 connections")
                    ),
                    Button(id="run-test", onclick="runWrkTest()")("Run Benchmark"),
                )
            )
        ),
        Script("""
            async function runWrkTest() {
                const res = await fetch('/wrk-results');
                const stats = await res.json();
                document.getElementById('stats').innerHTML = 
                    `RPS: ${stats.rps} | Latency: ${stats.p99}ms | Errors: ${stats.errors}%`;
            }
        """)
    )

# GLOBAL RATE LIMITER
current_rps = 100  # Signals per second
semaphore = asyncio.Semaphore(1000)  # Prevent overload

@app.post("/set-rps")
def set_rps(rps: int):
    global current_rps
    current_rps = int(rps)
    return Div(f"Set to {rps} signals/sec")

@app.get("/time-signals")
async def time_signals(request):
    async def event_generator():
        global current_rps
        last_time, frame_count, current_fps = datetime.now(), 0, 0.0
        interval = 1.0 / current_rps  # Dynamic sleep based on target RPS
        
        while True:
            async with semaphore:  # Rate limiting
                now = datetime.now()
                frame_count += 1
                elapsed = (now - last_time).total_seconds()
                if elapsed >= 1.0: 
                    current_fps, last_time, frame_count = frame_count / elapsed, now, 0
                
                # Yield signal
                yield {
                    "event": "datastar-patch-signals",
                    "data": f"signals {{'currentTime': '{now:%I:%M:%S.%f %p}', 'fps': '{current_fps:.1f}', 'rps': {current_rps}}}"
                }
                await asyncio.sleep(interval)  # Precise timing
    
    return EventSourceResponse(event_generator())

# WRK2 BENCHMARK ENDPOINT (for automated testing)
@app.get("/wrk-results")
async def wrk_results():
    # Simulate 1000 RPS test results (replace with real metrics)
    return {
        "rps": 850,  # Max achieved
        "latency_avg": 12,
        "latency_p99": 45,
        "errors": 0.2,
        "connections": 200
    }

if __name__ == "__main__":
    print("🚀 Starting SSE Rate Test Server...")
    print("📋 Install wrk2: brew install wrk2")
    print("🏃‍♂️ Test: wrk2 -t12 -c200 -d30s -R1000 http://localhost:5001/")
    uvicorn.run(app, host="0.0.0.0", port=5001)

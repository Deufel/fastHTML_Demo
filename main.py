from sse_starlette import EventSourceResponse
from fasthtml.common import *
import asyncio
from datetime import datetime
import uvicorn
import time
from collections import deque

# Application
hdrs = [
    Script(type="module", src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js")
]
app, rt = fast_app(hdrs=hdrs, htmx=False, surreal=False, live=False)

# Latency tracking for benchmark
latencies = deque(maxlen=1000)

@app.get("/")
def home():
    return (
        Title("FastHTML SSE Browser Benchmark"),
        Main(cls="container")(
            Header(H1("🚀 FastHTML SSE - BROWSER BENCHMARK")),
            Main(
                H2("🔥 1-CLICK LOAD TEST (No Terminal Needed!)"),
                Article(cls="card")(
                    Label("Test Users (Concurrent Streams):"),
                    Input(type="range", id="users", min="10", max="500", value="100"),
                    Span(id="users-display")("100"),
                    Br(),
                    Button(id="run-benchmark", cls="btn-primary", onclick="runBenchmark()")("🚀 RUN FULL BENCHMARK"),
                    Button(data_on_click="@get('/time-signals')")("👁️ Preview Single Stream"),
                    Button(data_on_click="window.location.reload()")("Stop All"),
                ),
                Article(cls="card")(
                    H3("📊 LIVE RESULTS (Updates Every Second)"),
                    Div(id="results")(
                        P("Status: Ready"),
                        P(id="rps-display")("Signals/Sec: 0"),
                        P(id="latency-display")("Avg Latency: 0ms"),
                        P(id="concurrent-display")("Active Streams: 0"),
                        P(id="cpu-display")("CPU Load: --"),
                        Progress(id="progress", value="0", max="100")
                    )
                ),
                Article(cls="card")(
                    H3("🏆 BENCHMARK SUMMARY"),
                    Div(id="summary")("Click 'RUN FULL BENCHMARK' to start!")
                )
            )
        ),
        Script("""
            let benchmarkActive = false;
            let totalSignals = 0;
            let startTime = 0;
            let streams = [];

            async function runBenchmark() {
                if (benchmarkActive) return;
                benchmarkActive = true;
                
                const users = parseInt(document.getElementById('users').value);
                document.getElementById('run-benchmark').innerHTML = '⏳ TESTING...';
                document.getElementById('results').innerHTML = '<p>Status: Launching ' + users + ' streams...</p>';
                
                startTime = Date.now();
                totalSignals = 0;
                
                // Launch concurrent SSE streams
                for (let i = 0; i < users; i++) {
                    const evtSource = new EventSource('/time-signals');
                    streams.push(evtSource);
                    
                    evtSource.onmessage = (event) => {
                        totalSignals++;
                        const latency = Date.now() - startTime;
                        fetch('/log-latency?lat=' + (Date.now() - JSON.parse(event.data).timestamp));
                    };
                    
                    evtSource.onerror = () => {
                        streams = streams.filter(s => s.readyState === EventSource.OPEN);
                        updateStats();
                    };
                }
                
                // Run for 30 seconds
                setTimeout(() => {
                    stopBenchmark();
                    showSummary(users);
                }, 30000);
                
                // Update stats every second
                const interval = setInterval(updateStats, 1000);
            }
            
            function updateStats() {
                if (!benchmarkActive) return;
                const elapsed = (Date.now() - startTime) / 1000;
                const rps = totalSignals / elapsed;
                const concurrent = streams.filter(s => s.readyState === EventSource.OPEN).length;
                
                document.getElementById('rps-display').innerHTML = `Signals/Sec: ${rps.toFixed(0)}`;
                document.getElementById('concurrent-display').innerHTML = `Active Streams: ${concurrent}`;
                document.getElementById('progress').value = Math.min((elapsed / 30) * 100, 100);
                
                fetch('/get-stats').then(r => r.json()).then(stats => {
                    document.getElementById('latency-display').innerHTML = `Avg Latency: ${stats.avg_latency}ms`;
                    document.getElementById('cpu-display').innerHTML = `Server CPU: ${stats.cpu_load}%`;
                });
            }
            
            function stopBenchmark() {
                benchmarkActive = false;
                streams.forEach(s => s.close());
                streams = [];
            }
            
            async function showSummary(users) {
                const elapsed = 30;
                const rps = totalSignals / elapsed;
                const score = rps > 500 ? '🏆 EXCELLENT' : rps > 300 ? '👍 GOOD' : '⚠️ NEEDS TUNING';
                
                document.getElementById('summary').innerHTML = `
                    <h4>FINAL RESULTS (${users} users, 30s test)</h4>
                    <p><strong>Max Signals/Sec:</strong> ${rps.toFixed(0)}</p>
                    <p><strong>Total Signals:</strong> ${totalSignals}</p>
                    <p><strong>Score:</strong> ${score}</p>
                    <p><em>${rps > 500 ? 'Ready for production trading!' : 'Consider upgrading VPS CPU/RAM'}</em></p>
                `;
                document.getElementById('run-benchmark').innerHTML = '✅ DONE! Run Again';
            }
        """)
    )

# GLOBAL RATE LIMITER + STATS
current_rps = 100
semaphore = asyncio.Semaphore(1000)
signal_count = 0
start_time = time.time()

@app.post("/set-rps")
def set_rps(rps: int):
    global current_rps
    current_rps = int(rps)
    return Div(f"Set to {rps} signals/sec")

@app.get("/time-signals")
async def time_signals(request):
    async def event_generator():
        global current_rps, signal_count
        interval = 1.0 / current_rps if current_rps > 0 else 0.01
        
        while True:
            async with semaphore:
                now = datetime.now()
                signal_count += 1
                yield {
                    "event": "datastar-patch-signals",
                    "data": f"signals {{'currentTime': '{now:%I:%M:%S.%f %p}', 'fps': '{current_rps}', 'timestamp': {int(time.time() * 1000)}}}"
                }
                await asyncio.sleep(interval)
    
    return EventSourceResponse(event_generator())

@app.get("/log-latency")
async def log_latency(lat: float):
    latencies.append(lat)
    return {"ok": True}

@app.get("/get-stats")
async def get_stats():
    global signal_count, start_time
    elapsed = time.time() - start_time
    rps = signal_count / elapsed if elapsed > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    # Simulate CPU load (replace with real psutil if needed)
    cpu_load = min(rps / 10, 100)
    
    return {
        "avg_latency": avg_latency,
        "cpu_load": cpu_load,
        "total_signals": signal_count,
        "rps": rps
    }

if __name__ == "__main__":
    print("🚀 BROWSER BENCHMARK READY!")
    print("📱 Visit your Coolify URL → Click 'RUN FULL BENCHMARK'")
    uvicorn.run(app, host="0.0.0.0", port=8000)

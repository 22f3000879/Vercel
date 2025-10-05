from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import statistics
import json

app = FastAPI()

# Enable CORS for all origins (important for Vercel tests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/")
async def telemetry(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 0)

    # Load telemetry data (this file should be in your repo root or api folder)
    with open("telemetry.json", "r") as f:
        telemetry = json.load(f)

    response = {}
    for region in regions:
        entries = telemetry.get(region, [])
        if not entries:
            continue

        latencies = [e["latency_ms"] for e in entries]
        uptimes = [e["uptime"] for e in entries]

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = statistics.quantiles(latencies, n=100)[94]  # 95th percentile
        avg_uptime = sum(uptimes) / len(uptimes)
        breaches = sum(1 for l in latencies if l > threshold)

        response[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return response

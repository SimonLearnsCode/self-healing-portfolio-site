from flask import Flask, render_template_string, jsonify
from prometheus_client import generate_latest, Counter, Gauge, REGISTRY
import psutil
import time
import os
import threading

app = Flask(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter('portfolio_requests_total', 'Total Web Visits')
CPU_GAUGE = Gauge('portfolio_cpu_usage_percent', 'Current CPU Usage Percent')
MEMORY_GAUGE = Gauge('portfolio_memory_usage_percent', 'Current Memory Usage Percent')

# Chaos states
cpu_stress_active = False
traffic_stress_active = False

def stress_cpu():
    global cpu_stress_active
    timeout = time.time() + 45  # Keep spike alive for 45 seconds
    while time.time() < timeout and cpu_stress_active:
        _ = 10000 * 10000

def stress_traffic():
    global traffic_stress_active
    timeout = time.time() + 45
    while time.time() < timeout and traffic_stress_active:
        REQUEST_COUNT.inc(15)  # Increment visits aggressively
        time.sleep(0.1)        # 150 visits per second simulation

@app.route('/')
def home():
    REQUEST_COUNT.inc()
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SRE & DevOps Cloud Cockpit</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans antialiased selection:bg-indigo-500 selection:text-white">
        
        <div class="bg-gradient-to-r from-indigo-900 via-slate-900 to-blue-900 border-b border-slate-800 px-6 py-4 shadow-2xl">
            <div class="max-w-5xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
                <div>
                    <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">Simon Learns Code</h1>
                    <p class="text-xs font-mono text-slate-400 mt-1">🚀 Systems Administrator & DevOps Architect</p>
                </div>
                <div class="flex items-center gap-3 bg-slate-900/80 px-4 py-2 rounded-lg border border-slate-700/50">
                    <span class="relative flex h-3 w-3">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                    </span>
                    <span class="text-xs font-mono font-bold tracking-wider text-emerald-400 uppercase">System: Operational</span>
                </div>
            </div>
        </div>

        <main class="max-w-5xl mx-auto px-4 py-12 space-y-12">
            
            <div class="bg-slate-900 rounded-2xl border border-slate-800 shadow-xl overflow-hidden">
                <div class="border-b border-slate-800 bg-slate-900/50 px-6 py-4 flex items-center justify-between">
                    <h2 class="text-lg font-bold flex items-center gap-2 text-indigo-400">
                        <i class="fa-solid var(--fa-terminal) text-sm"></i> 🛠️ Live Site Reliability Engineering (SRE) Sandbox
                    </h2>
                    <span class="text-xs font-mono text-slate-500 bg-slate-950 px-2 py-1 rounded">Target: Production-Node-01</span>
                </div>
                
                <div class="p-6 space-y-6">
                    <p class="text-slate-300 text-sm max-w-3xl leading-relaxed">
                        Welcome, Recruiter! Instead of reading a static resume, you have access to my infrastructure's control plane. Use the triggers below to launch synthetic anomalies and watch how my automated monitoring matrix auto-heals this node.
                    </p>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 hover:border-red-500/30 transition-all duration-300 flex flex-col justify-between">
                            <div>
                                <div class="text-red-400 text-xl mb-2"><i class="fa-solid fa-microchip"></i></div>
                                <h3 class="font-bold text-slate-200">Inject CPU Anomaly</h3>
                                <p class="text-xs text-slate-400 mt-1 mb-4">Forces calculation thread blocks to drive kernel metrics over 80% utilization limits, tripping Prometheus alerting thresholds.</p>
                            </div>
                            <button onclick="triggerChaos('cpu')" id="cpuBtn" class="w-full bg-red-950/40 hover:bg-red-600 border border-red-800 hover:border-red-500 text-red-200 hover:text-white font-mono font-medium py-2.5 px-4 rounded-lg transition-all duration-300 shadow-lg shadow-red-950/20">
                                Launch Stress Matrix
                            </button>
                        </div>

                        <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 hover:border-cyan-500/30 transition-all duration-300 flex flex-col justify-between">
                            <div>
                                <div class="text-cyan-400 text-xl mb-2"><i class="fa-solid fa-chart-line"></i></div>
                                <h3 class="font-bold text-slate-200">Simulate DDoS Traffic Surge</h3>
                                <p class="text-xs text-slate-400 mt-1 mb-4">Mocks a distributed flood of concurrent visitors, driving telemetry count parameters upwards at 150 requests/sec.</p>
                            </div>
                            <button onclick="triggerChaos('traffic')" id="trafficBtn" class="w-full bg-cyan-950/40 hover:bg-cyan-600 border border-cyan-800 hover:border-cyan-500 text-cyan-200 hover:text-white font-mono font-medium py-2.5 px-4 rounded-lg transition-all duration-300 shadow-lg shadow-cyan-950/20">
                                Simulate 15k Reqs/Min
                            </button>
                        </div>
                    </div>

                    <div id="statusConsole" class="hidden bg-slate-950 border border-amber-500/20 rounded-xl p-5 font-mono text-xs space-y-2 text-amber-400 shadow-inner">
                        <div class="flex items-center gap-2 text-sm font-bold text-amber-300">
                            <i class="fa-solid fa-triangle-exclamation animate-pulse"></i> SIMULATION INJECTED & ACTIVE
                        </div>
                        <hr class="border-slate-800 my-2">
                        <p class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-blue-500"></span> [TELEMETRY] Scrape metrics route exposed at <a href="/metrics" target="_blank" class="underline text-blue-400 hover:text-blue-300">/metrics</a></p>
                        <p class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span> [ALERTMANAGER] Evaluating metric thresholds across instances...</p>
                        <p id="healLog" class="text-slate-500 transition-all duration-500">[SYSTEM] Listening for automated GitHub recovery dispatch action...</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-slate-900 p-6 rounded-xl border border-slate-800 space-y-3 shadow-lg">
                    <h3 class="text-base font-bold text-indigo-400 flex items-center gap-2"><i class="fa-solid fa-layer-group"></i> Container Stack Details</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">Built using a lightweight multi-stage Docker file on top of Python-Alpine distributions. Exposes native counters explicitly mapped for Prometheus collectors.</p>
                </div>
                <div class="bg-slate-900 p-6 rounded-xl border border-slate-800 space-y-3 shadow-lg">
                    <h3 class="text-base font-bold text-indigo-400 flex items-center gap-2"><i class="fa-solid fa-heart-pulse"></i> Auto-Recovery Infrastructure</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">UptimeRobot hooks evaluate conditions every 5 seconds. Exceeding thresholds automatically sends a payload to GitHub Actions API to trigger an instant application container rollout.</p>
                </div>
            </div>
        </main>

        <script>
            function triggerChaos(type) {
                const btn = type === 'cpu' ? document.getElementById('cpuBtn') : document.getElementById('trafficBtn');
                const consoleBox = document.getElementById('statusConsole');
                const healLog = document.getElementById('healLog');
                
                consoleBox.classList.remove('hidden');
                btn.disabled = true;
                btn.className = "w-full bg-slate-900 border border-slate-800 text-slate-600 font-mono font-medium py-2.5 px-4 rounded-lg cursor-not-allowed text-xs";
                btn.innerHTML = "Simulation Running...";

                fetch('/simulate-chaos/' + type, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                        setTimeout(() => {
                            healLog.classList.remove('text-slate-500');
                            healLog.classList.add('text-rose-400', 'font-bold');
                            healLog.innerHTML = "🚨 [ALERT] Threshold Breached! Action webhook sent to GitHub Core Workflow.";
                        }, 4000);
                    });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/simulate-chaos/<chaos_type>', methods=['POST'])
def simulate_chaos(chaos_type):
    global cpu_stress_active, traffic_stress_active
    
    if chaos_type == 'cpu' and not cpu_stress_active:
        cpu_stress_active = True
        threading.Thread(target=stress_cpu).start()
        return jsonify({"status": "success", "message": "CPU stress thread spawned."})
        
    elif chaos_type == 'traffic' and not traffic_stress_active:
        traffic_stress_active = True
        threading.Thread(target=stress_traffic).start()
        return jsonify({"status": "success", "message": "Synthetic request influx active."})
        
    return jsonify({"status": "ignored", "message": "Simulation already running or invalid type."})

@app.route('/metrics')
def metrics():
    CPU_GAUGE.set(psutil.cpu_percent())
    MEMORY_GAUGE.set(psutil.virtual_memory().percent)
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

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

# Simulated heavy load state
cpu_stress_active = False

def stress_cpu():
    global cpu_stress_active
    # Intense math loop to peg CPU usage high for 60 seconds
    timeout = time.time() + 60
    while time.time() < timeout and cpu_stress_active:
        _ = 10000 * 10000

@app.route('/')
def home():
    REQUEST_COUNT.inc()
    
    # HTML template embedded directly for simplicity
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DevOps Self-Healing Portfolio</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white font-sans">
        <div class="max-w-4xl mx-auto px-4 py-12">
            <header class="text-center mb-12">
                <h1 class="text-4xl font-extrabold text-indigo-400">John Doe</h1>
                <p class="text-xl text-gray-400 mt-2">DevOps & AI Systems Engineer</p>
                <div class="mt-4">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-500/10 text-green-400 ring-1 ring-inset ring-green-500/20">
                        System Status: Operational
                    </span>
                </div>
            </header>

            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-xl mb-8">
                <h2 class="text-2xl font-bold text-white mb-4">⚙️ Live Chaos Engineering Demo</h2>
                <p class="text-gray-300 mb-6">As a recruiter, you can try to break my website. Click the button below to inject a CPU spike (>80%). The monitoring layer will catch it, trigger a GitHub Action, and automatically restart/heal the container.</p>
                <div class="flex flex-wrap gap-4">
                    <button onclick="triggerCrash()" id="crashBtn" class="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg transition dynamic-btn">
                        Simulate CPU Spike (>80%)
                    </button>
                    <a href="/metrics" target="_blank" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition">
                        View Raw Prometheus Metrics
                    </a>
                </div>
                <div id="statusMessage" class="mt-4 text-yellow-400 hidden font-mono">⚠️ Chaos injected! High CPU load simulated. Watch the self-healing trigger...</div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                    <h3 class="text-xl font-bold text-indigo-300 mb-2">Core Tech Stack</h3>
                    <p class="text-gray-400">Docker, Kubernetes, ArgoCD, GitHub Actions, Prometheus, Grafana, Python.</p>
                </div>
                <div class="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                    <h3 class="text-xl font-bold text-indigo-300 mb-2">Self-Healing Logic</h3>
                    <p class="text-gray-400">Monitored by Prometheus. Alerts trip automated GitHub Action API dispatches to redeploy via webhook instantly.</p>
                </div>
            </div>
        </div>

        <script>
            function triggerCrash() {
                document.getElementById('statusMessage').classList.remove('hidden');
                document.getElementById('crashBtn').disabled = true;
                document.getElementById('crashBtn').classList.add('opacity-50', 'cursor-not-allowed');
                
                fetch('/simulate-crash', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => console.log(data));
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/simulate-crash', methods=['POST'])
def simulate_crash():
    global cpu_stress_active
    if not cpu_stress_active:
        cpu_stress_active = True
        t = threading.Thread(target=stress_cpu)
        t.start()
    return jsonify({"status": "Chaos initiated", "message": "CPU load rising..."})

@app.route('/metrics')
def metrics():
    # Update system utilization metrics dynamically on scrape
    CPU_GAUGE.set(psutil.cpu_percent())
    MEMORY_GAUGE.set(psutil.virtual_memory().percent)
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    # Render binds port to the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

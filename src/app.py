from flask import Flask, render_template_string, jsonify
from prometheus_client import generate_latest, Counter, Gauge, REGISTRY
import psutil
import time
import os
import threading

app = Flask(__name__)

# Prometheus Metrics (Our background system counters)
REQUEST_COUNT = Counter('portfolio_requests_total', 'Total Web Visits')
CPU_GAUGE = Gauge('portfolio_cpu_usage_percent', 'Current CPU Usage Percent')
MEMORY_GAUGE = Gauge('portfolio_memory_usage_percent', 'Current Memory Usage Percent')

# Simple tracking flags for our background tasks
cpu_stress_active = False
traffic_stress_active = False


def stress_cpu():
    timeout = time.time() + 45  # Run for 45 seconds max
    while time.time() < timeout and cpu_stress_active:
        _ = 10000 * 10000  # Make the computer calculate numbers rapidly


def stress_traffic():
    timeout = time.time() + 45
    while time.time() < timeout and traffic_traffic_active:
        REQUEST_COUNT.inc(15)  # Simulate 15 hits at once
        time.sleep(0.1)        # Pause for a split second


@app.route('/')
def home():
    REQUEST_COUNT.inc()  # Log a normal visit

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud Auto-Heal Lab</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans antialiased">
        
        <div class="max-w-4xl mx-auto pt-12 px-4 text-center">
            <span class="text-xs font-mono tracking-widest text-indigo-400 uppercase bg-indigo-950/50 px-3 py-1 rounded-full border border-indigo-800/40">
                Interactive Cloud Experiment
            </span>
            <h1 class="text-4xl font-black tracking-tight mt-3 bg-gradient-to-r from-slate-100 via-indigo-200 to-cyan-400 bg-clip-text text-transparent">
                The Self-Healing Infrastructure Lab
            </h1>
            <p class="text-sm text-slate-400 mt-2 max-w-xl mx-auto">
                Designed by Simon Motaung. A hands-on demonstration showing how modern cloud networks automatically detect faults and repair themselves without human intervention.
            </p>
        </div>

        <main class="max-w-3xl mx-auto px-4 py-8 space-y-6">
            
            <div class="bg-slate-900/60 p-5 rounded-xl border border-slate-800/80 text-xs text-slate-300 leading-relaxed space-y-2 shadow-xl">
                <p class="font-bold text-slate-200 text-sm">💡 How this experiment works (In plain terms):</p>
                <p>When software runs in production, servers can slow down or crash due to unexpected traffic floods or heavy calculations. Usually, an engineer gets woken up at 2 AM to fix it. Here, my cloud platform uses automated monitoring to watch the server's pulse. If you break it using the buttons below, the system will detect the issue and issue an automatic system restart command instantly.</p>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6">
                <div class="text-center space-y-1">
                    <h2 class="text-lg font-bold text-slate-200">Step 1: Choose Your Weapon</h2>
                    <p class="text-xs text-slate-400">Click a button below to actively inject a system fault into this live website.</p>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <button onclick="startExperiment('cpu')" id="cpuBtn" class="group relative bg-gradient-to-b from-slate-900 to-slate-950 hover:from-red-950/30 hover:to-slate-950 p-5 rounded-xl border border-slate-800 hover:border-red-500/50 text-left transition-all duration-300 shadow-lg">
                        <div class="text-red-400 text-lg group-hover:scale-110 transition-transform"><i class="fa-solid fa-microchip"></i></div>
                        <h3 class="font-bold text-slate-200 text-sm mt-2">Overload the CPU Processor</h3>
                        <p class="text-[11px] text-slate-400 mt-1">Forces the server to calculate massive mathematical formulas, pushing utilization to 100% instantly.</p>
                    </button>

                    <button onclick="startExperiment('traffic')" id="trafficBtn" class="group relative bg-gradient-to-b from-slate-900 to-slate-950 hover:from-cyan-950/30 hover:to-slate-950 p-5 rounded-xl border border-slate-800 hover:border-cyan-500/50 text-left transition-all duration-300 shadow-lg">
                        <div class="text-cyan-400 text-lg group-hover:scale-110 transition-transform"><i class="fa-solid fa-bolt"></i></div>
                        <h3 class="font-bold text-slate-200 text-sm mt-2">Simulate Fake Traffic Surge</h3>
                        <p class="text-[11px] text-slate-400 mt-1">Simulates 15,000 automated bots visiting this exact webpage at the exact same moment.</p>
                    </button>
                </div>

                <div id="trackerMap" class="hidden border-t border-slate-800/80 pt-6 space-y-4">
                    <p class="text-center text-xs font-mono tracking-wider text-amber-400 font-bold animate-pulse">
                        ⚠️ LIVE FAULT INJECTED. AUTOMATED AUTOMATION SEQUENCE INITIALIZED:
                    </p>

                    <div class="grid grid-cols-3 gap-2 font-mono text-[10px] text-center">
                        <div id="step1" class="bg-slate-950 border border-slate-800 p-3 rounded-lg text-slate-500 transition-all duration-500">
                            <div class="text-sm font-bold mb-1">01</div>
                            <span class="font-bold">FAULT DETECTED</span>
                            <p class="text-[9px] text-slate-600 mt-1">System parameters broke safety guidelines.</p>
                        </div>
                        <div id="step2" class="bg-slate-950 border border-slate-800 p-3 rounded-lg text-slate-500 transition-all duration-500">
                            <div class="text-sm font-bold mb-1">02</div>
                            <span class="font-bold">TRIGGER ALERT</span>
                            <p class="text-[9px] text-slate-600 mt-1">Monitoring tools fired recovery webhook flags.</p>
                        </div>
                        <div id="step3" class="bg-slate-950 border border-slate-800 p-3 rounded-lg text-slate-500 transition-all duration-500">
                            <div class="text-sm font-bold mb-1">03</div>
                            <span class="font-bold">SELF-HEAL COMPLETE</span>
                            <p class="text-[9px] text-slate-600 mt-1">Fresh server container deployed live.</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <script>
            function startExperiment(faultType) {
                // Show the visual stepper track map
                document.getElementById('trackerMap').classList.remove('hidden');
                
                // Disable both action triggers to keep state clean
                document.getElementById('cpuBtn').disabled = true;
                document.getElementById('trafficBtn').disabled = true;
                document.getElementById('cpuBtn').classList.add('opacity-40', 'cursor-not-allowed');
                document.getElementById('trafficBtn').classList.add('opacity-40', 'cursor-not-allowed');

                // Step 1 Lights up instantly
                const s1 = document.getElementById('step1');
                s1.className = "bg-red-950/20 border-red-500/60 p-3 rounded-lg text-red-400 transition-all duration-500 shadow-md shadow-red-900/10";

                // Send the network signal to the python app back-end
                fetch('/simulate-chaos/' + faultType, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                        
                        // Step 2 lights up 3.5 seconds later (Simulating metric evaluation time)
                        setTimeout(() => {
                            const s2 = document.getElementById('step2');
                            s2.className = "bg-amber-950/20 border-amber-500/60 p-3 rounded-lg text-amber-400 transition-all duration-500 shadow-md shadow-amber-900/10";
                        }, 3500);

                        // Step 3 lights up 7 seconds later (Simulating GitHub Actions workflow catch-up)
                        setTimeout(() => {
                            const s3 = document.getElementById('step3');
                            s3.className = "bg-emerald-950/20 border-emerald-500/60 p-3 rounded-lg text-emerald-400 transition-all duration-500 shadow-md shadow-emerald-900/10";
                        }, 7000);
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
        return jsonify({"status": "success", "message": "CPU load running."})

    elif chaos_type == 'traffic' and not traffic_stress_active:
        traffic_stress_active = True
        threading.Thread(target=stress_traffic).start()
        return jsonify({"status": "success", "message": "Traffic flood running."})

    return jsonify({"status": "ignored", "message": "Already active."})

sssds
@app.route('/metrics')
def metrics():
    CPU_GAUGE.set(psutil.cpu_percent())
    MEMORY_GAUGE.set(psutil.virtual_memory().percent)
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
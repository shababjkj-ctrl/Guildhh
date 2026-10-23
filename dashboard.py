import json, subprocess, time
from pathlib import Path
from flask import Flask, request, render_template

BASE = Path(__file__).parent
CONFIG_FILE = BASE / "dashboard_config.json"
LOG_FILE = BASE / "bot_run.log"

app = Flask(__name__, template_folder="templates")
state = {"proc": None, "started_at": None}

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {"region": "BD", "parallel": 2, "bots": 20, "guild_uid": "3105974875"}

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        cfg = request.json; save_config(cfg)
        return {"ok": True, "config": cfg}
    return {"config": load_config()}

@app.route("/api/start", methods=["POST"])
def api_start():
    p = state["proc"]
    if p and p.poll() is None:
        return {"error": "already running"}, 400
    cfg = request.json or load_config(); save_config(cfg)
    LOG_FILE.write_text("")
    log_fh = open(LOG_FILE, "a", buffering=1)
    proc = subprocess.Popen(["python3", "-u", "main.py"],
        stdin=subprocess.PIPE, stdout=log_fh, stderr=subprocess.STDOUT, cwd=str(BASE))
    inputs = f"{cfg['region']}\n{cfg['parallel']}\n{cfg['bots']}\n{cfg['guild_uid']}\n"
    try:
        proc.stdin.write(inputs.encode()); proc.stdin.flush(); proc.stdin.close()
    except Exception as e:
        print(f"[pipe] {e}")
    state["proc"] = proc; state["started_at"] = time.time()
    return {"ok": True, "pid": proc.pid}

@app.route("/api/stop", methods=["POST"])
def api_stop():
    p = state["proc"]
    if not p or p.poll() is not None:
        return {"error": "not running"}, 400
    p.terminate()
    try: p.wait(timeout=5)
    except subprocess.TimeoutExpired: p.kill()
    state["proc"] = None
    return {"ok": True}

@app.route("/api/status")
def api_status():
    p = state["proc"]
    if not p: return {"running": False}
    code = p.poll()
    if code is None:
        return {"running": True, "pid": p.pid, "uptime": int(time.time() - state["started_at"])}
    state["proc"] = None
    return {"running": False, "exit_code": code}

@app.route("/api/logs")
def api_logs():
    offset = int(request.args.get("offset", 0))
    if not LOG_FILE.exists(): return {"content": "", "offset": 0}
    data = LOG_FILE.read_bytes()
    if offset > len(data): offset = 0
    return {"content": data[offset:].decode("utf-8", errors="replace"), "offset": len(data)}

if __name__ == "__main__":
    print("wrapper dashboard: http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)

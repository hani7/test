# agent/service.py
import os
import json
from typing import Dict, Set
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

# ---- Driver portes (RS-485) ----
# Adapte si ton driver de relais est dans rs485.py / LockDriver
try:
    from rs485 import LockDriver
except ImportError:
    LockDriver = None

# ---- Monnayeur TB74 ----
from tb74_rs232 import TB74BillAcceptor, TB74Config, BillEvent

# --------- Config série portes ---------
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyS5")
BAUD = int(os.getenv("SERIAL_BAUD", "9600"))

app = FastAPI(title="Fleuriste Agent")

# --------- Instances globales ---------
lock_driver = None
tb_cfg = TB74Config()
acceptor = None

# Sessions de paiement espèces : session_id -> {target:int, total:int, clients:Set[WebSocket]}
_sessions: Dict[str, Dict] = {}

# --------- Startup ---------
@app.on_event("startup")
def startup():
    global lock_driver, acceptor
    if LockDriver:
        try:
            lock_driver = LockDriver(SERIAL_PORT, BAUD)
        except Exception as e:
            print("LockDriver init failed:", e)
            lock_driver = None
    # TB74
    acceptor = TB74BillAcceptor(tb_cfg, on_event=_on_bill_event)
    acceptor.open()

@app.on_event("shutdown")
def shutdown():
    try:
        if acceptor:
            acceptor.close()
    except Exception:
        pass

# --------- Callbacks ---------
def _on_bill_event(evt: BillEvent):
    # Push à toutes les sessions en cours
    dead_clients: Set[WebSocket] = set()
    for sid, s in _sessions.items():
        s["total"] += evt.value
        payload = {"type": "bill", "value": evt.value, "total": s["total"]}
        for ws in list(s["clients"]):
            try:
                ws.send_text(json.dumps(payload))
            except Exception:
                dead_clients.add(ws)
    # Nettoyage
    if dead_clients:
        for s in _sessions.values():
            for ws in dead_clients:
                s["clients"].discard(ws)

# --------- Endpoints portes ---------
@app.post("/open")
def open_lock(slot: int = Query(..., ge=1, le=32), duration_ms: int = Query(600, ge=100, le=5000)):
    """
    Ouvre le relais 'slot' pendant duration_ms millisecondes.
    """
    if not lock_driver:
        raise HTTPException(500, "LockDriver non initialisé")
    try:
        ok = lock_driver.open_channel(slot, duration_ms)
        return {"ok": bool(ok)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/health")
def health():
    return {
        "status": "ok",
        "serial_port": SERIAL_PORT,
        "baud": BAUD,
        "tb74_port": tb_cfg.port,
        "tb74_baud": tb_cfg.baud,
        "tb74_sim": tb_cfg.simulate,
    }

# --------- Endpoints espèces TB74 ---------
@app.post("/bill/start")
def bill_start(session_id: str, target: int):
    """
    Initialise/Reset une session espèces pour un montant 'target' (DA).
    """
    _sessions[session_id] = {"target": int(target), "total": 0, "clients": set()}
    return {"ok": True}

@app.get("/bill/status")
def bill_status(session_id: str):
    s = _sessions.get(session_id)
    if not s:
        raise HTTPException(404, "Unknown session")
    return {"ok": True, "total": s["total"], "target": s["target"]}

@app.post("/bill/stop")
def bill_stop(session_id: str):
    _sessions.pop(session_id, None)
    return {"ok": True}

@app.websocket("/bill/ws")
async def bill_ws(ws: WebSocket):
    await ws.accept()
    sid = None
    try:
        init = await ws.receive_json()
        sid = init.get("session_id")
        if not sid or sid not in _sessions:
            await ws.send_json({"type": "error", "message": "invalid session"})
            await ws.close()
            return
        _sessions[sid]["clients"].add(ws)
        # Boucle d'attente : le client peut envoyer des "ping" (texte) pour garder la connexion
        while True:
            _ = await ws.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        # cleanup
        try:
            if sid and sid in _sessions:
                _sessions[sid]["clients"].discard(ws)
        except Exception:
            pass

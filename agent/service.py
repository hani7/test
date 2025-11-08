import os
from fastapi import FastAPI, HTTPException
from rs485 import LockDriver

SERIAL_PORT = os.getenv("SERIAL_PORT","/dev/ttyUSB0")
BAUD = int(os.getenv("SERIAL_BAUD","9600"))

app = FastAPI(title="Fleuriste Agent")
driver = None

@app.on_event("startup")
def startup():
    global driver
    driver = LockDriver(SERIAL_PORT, BAUD)

@app.post("/open")
def open_lock(slot: int, duration_ms: int = 500):
    try:
        ok = driver.open_channel(slot, duration_ms)
        return {"ok": bool(ok)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status":"ok","serial_port":SERIAL_PORT}

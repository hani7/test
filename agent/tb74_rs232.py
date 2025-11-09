# agent/tb74_rs232.py
"""
Driver minimal pour monnayeur TB74 en RS-232.
- Gère une boucle de lecture et déclenche un callback à chaque billet accepté.
- Mapping configurable canal -> valeur (DA).
- Mode simulation (TB74_SIM=1) pour tests sans matériel.

⚠️ Les trames exactes (enable/disable/poll) varient selon firmware. Ce driver
utilise une lecture "octet par octet" où chaque octet reçu est traité comme un
code canal (ex: 0x13, 0x14, 0x15). Adapte _enable_acceptance(), _disable_acceptance()
et _parse() quand tu reçois la doc protocole officielle.
"""
import os
import time
import threading
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional
import serial

@dataclass
class BillEvent:
    value: int            # valeur du billet accepté en DA
    raw: bytes = b''      # octets bruts reçus (debug)

@dataclass
class TB74Config:
    port: str = os.getenv("TB74_PORT", "/dev/ttyS9")
    baud: int = int(os.getenv("TB74_BAUD", "9600"))
    simulate: bool = os.getenv("TB74_SIM", "0") == "1"
    # Canal/code -> valeur (DA). Mets ici tes 500/1000/2000 :
    code_map: Dict[int, int] = field(default_factory=lambda: {
        0x13: 500,    # canal/code 0x13 = billet 500 DA
        0x14: 1000,   # canal/code 0x14 = billet 1000 DA
        0x15: 2000,   # canal/code 0x15 = billet 2000 DA
    })
    # (Optionnel) Masque d'inhibition (activer uniquement 500/1000/2000)
    # À adapter au protocole réel ; ici décoratif.
    inhibit_mask: int = 0b00111000  # ex: bits 3,4,5 ON

class TB74BillAcceptor:
    """
    - open(): ouvre le port et active l'acceptation.
    - on_event(BillEvent): callback appelé à chaque billet validé.
    """
    def __init__(self, cfg: TB74Config, on_event: Callable[[BillEvent], None]):
        self.cfg = cfg
        self.on_event = on_event
        self._ser: Optional[serial.Serial] = None
        self._run = False
        self._t: Optional[threading.Thread] = None

    def open(self):
        if self.cfg.simulate:
            self._run = True
            self._t = threading.Thread(target=self._loop_sim, daemon=True)
            self._t.start()
            return

        self._ser = serial.Serial(self.cfg.port, baudrate=self.cfg.baud, timeout=0.2)
        self._enable_acceptance()
        self._run = True
        self._t = threading.Thread(target=self._loop_read, daemon=True)
        self._t.start()

    def close(self):
        self._run = False
        try:
            if self._ser and self._ser.is_open:
                self._disable_acceptance()
                self._ser.close()
        except Exception:
            pass

    # ---------- À ADAPTER AVEC TA DOC PROTO ----------
    def _enable_acceptance(self):
        """
        Envoie (si nécessaire) une trame 'enable' + masque d'inhibition.
        Exemple illustratif (aucun effet réel sans doc) :
            self._ser.write(b"\x02\x11" + bytes([self.cfg.inhibit_mask]) + b"\x03")
        """
        pass

    def _disable_acceptance(self):
        """Trame 'disable' (illustrative)."""
        pass

    def _parse(self, b: bytes) -> Optional[BillEvent]:
        """
        Parse une réponse du monnayeur.
        Dans cette version simple, on traite 1 octet = 'code canal'.
        Retourne BillEvent si code reconnu, sinon None.
        """
        if not b:
            return None
        code = b[0]
        if code in self.cfg.code_map:
            return BillEvent(value=self.cfg.code_map[code], raw=b)
        return None

    # ---------- Boucles ----------
    def _loop_read(self):
        while self._run:
            try:
                ch = self._ser.read(1)
                evt = self._parse(ch)
                if evt:
                    self.on_event(evt)
            except Exception:
                time.sleep(0.1)

    def _loop_sim(self):
        # Simule un billet de 1000 DA toutes les 3s (pour tester l'UI)
        while self._run:
            time.sleep(3.0)
            self.on_event(BillEvent(value=1000, raw=b"\x14"))

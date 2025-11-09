import serial, time

def crc_xor(data: bytes) -> int:
    c = 0
    for b in data: c ^= b
    return c & 0xFF

class LockDriver:
    """
    Protocole générique :
    [0xAA][ADDR=0x01][CMD=0x10][CHANNEL][DUR_H][DUR_L][CRC_XOR]
    Adapte si ta carte a un autre protocole.
    """
<<<<<<< HEAD
    def __init__(self, port="/dev/ttyS5", baud=9600, addr=1):
=======
    def __init__(self, port="/dev/ttyS5", baud=9600, addr=1):
>>>>>>> d131bf99810b871477a0090032392574e82ec565
        self.ser = serial.Serial(port, baudrate=baud, timeout=0.5)
        self.addr = addr

    def open_channel(self, channel:int, duration_ms:int=500) -> bool:
        if not (1 <= channel <= 32): raise ValueError("channel 1..32")
        frame = bytearray([0xAA, self.addr, 0x10, channel, (duration_ms>>8)&0xFF, duration_ms&0xFF])
        # CRC
        frame.append(crc_xor(frame))
        self.ser.reset_input_buffer()
        self.ser.write(frame)
        time.sleep(0.05)
        _ = self.ser.read(1)  # si ACK
        return True

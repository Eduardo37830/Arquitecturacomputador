class Memory:
    def __init__(self, size=256):
        self.data = [0] * size

    def read(self, address):
        if 0 <= address < len(self.data):
            return self.data[address]
        else:
            print(f"[ERROR] Lectura fuera de rango: {address}")
            return 0

    def write(self, address, value):
        if 0 <= address < len(self.data):
            self.data[address] = value & 0xFF
        else:
            print(f"[ERROR] Escritura fuera de rango: {address}")

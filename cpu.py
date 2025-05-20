class Registers:
    def __init__(self):
        self.PC = 0      # Program Counter
        self.IR = 0      # Instruction Register
        self.PSW = 0     # Program Status Word (flags)
        self.MAR = 0     # Memory Address Register
        self.MBR = 0     # Memory Buffer Register
        self.RVPU = [0]*8  # Banco de 8 registros de propósito general (R0-R7)

    def as_dict(self):
        return {
            'PC': self.PC,
            'IR': self.IR,
            'PSW': self.PSW,
            'MAR': self.MAR,
            'MBR': self.MBR,
            'RVPU': self.RVPU.copy()
        }


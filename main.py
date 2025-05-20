from alu import ALU
from cpu import Registers
from memory import Memory

class CPU:
    def __init__(self):
        self.alu = ALU()
        self.registers = Registers()
        self.memory = Memory()
        self.current_cycle = 'FETCH'
        self.halted = False

    def decode_execute(self, instr):
        if isinstance(instr, tuple):
            opcode = instr[0].upper()
            ops = instr[1:]
        else:
            opcode = instr.upper()
            ops = ()
        # 0 direcciones
        if opcode == "NOP":
            pass
        elif opcode in ("HLT", "HALT"):
            self.halted = True
        elif opcode == "RET":
            # Simulación simple: no hay pila, solo ejemplo
            pass
        elif opcode == "CLC":
            self.alu.flags['C'] = 0
        elif opcode == "STC":
            self.alu.flags['C'] = 1
        elif opcode == "IN":
            val = int(input("IN (entrada de dato): "))
            self.registers.RVPU[0] = val & 0xFF
        elif opcode == "OUT":
            print(f"OUT: {self.registers.RVPU[0]}")
        # 1 dirección
        elif opcode == "LOAD":
            addr, = ops
            self.registers.MAR = addr
            self.registers.MBR = self.memory.read(self.registers.MAR)
            self.registers.RVPU[0] = self.registers.MBR
        elif opcode == "STORE":
            addr, = ops
            self.registers.MAR = addr
            self.registers.MBR = self.registers.RVPU[0]
            self.memory.write(self.registers.MAR, self.registers.MBR)
        elif opcode == "JMP":
            addr, = ops
            self.registers.PC = addr
        elif opcode == "JZ":
            addr, = ops
            if self.alu.flags['Z']:
                self.registers.PC = addr
        elif opcode == "INC":
            addr, = ops
            self.registers.RVPU[addr] = self.alu.add(self.registers.RVPU[addr], 1)
        elif opcode == "DEC":
            addr, = ops
            self.registers.RVPU[addr] = self.alu.sub(self.registers.RVPU[addr], 1)
        elif opcode == "NOT":
            addr, = ops
            self.registers.RVPU[addr] = self.alu.complement(self.registers.RVPU[addr])
        # 2 direcciones
        elif opcode == "MOV":
            dst, src = ops
            self.registers.RVPU[dst] = self.registers.RVPU[src]
        elif opcode == "ADD":
            if len(ops) == 2:
                dst, src = ops
                self.registers.RVPU[dst] = self.alu.add(self.registers.RVPU[dst], self.registers.RVPU[src])
            elif len(ops) == 3:
                dst, src1, src2 = ops
                self.registers.RVPU[dst] = self.alu.add(self.registers.RVPU[src1], self.registers.RVPU[src2])
        elif opcode == "SUB":
            if len(ops) == 2:
                dst, src = ops
                self.registers.RVPU[dst] = self.alu.sub(self.registers.RVPU[dst], self.registers.RVPU[src])
            elif len(ops) == 3:
                dst, src1, src2 = ops
                self.registers.RVPU[dst] = self.alu.sub(self.registers.RVPU[src1], self.registers.RVPU[src2])
        elif opcode == "AND":
            if len(ops) == 2:
                dst, src = ops
                self.registers.RVPU[dst] = self.alu.logical_and(self.registers.RVPU[dst], self.registers.RVPU[src])
            elif len(ops) == 3:
                dst, src1, src2 = ops
                self.registers.RVPU[dst] = self.alu.logical_and(self.registers.RVPU[src1], self.registers.RVPU[src2])
        elif opcode == "OR":
            if len(ops) == 2:
                dst, src = ops
                self.registers.RVPU[dst] = self.alu.logical_or(self.registers.RVPU[dst], self.registers.RVPU[src])
            elif len(ops) == 3:
                dst, src1, src2 = ops
                self.registers.RVPU[dst] = self.alu.logical_or(self.registers.RVPU[src1], self.registers.RVPU[src2])
        elif opcode == "CMP":
            if len(ops) == 2:
                dst, src = ops
                _ = self.alu.sub(self.registers.RVPU[dst], self.registers.RVPU[src])
            elif len(ops) == 3:
                dst, src1, src2 = ops
                _ = self.alu.sub(self.registers.RVPU[src1], self.registers.RVPU[src2])
        elif opcode == "XCHG":
            dst, src = ops
            self.registers.RVPU[dst], self.registers.RVPU[src] = self.registers.RVPU[src], self.registers.RVPU[dst]
        elif opcode == "XOR":
            if len(ops) == 2:
                dst, src = ops
                self.registers.RVPU[dst] = self.alu.logical_xor(self.registers.RVPU[dst], self.registers.RVPU[src])
            elif len(ops) == 3:
                dst, src1, src2 = ops
                self.registers.RVPU[dst] = self.alu.logical_xor(self.registers.RVPU[src1], self.registers.RVPU[src2])
        elif opcode == "SHL":
            if len(ops) == 2:
                dst, n = ops
                self.registers.RVPU[dst] = self.alu.shift_left(self.registers.RVPU[dst], n)
            elif len(ops) == 3:
                dst, src, n = ops
                self.registers.RVPU[dst] = self.alu.shift_left(self.registers.RVPU[src], n)
        elif opcode == "SHR":
            if len(ops) == 2:
                dst, n = ops
                self.registers.RVPU[dst] = self.alu.shift_right(self.registers.RVPU[dst], n)
            elif len(ops) == 3:
                dst, src, n = ops
                self.registers.RVPU[dst] = self.alu.shift_right(self.registers.RVPU[src], n)
        elif opcode == "MUL":
            if len(ops) == 3:
                dst, src1, src2 = ops
                res = (self.registers.RVPU[src1] * self.registers.RVPU[src2]) & 0xFF
                self.registers.RVPU[dst] = res
                self.alu._update_flags(res)
        elif opcode == "DIV":
            if len(ops) == 3:
                dst, src1, src2 = ops
                if self.registers.RVPU[src2] != 0:
                    res = (self.registers.RVPU[src1] // self.registers.RVPU[src2]) & 0xFF
                else:
                    res = 0
                self.registers.RVPU[dst] = res
                self.alu._update_flags(res)
        self.registers.PSW = (
            (self.alu.flags['Z'] << 0) |
            (self.alu.flags['C'] << 1) |
            (self.alu.flags['S'] << 2) |
            (self.alu.flags['O'] << 3)
        )

    def step(self):
        # Ciclo de instrucción (fetch-decode-execute) paso a paso
        if not hasattr(self, '_cycle_state'):
            self._cycle_state = 0  # 0: fetch, 1: decode, 2: execute
        if self._cycle_state == 0:
            self.current_cycle = 'FETCH'
            pc = self.registers.PC
            instr = self.memory.read(pc)
            self.registers.IR = instr
            self.registers.PC += 1
            self._fetched_instr = instr
            self._cycle_state = 1
        elif self._cycle_state == 1:
            self.current_cycle = 'DECODE'
            # Aquí podrías hacer decodificación más detallada si lo deseas
            self._cycle_state = 2
        elif self._cycle_state == 2:
            self.current_cycle = 'EXECUTE'
            self.decode_execute(self._fetched_instr)
            self._cycle_state = 0
        else:
            self._cycle_state = 0
            self.current_cycle = 'FETCH'

if __name__ == '__main__':
    from gui import CPUGUI
    cpu = CPU()
    # Ejemplo de carga de programa en memoria
    # Programa: R0 = 5; R1 = 10; R2 = R0 + R1
    cpu.memory.data[0] = ("MOV", 0, 0)      # R0 = R0 (NOP)
    cpu.memory.data[1] = ("LOAD", 0, 100)    # R0 = MEM[100]
    cpu.memory.data[2] = ("LOAD", 1, 101)    # R1 = MEM[101]
    cpu.memory.data[3] = ("ADD", 2, 0, 1)    # R2 = R0 + R1
    cpu.memory.data[4] = ("NOP",)
    cpu.memory.data[100] = 5
    cpu.memory.data[101] = 10
    app = CPUGUI(cpu, cpu.memory)
    app.mainloop()

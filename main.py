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
        # Diccionario de instrucciones
        self.instruction_set = {
            # 0 direcciones
            'NOP': self._op_nop,
            'HLT': self._op_hlt,
            'HALT': self._op_hlt,
            'RET': self._op_ret,
            'CLC': self._op_clc,
            'STC': self._op_stc,
            'IN': self._op_in,
            'OUT': self._op_out,
            'PUSH': self._op_push,
            'POP': self._op_pop,
            # 1 dirección
            'LOAD': self._op_load,
            'STORE': self._op_store,
            'JMP': self._op_jmp,
            'JZ': self._op_jz,
            'INC': self._op_inc,
            'DEC': self._op_dec,
            'NOT': self._op_not,
            # 2 direcciones
            'MOV': self._op_mov,
            'ADD': self._op_add,
            'SUB': self._op_sub,
            'AND': self._op_and,
            'OR': self._op_or,
            'CMP': self._op_cmp,
            'XCHG': self._op_xchg,
            'XOR': self._op_xor,
            'SHL': self._op_shl,
            'SHR': self._op_shr,
            # 3 direcciones
            'MUL': self._op_mul,
            'DIV': self._op_div,
        }

    def decode_execute(self, instr):
        # Solo procesa si es una instrucción válida (tupla o string)
        if not isinstance(instr, (tuple, str)):
            return  # Ignora datos que no son instrucciones
        if isinstance(instr, tuple):
            opcode = instr[0].upper()
            ops = instr[1:]
        else:
            opcode = instr.upper()
            ops = ()
        if opcode in self.instruction_set:
            self.instruction_set[opcode](*ops)
        self.registers.PSW = (
            (self.alu.flags['Z'] << 0) |
            (self.alu.flags['C'] << 1) |
            (self.alu.flags['S'] << 2) |
            (self.alu.flags['O'] << 3)
        )

    # Métodos para cada instrucción
    def _op_nop(self):
        pass
    def _op_hlt(self):
        self.halted = True
    def _op_ret(self):
        pass  # Simulación simple
    def _op_clc(self):
        self.alu.flags['C'] = 0
    def _op_stc(self):
        self.alu.flags['C'] = 1
    def _op_in(self):
        val = int(input("IN (entrada de dato): "))
        self.registers.RVPU[0] = val & 0xFF
        print(f"[DEBUG] IN -> R0 = {self.registers.RVPU[0]}") # DEBUG
    def _op_out(self):
        print(f"OUT: {self.registers.RVPU[0]}")
    def _resolve_operand(self, op):
        if isinstance(op, tuple) and op[0] == '@':
            return self.memory.read(op[1])
        return op

    def _op_load(self, *ops):
        if len(ops) == 2:
            reg, addr = ops
            addr_val = addr[1] if isinstance(addr, tuple) and addr[0] == '@' else addr
            print(f"[DEBUG] Executing: LOAD R{reg}, M[{addr_val}]")
            self.registers.MAR = addr_val
            self.registers.MBR = self.memory.read(self.registers.MAR)
            print(f"[DEBUG] LOAD: M[{addr_val}] (value: {self.registers.MBR}) -> MBR")
            self.registers.RVPU[reg] = self.registers.MBR
            print(f"[DEBUG] LOAD: MBR -> R{reg} (new value: {self.registers.RVPU[reg]})")
        else:
            addr, = ops
            addr_val = addr[1] if isinstance(addr, tuple) and addr[0] == '@' else addr
            print(f"[DEBUG] Executing: LOAD R0, M[{addr_val}]")
            self.registers.MAR = addr_val
            self.registers.MBR = self.memory.read(self.registers.MAR)
            print(f"[DEBUG] LOAD: M[{addr_val}] (value: {self.registers.MBR}) -> MBR")
            self.registers.RVPU[0] = self.registers.MBR
            print(f"[DEBUG] LOAD: MBR -> R0 (new value: {self.registers.RVPU[0]})")

    def _op_store(self, *ops):
        if len(ops) == 2:
            reg, addr = ops
            addr_val = addr[1] if isinstance(addr, tuple) and addr[0] == '@' else addr
            print(f"[DEBUG] Executing: STORE R{reg}, M[{addr_val}]")
            self.registers.MAR = addr_val
            self.registers.MBR = self.registers.RVPU[reg]
            print(f"[DEBUG] STORE: R{reg} (value: {self.registers.RVPU[reg]}) -> MBR")
            self.memory.write(self.registers.MAR, self.registers.MBR)
            print(f"[DEBUG] STORE: MBR -> M[{addr_val}] (new value: {self.memory.read(addr_val)})")
        else:
            addr, = ops
            addr_val = addr[1] if isinstance(addr, tuple) and addr[0] == '@' else addr
            print(f"[DEBUG] Executing: STORE R0, M[{addr_val}]")
            self.registers.MAR = addr_val
            self.registers.MBR = self.registers.RVPU[0]
            print(f"[DEBUG] STORE: R0 (value: {self.registers.RVPU[0]}) -> MBR")
            self.memory.write(self.registers.MAR, self.registers.MBR)
            print(f"[DEBUG] STORE: MBR -> M[{addr_val}] (new value: {self.memory.read(addr_val)})")

    def _op_add(self, *ops):
        if len(ops) == 2:
            dst, src = ops
            if not self._valid_reg(dst): return
            val_dst_before = self.registers.RVPU[dst]
            val_src = self._resolve_operand(src)
            print(f"[DEBUG] Executing: ADD R{dst}, {src} (R{dst} before: {val_dst_before}, src: {val_src})")
            self.registers.RVPU[dst] = self.alu.add(val_dst_before, val_src)
            print(f"[DEBUG] ADD: R{dst} new value: {self.registers.RVPU[dst]}")
        elif len(ops) == 3:
            dst, src1, src2 = ops
            if not self._valid_reg(dst): return
            val_src1 = self._resolve_operand(src1)
            val_src2 = self._resolve_operand(src2)
            print(f"[DEBUG] Executing: ADD R{dst}, {src1}, {src2} (src1: {val_src1}, src2: {val_src2})")
            self.registers.RVPU[dst] = self.alu.add(val_src1, val_src2)
            print(f"[DEBUG] ADD: R{dst} new value: {self.registers.RVPU[dst]}")

    def _op_sub(self, *ops):
        if len(ops) == 2:
            dst, src = ops
            if not self._valid_reg(dst): return
            val_dst_before = self.registers.RVPU[dst]
            val_src = self._resolve_operand(src)
            print(f"[DEBUG] Executing: SUB R{dst}, {src} (R{dst} before: {val_dst_before}, src: {val_src})")
            self.registers.RVPU[dst] = self.alu.sub(val_dst_before, val_src)
            print(f"[DEBUG] SUB: R{dst} new value: {self.registers.RVPU[dst]}")
        elif len(ops) == 3:
            dst, src1, src2 = ops
            if not self._valid_reg(dst): return
            val_src1 = self._resolve_operand(src1)
            val_src2 = self._resolve_operand(src2)
            print(f"[DEBUG] Executing: SUB R{dst}, {src1}, {src2} (src1: {val_src1}, src2: {val_src2})")
            self.registers.RVPU[dst] = self.alu.sub(val_src1, val_src2)
            print(f"[DEBUG] SUB: R{dst} new value: {self.registers.RVPU[dst]}")

    def _op_jmp(self, addr):
        self.registers.PC = addr
    def _op_jz(self, addr):
        if self.alu.flags['Z']:
            self.registers.PC = addr

    def _valid_reg(self, idx):
        if not (0 <= idx < len(self.registers.RVPU)):
            print(f"[ERROR] Registro fuera de rango: R{idx}")
            return False
        return True

    def _op_inc(self, addr):
        if not self._valid_reg(addr): return
        before = self.registers.RVPU[addr]
        self.registers.RVPU[addr] = self.alu.add(self.registers.RVPU[addr], 1)
        print(f"[DEBUG] INC: R{addr} {before} -> {self.registers.RVPU[addr]}")

    def _op_dec(self, addr):
        if not self._valid_reg(addr): return
        before = self.registers.RVPU[addr]
        self.registers.RVPU[addr] = self.alu.sub(self.registers.RVPU[addr], 1)
        print(f"[DEBUG] DEC: R{addr} {before} -> {self.registers.RVPU[addr]}")

    def _op_not(self, addr):
        if not self._valid_reg(addr): return
        before = self.registers.RVPU[addr]
        self.registers.RVPU[addr] = self.alu.complement(self.registers.RVPU[addr])
        print(f"[DEBUG] NOT: R{addr} {before} -> {self.registers.RVPU[addr]}")

    def _op_mov(self, dst, src):
        if not self._valid_reg(dst) or not self._valid_reg(src): return
        before = self.registers.RVPU[dst]
        self.registers.RVPU[dst] = self.registers.RVPU[src]
        print(f"[DEBUG] MOV: R{dst} {before} -> {self.registers.RVPU[dst]} (copiado de R{src})")

    def _op_and(self, *ops):
        if len(ops) == 2:
            dst, src = ops
            if not self._valid_reg(dst) or not self._valid_reg(src): return
            self.registers.RVPU[dst] = self.alu.logical_and(self.registers.RVPU[dst], self.registers.RVPU[src])
        elif len(ops) == 3:
            dst, src1, src2 = ops
            if not self._valid_reg(dst) or not self._valid_reg(src1) or not self._valid_reg(src2): return
            self.registers.RVPU[dst] = self.alu.logical_and(self.registers.RVPU[src1], self.registers.RVPU[src2])

    def _op_or(self, *ops):
        if len(ops) == 2:
            dst, src = ops
            if not self._valid_reg(dst) or not self._valid_reg(src): return
            self.registers.RVPU[dst] = self.alu.logical_or(self.registers.RVPU[dst], self.registers.RVPU[src])
        elif len(ops) == 3:
            dst, src1, src2 = ops
            if not self._valid_reg(dst) or not self._valid_reg(src1) or not self._valid_reg(src2): return
            self.registers.RVPU[dst] = self.alu.logical_or(self.registers.RVPU[src1], self.registers.RVPU[src2])

    def _op_cmp(self, *ops):
        if len(ops) == 2:
            dst, src = ops
            if not self._valid_reg(dst) or not self._valid_reg(src): return
            _ = self.alu.sub(self.registers.RVPU[dst], self.registers.RVPU[src])
        elif len(ops) == 3:
            dst, src1, src2 = ops
            if not self._valid_reg(dst) or not self._valid_reg(src1) or not self._valid_reg(src2): return
            _ = self.alu.sub(self.registers.RVPU[src1], self.registers.RVPU[src2])

    def _op_xchg(self, dst, src):
        if not self._valid_reg(dst) or not self._valid_reg(src): return
        self.registers.RVPU[dst], self.registers.RVPU[src] = self.registers.RVPU[src], self.registers.RVPU[dst]

    def _op_xor(self, *ops):
        if len(ops) == 2:
            dst, src = ops
            if not self._valid_reg(dst) or not self._valid_reg(src): return
            self.registers.RVPU[dst] = self.alu.logical_xor(self.registers.RVPU[dst], self.registers.RVPU[src])
        elif len(ops) == 3:
            dst, src1, src2 = ops
            if not self._valid_reg(dst) or not self._valid_reg(src1) or not self._valid_reg(src2): return
            self.registers.RVPU[dst] = self.alu.logical_xor(self.registers.RVPU[src1], self.registers.RVPU[src2])

    def _op_shl(self, *ops):
        if len(ops) == 2:
            dst, n = ops
            if not self._valid_reg(dst): return
            self.registers.RVPU[dst] = self.alu.shift_left(self.registers.RVPU[dst], n)
        elif len(ops) == 3:
            dst, src, n = ops
            if not self._valid_reg(dst) or not self._valid_reg(src): return
            self.registers.RVPU[dst] = self.alu.shift_left(self.registers.RVPU[src], n)

    def _op_shr(self, *ops):
        if len(ops) == 2:
            dst, n = ops
            if not self._valid_reg(dst): return
            self.registers.RVPU[dst] = self.alu.shift_right(self.registers.RVPU[dst], n)
        elif len(ops) == 3:
            dst, src, n = ops
            if not self._valid_reg(dst) or not self._valid_reg(src): return
            self.registers.RVPU[dst] = self.alu.shift_right(self.registers.RVPU[src], n)

    def _op_mul(self, dst, src1, src2):
        if not self._valid_reg(dst) or not self._valid_reg(src1) or not self._valid_reg(src2): return
        res = (self.registers.RVPU[src1] * self.registers.RVPU[src2]) & 0xFF
        self.registers.RVPU[dst] = res
        self.alu._update_flags(res)

    def _op_div(self, dst, src1, src2):
        if not self._valid_reg(dst) or not self._valid_reg(src1) or not self._valid_reg(src2): return
        if self.registers.RVPU[src2] != 0:
            res = (self.registers.RVPU[src1] // self.registers.RVPU[src2]) & 0xFF
        else:
            res = 0
        self.registers.RVPU[dst] = res
        self.alu._update_flags(res)

    def _op_push(self, *ops):
        # Por convención, SP es R7
        sp = 7
        reg = 0
        if len(ops) == 1:
            reg = ops[0]
        self.registers.RVPU[sp] = (self.registers.RVPU[sp] - 1) & 0xFF
        addr = self.registers.RVPU[sp]
        self.memory.write(addr, self.registers.RVPU[reg])
    def _op_pop(self, *ops):
        sp = 7
        reg = 0
        if len(ops) == 1:
            reg = ops[0]
        addr = self.registers.RVPU[sp]
        self.registers.RVPU[reg] = self.memory.read(addr)
        self.registers.RVPU[sp] = (self.registers.RVPU[sp] + 1) & 0xFF

    def step(self):
        # Ejecución paso a paso de cada fase FI-DI-CO-FO-EI-WO
        if not hasattr(self, '_fidicofoeiwo_state'):
            self._fidicofoeiwo_state = 0
            self._fidicofoeiwo_context = {}
        if self.halted:
            print("[FIDICOFOEIWO] CPU detenida (HALT)")
            return
        fases = [
            'FETCH', 'IDENTIFICACION', 'DECODIFICACION', 'CALCULO_OPERANDO',
            'FETCH_OPERANDO', 'EJECUCION', 'WRITEBACK', 'OUTPUT'
        ]
        fase = fases[self._fidicofoeiwo_state]
        ctx = self._fidicofoeiwo_context
        if fase == 'FETCH':
            pc = self.registers.PC
            instr = self.memory.read(pc)
            print(f"[FIDICOFOEIWO] FETCH: PC={pc}, INSTR={instr}")
            self.registers.IR = instr
            ctx['instr'] = instr
            ctx['pc'] = pc
            self.registers.PC += 1
        elif fase == 'IDENTIFICACION':
            instr = ctx['instr']
            if isinstance(instr, tuple):
                opcode = instr[0].upper()
                ops = instr[1:]
            elif isinstance(instr, str):
                opcode = instr.upper()
                ops = ()
            else:
                print("[FIDICOFOEIWO] INSTRUCCIÓN NO VÁLIDA")
                self._fidicofoeiwo_state = 0
                return
            ctx['opcode'] = opcode
            ctx['ops'] = ops
            print(f"[FIDICOFOEIWO] IDENTIFICACIÓN: OPCODE={opcode}")
        elif fase == 'DECODIFICACION':
            opcode = ctx['opcode']
            ops = ctx['ops']
            if opcode not in self.instruction_set:
                print(f"[FIDICOFOEIWO] INSTRUCCIÓN DESCONOCIDA: {opcode}")
                self._fidicofoeiwo_state = 0
                return
            print(f"[FIDICOFOEIWO] DECODIFICACIÓN: OPERANDOS={ops}")
        elif fase == 'CALCULO_OPERANDO':
            ops = ctx['ops']
            resolved_ops = tuple(self._resolve_operand(op) for op in ops)
            ctx['resolved_ops'] = resolved_ops
            print(f"[FIDICOFOEIWO] CÁLCULO DE OPERANDO: {resolved_ops}")
        elif fase == 'FETCH_OPERANDO':
            # En este ejemplo, ya se resolvieron los operandos en la fase anterior
            print(f"[FIDICOFOEIWO] FETCH OPERANDO: {ctx['resolved_ops']}")
        elif fase == 'EJECUCION':
            opcode = ctx['opcode']
            resolved_ops = ctx['resolved_ops']
            print(f"[FIDICOFOEIWO] EJECUCIÓN: {opcode} {resolved_ops}")
            self.instruction_set[opcode](*resolved_ops)
        elif fase == 'WRITEBACK':
            # Simulación: el writeback depende de la instrucción, pero actualizamos PSW
            self.registers.PSW = (
                (self.alu.flags['Z'] << 0) |
                (self.alu.flags['C'] << 1) |
                (self.alu.flags['S'] << 2) |
                (self.alu.flags['O'] << 3)
            )
            print(f"[FIDICOFOEIWO] WRITEBACK: PSW={self.registers.PSW}")
        elif fase == 'OUTPUT':
            # Simulación: solo mostramos que terminó el ciclo
            print(f"[FIDICOFOEIWO] OUTPUT: Fin de ciclo para instrucción {ctx['opcode']}\n")
        # Avanza a la siguiente fase
        self._fidicofoeiwo_state = (self._fidicofoeiwo_state + 1) % len(fases)
        # Si termina OUTPUT, reinicia contexto para la siguiente instrucción
        if self._fidicofoeiwo_state == 0:
            self._fidicofoeiwo_context = {}

    def get_fidicofoeiwo_phase(self):
        fases = [
            'FETCH', 'IDENTIFICACION', 'DECODIFICACION', 'CALCULO_OPERANDO',
            'FETCH_OPERANDO', 'EJECUCION', 'WRITEBACK', 'OUTPUT'
        ]
        if hasattr(self, '_fidicofoeiwo_state'):
            return fases[self._fidicofoeiwo_state]
        return 'FETCH'

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

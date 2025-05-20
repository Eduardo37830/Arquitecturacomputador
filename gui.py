import tkinter as tk
from tkinter import ttk

class CPUGUI(tk.Tk):
    def __init__(self, cpu, memory):
        super().__init__()
        self.title('Simulador de Computador - CPU')
        self.cpu = cpu
        self.memory = memory
        self.create_widgets()
        self.update_view()

    def create_widgets(self):
        self.reg_frame = ttk.LabelFrame(self, text='Registros')
        self.reg_frame.grid(row=0, column=0, padx=10, pady=10)
        self.reg_labels = {}
        for i, reg in enumerate(['PC', 'IR', 'PSW', 'MAR', 'MBR']):
            lbl = ttk.Label(self.reg_frame, text=f'{reg}: 0')
            lbl.grid(row=i, column=0, sticky='w')
            self.reg_labels[reg] = lbl
        self.rvpu_labels = []
        for i in range(8):
            lbl = ttk.Label(self.reg_frame, text=f'R{i}: 0')
            lbl.grid(row=i, column=1, sticky='w')
            self.rvpu_labels.append(lbl)
        # Flags de la ALU
        self.flag_frame = ttk.LabelFrame(self, text='Flags ALU')
        self.flag_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n')
        self.flag_labels = {}
        for i, flag in enumerate(['Z', 'C', 'S', 'O']):
            lbl = ttk.Label(self.flag_frame, text=f'{flag}: 0')
            lbl.grid(row=i, column=0, sticky='w')
            self.flag_labels[flag] = lbl
        # Buses
        self.bus_frame = ttk.LabelFrame(self, text='Buses')
        self.bus_frame.grid(row=1, column=1, padx=10, pady=10, sticky='n')
        self.bus_labels = {}
        for i, bus in enumerate(['Bus de Direcciones (MAR)', 'Bus de Datos (MBR)']):
            lbl = ttk.Label(self.bus_frame, text=f'{bus}: 0')
            lbl.grid(row=i, column=0, sticky='w')
            self.bus_labels[bus] = lbl
        # Memoria completa
        self.mem_frame = ttk.LabelFrame(self, text='Memoria (RAM)')
        self.mem_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        self.mem_canvas = tk.Canvas(self.mem_frame, width=600, height=200)
        self.mem_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.mem_scroll = ttk.Scrollbar(self.mem_frame, orient='vertical', command=self.mem_canvas.yview)
        self.mem_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.mem_canvas.configure(yscrollcommand=self.mem_scroll.set)
        self.mem_table_frame = tk.Frame(self.mem_canvas)
        self.mem_canvas.create_window((0,0), window=self.mem_table_frame, anchor='nw')
        self.mem_labels = []
        for i in range(len(self.memory.data)):
            lbl = tk.Label(self.mem_table_frame, text=f'{i:03}: {self.memory.data[i]}', anchor='w', width=20)
            lbl.grid(row=i, column=0, sticky='w')
            self.mem_labels.append(lbl)
        self.mem_table_frame.update_idletasks()
        self.mem_canvas.config(scrollregion=self.mem_canvas.bbox("all"))
        self.step_btn = ttk.Button(self, text='Paso', command=self.step)
        self.step_btn.grid(row=3, column=0, pady=10)
        # Ciclo de instrucción
        self.cycle_frame = ttk.LabelFrame(self, text='Ciclo de instrucción')
        self.cycle_frame.grid(row=3, column=1, padx=10, pady=10, sticky='n')
        self.cycle_label = ttk.Label(self.cycle_frame, text='Fase: FETCH')
        self.cycle_label.grid(row=0, column=0, sticky='w')
        # Área de texto para instrucciones y botón de carga
        self.input_frame = ttk.LabelFrame(self, text='Programa (una instrucción por línea)')
        self.input_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        self.instr_text = tk.Text(self.input_frame, height=8, width=70)
        self.instr_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.load_btn = ttk.Button(self.input_frame, text='Cargar instrucciones', command=self.load_instructions)
        self.load_btn.pack(side=tk.RIGHT, padx=10)

    def update_view(self):
        regs = self.cpu.registers.as_dict()
        for reg in ['PC', 'IR', 'PSW', 'MAR', 'MBR']:
            self.reg_labels[reg].config(text=f'{reg}: {regs[reg]}')
        for i, val in enumerate(regs['RVPU']):
            self.rvpu_labels[i].config(text=f'R{i}: {val}')
        # Flags ALU
        flags = self.cpu.alu.flags
        for flag in ['Z', 'C', 'S', 'O']:
            self.flag_labels[flag].config(text=f'{flag}: {flags[flag]}')
        # Buses
        self.bus_labels['Bus de Direcciones (MAR)'].config(text=f'Bus de Direcciones (MAR): {regs["MAR"]}')
        self.bus_labels['Bus de Datos (MBR)'].config(text=f'Bus de Datos (MBR): {regs["MBR"]}')
        # Memoria
        for i, lbl in enumerate(self.mem_labels):
            val = self.memory.data[i]
            if isinstance(val, tuple):
                lbl.config(text=f'{i:03}: {val}')
            else:
                lbl.config(text=f'{i:03}: {val}')
        self.mem_table_frame.update_idletasks()
        self.mem_canvas.config(scrollregion=self.mem_canvas.bbox("all"))
        # Actualizar ciclo de instrucción
        self.cycle_label.config(text=f'Fase: {self.cpu.current_cycle}')

    def step(self):
        self.cpu.step()
        self.update_view()

    def load_instructions(self):
        # Limpiar memoria y registros
        self.cpu.memory.data = [0] * len(self.cpu.memory.data)
        self.cpu.registers.PC = 0
        self.cpu.registers.IR = 0
        self.cpu.registers.PSW = 0
        self.cpu.registers.MAR = 0
        self.cpu.registers.MBR = 0
        self.cpu.registers.RVPU = [0]*8
        self.cpu.current_cycle = 'FETCH'
        if hasattr(self.cpu, '_cycle_state'):
            self.cpu._cycle_state = 0
        # Parsear instrucciones
        lines = self.instr_text.get('1.0', tk.END).strip().split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            instr = self.parse_instruction(line)
            if instr is not None:
                self.cpu.memory.data[i] = instr
        self.update_view()

    def parse_instruction(self, line):
        # Formato: OPCODE op1,op2,op3
        parts = line.replace(',', ' ').split()
        if not parts:
            return None
        opcode = parts[0].upper()
        ops = []
        for p in parts[1:]:
            try:
                ops.append(int(p))
            except ValueError:
                return None
        return tuple([opcode] + ops)


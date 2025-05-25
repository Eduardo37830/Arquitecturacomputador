import tkinter as tk
from tkinter import ttk
from tkinter import font

class CPUGUI(tk.Tk):
    def __init__(self, cpu, memory):
        super().__init__()
        self.title('Simulador de Computador - CPU')
        self.configure(bg='#23272e')
        self.cpu = cpu
        self.memory = memory
        self.custom_font = font.Font(family='Consolas', size=10)
        self.create_widgets()
        self.update_view()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelFrame', background='#282c34', foreground='#61dafb', font=('Consolas', 10, 'bold'))
        style.configure('TLabel', background='#282c34', foreground='#abb2bf', font=('Consolas', 9))
        style.configure('TButton', background='#61dafb', foreground='#23272e', font=('Consolas', 9, 'bold'))
        style.configure('TFrame', background='#282c34')

        # Frame principal para mejor organización
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Registros y flags
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky='nw')
        self.reg_frame = ttk.LabelFrame(self.left_frame, text='Registros')
        self.reg_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        self.reg_labels = {}
        for i, reg in enumerate(['PC', 'IR', 'PSW', 'MAR', 'MBR']):
            lbl = ttk.Label(self.reg_frame, text=f'{reg}: 0')
            lbl.grid(row=i, column=0, sticky='w', pady=1)
            self.reg_labels[reg] = lbl
        self.rvpu_labels = []
        for i in range(8):
            lbl = ttk.Label(self.reg_frame, text=f'R{i}: 0')
            lbl.grid(row=i, column=1, sticky='w', pady=1)
            self.rvpu_labels.append(lbl)
        self.flag_frame = ttk.LabelFrame(self.left_frame, text='Flags ALU')
        self.flag_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        self.flag_labels = {}
        for i, flag in enumerate(['Z', 'C', 'S', 'O']):
            lbl = ttk.Label(self.flag_frame, text=f'{flag}: 0')
            lbl.grid(row=i, column=0, sticky='w', pady=1)
            self.flag_labels[flag] = lbl
        self.bus_frame = ttk.LabelFrame(self.left_frame, text='Buses')
        self.bus_frame.grid(row=2, column=0, padx=5, pady=5, sticky='nw')
        self.bus_labels = {}
        for i, bus in enumerate(['Bus de Direcciones (MAR)', 'Bus de Datos (MBR)']):
            lbl = ttk.Label(self.bus_frame, text=f'{bus}: 0')
            lbl.grid(row=i, column=0, sticky='w', pady=1)
            self.bus_labels[bus] = lbl

        # Memoria visual (derecha)
        self.mem_visual_frame = ttk.LabelFrame(self.main_frame, text='Memoria RAM (Guía Visual)')
        self.mem_visual_frame.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')
        self.mem_visual_frame.grid_rowconfigure(0, weight=1)
        self.mem_visual_frame.grid_columnconfigure(0, weight=1)
        self.mem_canvas = tk.Canvas(self.mem_visual_frame, width=420, height=320, bg='#23272e', highlightthickness=0)
        self.mem_canvas.grid(row=0, column=0, sticky='nsew')
        self.mem_scroll = ttk.Scrollbar(self.mem_visual_frame, orient='vertical', command=self.mem_canvas.yview)
        self.mem_scroll.grid(row=0, column=1, sticky='ns')
        self.mem_canvas.configure(yscrollcommand=self.mem_scroll.set)
        self.mem_table_frame = tk.Frame(self.mem_canvas, bg='#23272e')
        self.mem_canvas.create_window((0,0), window=self.mem_table_frame, anchor='nw')
        self.mem_labels = []
        # Encabezado de la tabla de memoria
        header = tk.Label(self.mem_table_frame, text='Dir', width=5, font=('Consolas', 10, 'bold'), bg='#282c34', fg='#61dafb')
        header.grid(row=0, column=0, sticky='nsew')
        header2 = tk.Label(self.mem_table_frame, text='Contenido', width=32, font=('Consolas', 10, 'bold'), bg='#282c34', fg='#61dafb')
        header2.grid(row=0, column=1, sticky='nsew')
        for i in range(len(self.memory.data)):
            lbl_addr = tk.Label(self.mem_table_frame, text=f'{i:03}', width=5, font=self.custom_font, bg='#23272e', fg='#abb2bf')
            lbl_addr.grid(row=i+1, column=0, sticky='nsew')
            lbl_val = tk.Label(self.mem_table_frame, text=f'{self.memory.data[i]}', anchor='w', width=32, font=self.custom_font, bg='#23272e', fg='#98c379')
            lbl_val.grid(row=i+1, column=1, sticky='nsew')
            self.mem_labels.append((lbl_addr, lbl_val))
        self.mem_table_frame.update_idletasks()
        self.mem_canvas.config(scrollregion=self.mem_canvas.bbox("all"))

        # Panel inferior: ciclo, instrucciones y control
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.step_btn = ttk.Button(self.bottom_frame, text='Paso', command=self.step)
        self.step_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.cycle_frame = ttk.LabelFrame(self.bottom_frame, text='Ciclo de instrucción')
        self.cycle_frame.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.cycle_label = ttk.Label(self.cycle_frame, text='Fase: FETCH')
        self.cycle_label.grid(row=0, column=0, sticky='w')
        self.input_frame = ttk.LabelFrame(self.bottom_frame, text='Programa (una instrucción por línea)')
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.instr_text = tk.Text(self.input_frame, height=6, width=55, font=self.custom_font, bg='#1e2228', fg='#d7dae0', insertbackground='#61dafb', selectbackground='#282c34')
        self.instr_text.grid(row=0, column=0, sticky='ew')
        self.load_btn = ttk.Button(self.input_frame, text='Cargar instrucciones', command=self.load_instructions)
        self.load_btn.grid(row=0, column=1, padx=5)
        self.info_label = tk.Label(self.bottom_frame, text='', anchor='w', justify='left', font=('Consolas', 8), bg='#23272e', fg='#e06c75')
        self.info_label.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=3)

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
        for i, (lbl_addr, lbl_val) in enumerate(self.mem_labels):
            val = self.memory.data[i]
            lbl_val.config(text=f'{val}')
        self.mem_table_frame.update_idletasks()
        self.mem_canvas.config(scrollregion=self.mem_canvas.bbox("all"))
        # Actualizar ciclo de instrucción
        self.cycle_label.config(text=f'Fase: {self.cpu.current_cycle}')
        # Información extendida
        info = f"\n--- INFORMACIÓN DETALLADA ---\n"
        info += f"Registros: {regs['RVPU']}\n"
        info += f"PC: {regs['PC']}  IR: {regs['IR']}  PSW: {regs['PSW']}  MAR: {regs['MAR']}  MBR: {regs['MBR']}\n"
        info += f"Flags: {flags}\n"
        info += f"Ciclo: {self.cpu.current_cycle}\n"
        info += f"Memoria (primeros 32): {[self.memory.data[i] for i in range(32)]}\n"
        if hasattr(self.cpu, '_cycle_state'):
            info += f"_cycle_state: {self.cpu._cycle_state}\n"
        if hasattr(self.cpu, 'halted'):
            info += f"Halted: {self.cpu.halted}\n"
        if hasattr(self.cpu, 'instruction_set'):
            info += f"Instrucciones soportadas: {list(self.cpu.instruction_set.keys())}\n"
        self.info_label.config(text=info)

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
        print("[DEBUG_GUI] load_instructions: Memoria y registros reseteados.")

        # Parsear instrucciones
        lines = self.instr_text.get('1.0', tk.END).strip().split('\n')
        print(f"[DEBUG_GUI] load_instructions: Leyendo {len(lines)} líneas del área de texto.")
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                print(f"[DEBUG_GUI] load_instructions: Línea {i+1} ignorada (vacía o comentario): '{line}'")
                continue

            print(f"[DEBUG_GUI] load_instructions: Parseando línea {i+1}: '{line}'")
            instr = self.parse_instruction(line)

            if instr is not None:
                print(f"[DEBUG_GUI] load_instructions: Línea {i+1} parseada como {instr}. Cargando en M[{i}]")
                if i < len(self.cpu.memory.data):
                    self.cpu.memory.data[i] = instr
                else:
                    print(f"[DEBUG_GUI] load_instructions: ERROR - Índice de memoria {i} fuera de rango para la línea '{line}'.")
            else:
                print(f"[DEBUG_GUI] load_instructions: Línea {i+1} NO PUDO SER PARSEADA. M[{i}] se queda como 0.")
                # Asegurarse de que la memoria se quede en 0 si no se pudo parsear
                if i < len(self.cpu.memory.data):
                    self.cpu.memory.data[i] = 0


        self.update_view()
        print("[DEBUG_GUI] load_instructions: Carga finalizada y vista actualizada.")

    def parse_instruction(self, line):
        # Formato: OPCODE op1,op2,op3
        parts = line.replace(',', ' ').split()
        if not parts:
            print("[DEBUG_GUI] parse_instruction: Línea vacía después de split, devolviendo None.")
            return None
        opcode = parts[0].upper()
        ops = []
        for p_idx, p_val in enumerate(parts[1:]):
            if p_val.startswith('@'):
                try:
                    addr = int(p_val[1:])
                    ops.append(('@', addr))
                except ValueError:
                    print(f"[DEBUG_GUI] parse_instruction: Error al convertir dirección '{p_val}' (índice {p_idx}) a entero para opcode '{opcode}'. Devolviendo None.")
                    return None
            else:
                try:
                    ops.append(int(p_val))
                except ValueError:
                    print(f"[DEBUG_GUI] parse_instruction: Error al convertir operando '{p_val}' (índice {p_idx}) a entero para opcode '{opcode}'. Devolviendo None.")
                    return None
        parsed_tuple = tuple([opcode] + ops)
        print(f"[DEBUG_GUI] parse_instruction: Parseado exitoso: {parsed_tuple}")
        return parsed_tuple

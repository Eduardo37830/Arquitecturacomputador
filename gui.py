import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog

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

    def reset_cpu(self):
        """Resetea el estado de la CPU y la memoria."""
        # self.cpu.memory.data = [0] * len(self.cpu.memory.data)  # resetear la memoria
        self.cpu.registers.PC = 0
        self.cpu.registers.IR = 0
        self.cpu.registers.PSW = 0
        self.cpu.registers.MAR = 0
        self.cpu.registers.MBR = 0
        self.cpu.registers.RVPU = [0] * 8
        self.cpu.alu.flags = {'Z': 0, 'C': 0, 'S': 0, 'O': 0}
        self.cpu.halted = False
        self.cpu.current_cycle = 'FETCH'
        if hasattr(self.cpu, '_fidicofoeiwo_state'):
            self.cpu._fidicofoeiwo_state = 0
            self.cpu._fidicofoeiwo_context = {}
        print("[DEBUG_GUI] CPU y Memoria reseteados.")
        self.info_label.config(text="CPU y Memoria reseteados.")

    def limpiar_primeras_16_posiciones_memoria(self):
        """Limpia (pone a cero) las primeras 16 posiciones de la memoria principal."""
        if hasattr(self.cpu.memory, 'data'):
            for i in range(16):
                self.cpu.memory.data[i] = 0

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelFrame', background='#282c34', foreground='#61dafb', font=('Consolas', 10, 'bold'))
        style.configure('TLabel', background='#282c34', foreground='#abb2bf', font=('Consolas', 9))
        style.configure('TButton', background='#61dafb', foreground='#23272e', font=('Consolas', 9, 'bold'))
        style.configure('TFrame', background='#282c34')

        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

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

        # --- NUEVO: Visualización continua de memoria ---
        self.mem_dump_label = tk.Label(self.mem_visual_frame, text='Memoria (primeros 128 bytes):', bg='#282c34', fg='#61dafb', font=self.custom_font)
        self.mem_dump_label.grid(row=1, column=0, sticky='w', padx=5, pady=(10,0))
        self.mem_dump_text = tk.Text(self.mem_visual_frame, height=10, width=80, font=self.custom_font, bg='#1e2228', fg='#d7dae0', state='disabled')
        self.mem_dump_text.grid(row=2, column=0, sticky='ew', padx=5, pady=2)
        # --- NUEVO: Consola de resultados ---
        self.console_label = tk.Label(self.mem_visual_frame, text='Consola de resultados:', bg='#282c34', fg='#61dafb', font=self.custom_font)
        self.console_label.grid(row=3, column=0, sticky='w', padx=5, pady=(10,0))
        self.console_text = tk.Text(self.mem_visual_frame, height=6, width=80, font=self.custom_font, bg='#181a1f', fg='#e5c07b', state='disabled')
        self.console_text.grid(row=4, column=0, sticky='ew', padx=5, pady=2)

        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.step_btn = ttk.Button(self.bottom_frame, text='Paso', command=self.step)
        self.step_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.cycle_frame = ttk.LabelFrame(self.bottom_frame, text='Ciclo de instrucción')
        self.cycle_frame.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.cycle_label = ttk.Label(self.cycle_frame, text='Fase: FETCH')
        self.cycle_label.grid(row=0, column=0, sticky='w')
        self.phase_desc_label = ttk.Label(self.cycle_frame, text='', font=('Consolas', 9, 'italic'), foreground='#e5c07b')
        self.phase_desc_label.grid(row=1, column=0, sticky='w')
        # --- Modificación aquí ---
        self.input_frame = ttk.LabelFrame(self.bottom_frame, text='Programa')
        self.input_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.instr_text = tk.Text(self.input_frame, height=6, width=55, font=self.custom_font, bg='#1e2228', fg='#d7dae0', insertbackground='#61dafb', selectbackground='#282c34')
        self.instr_text.grid(row=0, column=0, rowspan=2, sticky='ew', padx=5, pady=5)
        self.load_btn = ttk.Button(self.input_frame, text='Cargar desde Texto', command=self.load_instructions)
        self.load_btn.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.load_file_btn = ttk.Button(self.input_frame, text='Cargar desde Archivo (.txt)', command=self.load_from_file)
        self.load_file_btn.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.info_label = tk.Label(self.bottom_frame, text='', anchor='w', justify='left', font=('Consolas', 8), bg='#23272e', fg='#e06c75')
        self.info_label.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=3)

    def append_console(self, msg):
        self.console_text.config(state='normal')
        self.console_text.insert(tk.END, msg + '\n')
        self.console_text.see(tk.END)
        self.console_text.config(state='disabled')

    def append_char(self, char):
        """Añade un solo carácter a la consola sin nueva línea."""
        self.console_text.config(state='normal')
        self.console_text.insert(tk.END, char)
        self.console_text.see(tk.END)
        self.console_text.config(state='disabled')

    def step(self):
        self.cpu.step()
        # Procesa salida de caracteres si corresponde
        if hasattr(self.cpu, 'output_char') and self.cpu.output_char is not None:
            if self.cpu.output_char == '\n':
                self.append_console("")  # Añade salto de línea
            elif self.cpu.output_char != '\r':
                self.append_char(self.cpu.output_char)
            self.cpu.output_char = None  # Limpia el flag/buffer
        # Mostrar en consola si hubo writeback
        if hasattr(self.cpu, '_fidicofoeiwo_state'):
            fases = [
                'FETCH', 'IDENTIFICACION', 'DECODIFICACION', 'CALCULO_OPERANDO',
                'FETCH_OPERANDO', 'EJECUCION', 'WRITEBACK', 'OUTPUT'
            ]
            fase_actual = fases[self.cpu._fidicofoeiwo_state - 1] if self.cpu._fidicofoeiwo_state > 0 else 'OUTPUT'
            if fase_actual == 'WRITEBACK':
                # Mostrar el estado de los registros y flags
                regs = self.cpu.registers.as_dict()
                msg = f"[WRITEBACK] PC={regs['PC']} | RVPU={regs['RVPU']} | PSW={regs['PSW']} | Flags={self.cpu.alu.flags}"
                self.append_console(msg)
        self.update_view()

    def load_instructions(self):
        self.reset_cpu()
        self.limpiar_primeras_16_posiciones_memoria()
        lines = self.instr_text.get('1.0', tk.END).strip().split('\n')
        print(f"[DEBUG_GUI] load_instructions: Leyendo {len(lines)} líneas del área de texto.")
        mem_addr = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                print(f"[DEBUG_GUI] load_instructions: Línea {i+1} ignorada: '{line}'")
                continue
            print(f"[DEBUG_GUI] load_instructions: Parseando línea {i+1}: '{line}'")
            instr = self.parse_instruction(line)
            if instr is not None:
                print(f"[DEBUG_GUI] load_instructions: Línea {i+1} parseada como {instr}. Cargando en M[{mem_addr}]")
                if mem_addr < len(self.cpu.memory.data):
                    self.cpu.memory.data[mem_addr] = instr
                    mem_addr += 1
                else:
                    msg = "Memoria llena. No se cargaron todas las instrucciones."
                    print(f"[ERROR] {msg}")
                    self.info_label.config(text=msg)
                    break
            else:
                print(f"[DEBUG_GUI] load_instructions: Línea {i+1} NO PUDO SER PARSEADA. M[{mem_addr}] se queda como 0.")
                if mem_addr < len(self.cpu.memory.data):
                    self.cpu.memory.data[mem_addr] = 0
                    mem_addr += 1
        self.update_view()
        print("[DEBUG_GUI] load_instructions: Carga finalizada y vista actualizada.")
        self.info_label.config(text="Instrucciones cargadas desde el área de texto.")

    def load_from_file(self):
        import os
        default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'archivos')
        filepath = filedialog.askopenfilename(
            title="Abrir archivo de instrucciones",
            initialdir=default_dir,
            filetypes=(("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*"))
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            self.reset_cpu()
            self.limpiar_primeras_16_posiciones_memoria()
            self.instr_text.delete('1.0', tk.END)
            mem_addr = 0
            for line in lines:
                line = line.strip()
                self.instr_text.insert(tk.END, line + '\n')
                if not line or line.startswith('#'):
                    continue
                instr = self.parse_instruction(line)
                if instr is not None:
                    if mem_addr < len(self.cpu.memory.data):
                        self.cpu.memory.data[mem_addr] = instr
                        mem_addr += 1
                    else:
                        msg = "Memoria llena. No se cargaron todas las instrucciones."
                        print(f"[ERROR] {msg}")
                        self.info_label.config(text=msg)
                        break
                else:
                    msg = f"Error de parseo en línea: '{line}'. Se cargó 0."
                    print(f"[ERROR] {msg}")
                    self.info_label.config(text=msg)
                    if mem_addr < len(self.cpu.memory.data):
                        self.cpu.memory.data[mem_addr] = 0
                        mem_addr += 1
            self.update_view()
            self.info_label.config(text=f"Instrucciones cargadas desde {filepath}")
        except Exception as e:
            print(f"[ERROR_GUI] Error al cargar archivo: {e}")
            self.info_label.config(text=f"Error al cargar archivo: {e}")

    def parse_instruction(self, line):
        # Elimina comentarios y espacios
        line_without_comment = line.split('#')[0].strip()
        if not line_without_comment:
            return None
        parts = line_without_comment.replace(',', ' ').split()
        if not parts:
            return None
        opcode = parts[0].upper()
        ops = []
        for p_idx, p_val in enumerate(parts[1:]):
            p_val = p_val.strip()
            if not p_val:
                continue
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

    def update_view(self):
        # Actualiza los valores de los registros
        regs = self.cpu.registers
        self.reg_labels['PC'].config(text=f'PC: {regs.PC}')
        self.reg_labels['IR'].config(text=f'IR: {regs.IR}')
        self.reg_labels['PSW'].config(text=f'PSW: {regs.PSW}')
        self.reg_labels['MAR'].config(text=f'MAR: {regs.MAR}')
        self.reg_labels['MBR'].config(text=f'MBR: {regs.MBR}')
        for i, val in enumerate(regs.RVPU):
            self.rvpu_labels[i].config(text=f'R{i}: {val}')
        # Actualiza los flags de la ALU
        for flag in ['Z', 'C', 'S', 'O']:
            self.flag_labels[flag].config(text=f'{flag}: {self.cpu.alu.flags[flag]}')
        # Actualiza los buses
        self.bus_labels['Bus de Direcciones (MAR)'].config(text=f'Bus de Direcciones (MAR): {regs.MAR}')
        self.bus_labels['Bus de Datos (MBR)'].config(text=f'Bus de Datos (MBR): {regs.MBR}')
        # Actualiza la memoria visual
        for i, (lbl_addr, lbl_val) in enumerate(self.mem_labels):
            lbl_val.config(text=f'{self.memory.data[i]}')
        # Actualiza el volcado de memoria (primeros 128 bytes)
        self.mem_dump_text.config(state='normal')
        self.mem_dump_text.delete('1.0', 'end')
        dump = ''
        for i in range(0, min(128, len(self.memory.data)), 8):
            row = ' '.join(f'{str(self.memory.data[j]):>8}' for j in range(i, min(i+8, len(self.memory.data))))
            dump += f'{i:03}: {row}\n'
        self.mem_dump_text.insert('1.0', dump)
        self.mem_dump_text.config(state='disabled')
        # Actualiza la fase del ciclo
        fase = self.cpu.get_fidicofoeiwo_phase() if hasattr(self.cpu, 'get_fidicofoeiwo_phase') else 'FETCH'
        self.cycle_label.config(text=f'Fase: {fase}')
        # Descripción de la fase
        descs = {
            'FETCH': 'Busca la instrucción en memoria (PC).',
            'IDENTIFICACION': 'Identifica el tipo de instrucción.',
            'DECODIFICACION': 'Decodifica y separa operandos.',
            'CALCULO_OPERANDO': 'Calcula el valor de los operandos.',
            'FETCH_OPERANDO': 'Obtiene operandos de memoria si es necesario.',
            'EJECUCION': 'Ejecuta la instrucción.',
            'WRITEBACK': 'Actualiza registros y flags.',
            'OUTPUT': 'Fin de ciclo de instrucción.'
        }
        self.phase_desc_label.config(text=descs.get(fase, ''))
        self.update_idletasks()

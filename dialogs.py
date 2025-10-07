import tkinter as tk
from tkinter import simpledialog, messagebox

# ------------------------- BLOQUE DE TEXTO -------------------------
def agregar_bloque_texto(scrollable_frame, botones_frame, canvas):
    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    # Evitar que el frame cambie de tamaño automáticamente
    bloque.pack_propagate(False)

    # Altura = 1/4 de la ventana principal
    bloque.update_idletasks()
    ventana_altura = bloque.winfo_toplevel().winfo_height()
    if ventana_altura < 100:
        ventana_altura = 600
    bloque.config(height=int(ventana_altura * 0.25))

    # Cuadro de texto
    text_widget = tk.Text(bloque, wrap="word", font=("Arial", 14), undo=True, borderwidth=0)
    text_widget.pack(fill="both", expand=True, padx=5, pady=5)

    text_widget.focus_set()
    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

    # Reposicionar botones al final
    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)
    canvas.update_idletasks()


# ------------------------- MOVER BOTONES -------------------------
def mover_botones_abajo(botones_frame, canvas):
    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)
    canvas.update_idletasks()

# ------------------------- SUMA -------------------------
def dibujar_tabla_suma(scrollable_frame, botones_frame, canvas):
    from tkinter import simpledialog
    a = simpledialog.askinteger("Suma", "Primer sumando:", parent=scrollable_frame)
    b = simpledialog.askinteger("Suma", "Segundo sumando:", parent=scrollable_frame)
    if a is None or b is None: return

    filas = 4
    columnas = max(len(str(a)), len(str(b)), len(str(a+b))) + 1

    tabla_frame = tk.Frame(scrollable_frame, bd=2, relief="groove", bg="white")
    tabla_frame.pack(side="top", fill="x", pady=5)

    entries = {}
    a_str, b_str = str(a), str(b)
    for i in range(filas):
        tabla_frame.grid_rowconfigure(i, weight=1)
        for j in range(columnas):
            e = tk.Entry(tabla_frame, font=("Arial", 16), justify="center")
            e.grid(row=i, column=j, sticky="nsew", padx=4, pady=4)
            entries[(i,j)] = e

    # Fila 1
    start_col_a = columnas - len(a_str)
    for j in range(columnas):
        if j>=start_col_a: entries[(1,j)].insert(0, a_str[j-start_col_a])
        entries[(1,j)].config(state="disabled")

    # Fila 2 con +
    start_col_b = columnas - len(b_str)
    for j in range(columnas):
        if j==0: entries[(2,j)].insert(0,"+")
        elif j>=start_col_b: entries[(2,j)].insert(0,b_str[j-start_col_b])
        entries[(2,j)].config(state="disabled")

    # Configuración filas/columnas
    for i in range(filas):
        tabla_frame.grid_rowconfigure(i, weight=1)
    for j in range(columnas):
        tabla_frame.grid_columnconfigure(j, weight=1)

    scrollable_frame.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)

# ------------------------- RESTA -------------------------
def dibujar_tabla_resta(scrollable_frame, botones_frame, canvas):
    from tkinter import simpledialog
    a = simpledialog.askinteger("Resta", "Minuendo:", parent=scrollable_frame)
    b = simpledialog.askinteger("Resta", "Sustraendo:", parent=scrollable_frame)
    if a is None or b is None: return

    filas = 4
    columnas = max(len(str(a)), len(str(b)), len(str(a-b))) + 1

    tabla_frame = tk.Frame(scrollable_frame, bd=2, relief="groove", bg="white")
    tabla_frame.pack(side="top", fill="x", pady=5)

    entries = {}
    a_str, b_str = str(a), str(b)
    for i in range(filas):
        tabla_frame.grid_rowconfigure(i, weight=1)
        for j in range(columnas):
            e = tk.Entry(tabla_frame, font=("Arial",16), justify="center")
            e.grid(row=i,column=j,sticky="nsew",padx=4,pady=4)
            entries[(i,j)] = e

    # Fila 1
    start_col_a = columnas - len(a_str)
    for j in range(columnas):
        if j>=start_col_a: entries[(1,j)].insert(0, a_str[j-start_col_a])
        entries[(1,j)].config(state="disabled")

    # Fila 2 con -
    start_col_b = columnas - len(b_str)
    for j in range(columnas):
        if j==0: entries[(2,j)].insert(0,"-")
        elif j>=start_col_b: entries[(2,j)].insert(0,b_str[j-start_col_b])
        entries[(2,j)].config(state="disabled")

    # Configuración filas/columnas
    for i in range(filas):
        tabla_frame.grid_rowconfigure(i,weight=1)
    for j in range(columnas):
        tabla_frame.grid_columnconfigure(j,weight=1)

    scrollable_frame.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)

# ------------------------- MULTIPLICACIÓN -------------------------
# ------------------------- MULTIPLICACIÓN -------------------------
def dibujar_tabla_multiplicacion(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    from tkinter import simpledialog, messagebox

    # --- Dialogo para pedir los números ---
    class MultiplicacionDialog(simpledialog.Dialog):
        def body(self, master):
            tk.Label(master, text="Introduce el 1º multiplicando:").grid(row=0, column=0, sticky="w")
            tk.Label(master, text="Introduce el 2º multiplicando:").grid(row=1, column=0, sticky="w")

            self.entry_a = tk.Entry(master)
            self.entry_b = tk.Entry(master)
            self.entry_a.grid(row=0, column=1, padx=5, pady=5)
            self.entry_b.grid(row=1, column=1, padx=5, pady=5)

            return self.entry_a

        def apply(self):
            try:
                self.a = int(self.entry_a.get())
                self.b = int(self.entry_b.get())
            except ValueError:
                self.a = None
                self.b = None

    # --- Crear diálogo y obtener los valores ---
    root_aux = tk.Tk()
    root_aux.withdraw()
    dialog = MultiplicacionDialog(root_aux, title="Introduce los números")
    root_aux.destroy()

    if dialog.a is None or dialog.b is None:
        return

    a, b = dialog.a, dialog.b

    # --- Calcular filas y columnas ---
    def calcular_filas_columnas(a, b):
        filas = 4
        if len(str(b)) > 1:
            filas += len(str(b))
        columnas = len(str(a * b)) + 1
        return filas, columnas

    filas, columnas = calcular_filas_columnas(a, b)

    # --- Crear bloque de tabla ---
    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    entries = {}
    a_str = str(a)
    b_str = str(b)

    # --- Crear celdas ---
    for i in range(filas):
        bloque.grid_rowconfigure(i, weight=1)
        for j in range(columnas):
            bloque.grid_columnconfigure(j, weight=1)
            e = tk.Entry(bloque, font=("Arial", font_size), justify="center", bd=2, relief="groove")
            e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
            entries[(i, j)] = e

    # --- Fila 1: primer multiplicando (bloqueado) ---
    start_col_a = columnas - len(a_str)
    for j in range(columnas):
        if j >= start_col_a:
            entries[(1, j)].insert(0, a_str[j - start_col_a])
        entries[(1, j)].config(state="disabled")

    # --- Fila 2: multiplicador con X (bloqueado) ---
    start_col_b = columnas - len(b_str)
    for j in range(columnas):
        if j == 0:
            entries[(2, j)].insert(0, "X")
        elif j >= start_col_b:
            entries[(2, j)].insert(0, b_str[j - start_col_b])
        entries[(2, j)].config(state="disabled")

    # --- Símbolo + en la penúltima fila si b tiene más de un dígito ---
    if len(str(b)) > 1:
        entries[(filas - 2, 0)].insert(0, "+")
        entries[(filas - 2, 0)].config(state="disabled")

    # --- Actualizar scroll y mover botones ---
    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)

# ------------------------- DIVISIÓN -------------------------
def dibujar_tabla_division(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    from tkinter import simpledialog, messagebox

    class DivisionDialog(simpledialog.Dialog):
        def body(self, master):
            tk.Label(master, text="Introduce el dividendo:", font=("Arial", font_size)).grid(row=0, column=0, sticky="w", pady=5)
            tk.Label(master, text="Introduce el divisor:", font=("Arial", font_size)).grid(row=1, column=0, sticky="w", pady=5)

            self.entry_dividendo = tk.Entry(master, font=("Arial", font_size))
            self.entry_divisor = tk.Entry(master, font=("Arial", font_size))
            self.entry_dividendo.grid(row=0, column=1, padx=5, pady=5)
            self.entry_divisor.grid(row=1, column=1, padx=5, pady=5)
            return self.entry_dividendo

        def apply(self):
            try:
                self.dividendo = int(self.entry_dividendo.get())
                self.divisor = int(self.entry_divisor.get())
            except ValueError:
                self.dividendo = None
                self.divisor = None

    root_aux = tk.Tk()
    root_aux.withdraw()
    dialog = DivisionDialog(root_aux, title="Introduce los números")
    root_aux.destroy()
    if dialog.dividendo is None or dialog.divisor is None:
        return

    dividendo = dialog.dividendo
    divisor = dialog.divisor

    n = len(str(dividendo))
    m = len(str(divisor))
    primeros_m = int(str(dividendo)[:m])
    if primeros_m >= divisor:
        filas = (n - m + 1) + 1
    else:
        filas = (n - m) + 1

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    entries = {}
    columnas = 2
    for i in range(filas):
        bloque.grid_rowconfigure(i, weight=1)
        for j in range(columnas):
            bloque.grid_columnconfigure(j, weight=1)
            e = tk.Entry(bloque, font=("Arial", font_size), justify="center", bd=2, relief="groove")
            e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
            entries[(i,j)] = e

    entries[(0,0)].insert(0, str(dividendo))
    entries[(0,0)].config(state="disabled", disabledbackground="#f0f0f0", disabledforeground="black")
    entries[(0,1)].insert(0, str(divisor))
    entries[(0,1)].config(state="disabled", disabledbackground="#f0f0f0", disabledforeground="black")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)
    
# ------------------------- FACTORIAL (botón "|") -------------------------
def contar_filas(numero: int) -> int:
    if numero < 1: return 1
    n = numero
    count = 0
    d = 2
    while n>1:
        if n%d==0:
            n//=d
            count+=1
        else:
            d+=1
    return count+1

def dibujar_tabla_factorial(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    numero = simpledialog.askinteger("Recomposición factorial", "Introduce un número:", parent=scrollable_frame)
    if numero is None: return

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    filas = contar_filas(numero)
    entries = {}
    for i in range(filas):
        bloque.grid_rowconfigure(i, weight=1)
        for j in range(2):
            bloque.grid_columnconfigure(j, weight=1)
            e = tk.Entry(bloque, font=("Arial", font_size), justify="center", bd=2, relief="groove")
            e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
            entries[(i,j)] = e
    entries[(0,0)].insert(0,str(numero))
    entries[(0,0)].config(state="disabled")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)

# ------------------------- RAÍZ (botón "√") -------------------------
class RaizDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Índice de la raíz:", font=("Arial",14)).grid(row=0,column=0,sticky="w", pady=5)
        tk.Label(master, text="Radicando:", font=("Arial",14)).grid(row=1,column=0,sticky="w", pady=5)
        self.entry_indice = tk.Entry(master,font=("Arial",14))
        self.entry_radicando = tk.Entry(master,font=("Arial",14))
        self.entry_indice.grid(row=0,column=1,padx=10,pady=5)
        self.entry_radicando.grid(row=1,column=1,padx=10,pady=5)
        return self.entry_indice
    def apply(self):
        try:
            self.indice = int(self.entry_indice.get())
            self.radicando = int(self.entry_radicando.get())
        except ValueError:
            self.indice=None
            self.radicando=None

def dibujar_tabla_raiz(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    root_aux = tk.Tk()
    root_aux.withdraw()
    dialog = RaizDialog(root_aux, title="Datos de la raíz")
    root_aux.destroy()
    if not dialog.indice or not dialog.radicando: return

    indice = dialog.indice
    radicando = dialog.radicando

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    filas = contar_filas(radicando)
    entries = {}
    for i in range(filas):
        bloque.grid_rowconfigure(i, weight=1)
        for j in range(3):
            bloque.grid_columnconfigure(j, weight=1)
            if (i,j)==(0,0):
                frame_super = tk.Frame(bloque, bg="#e0e0e0")
                frame_super.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
                label_super = tk.Label(frame_super, text=str(indice), font=("Arial", font_size), bg="#e0e0e0")
                label_super.place(relx=0.9, rely=0.2, anchor="ne")
                entries[(i,j)] = frame_super
            else:
                e = tk.Entry(bloque, font=("Arial", font_size), justify="center", bd=2, relief="groove")
                e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
                entries[(i,j)] = e

    for i in range(1, filas):
        entries[(i,0)].config(state="disabled", disabledbackground="#e0e0e0", disabledforeground="black")

    entries[(0,1)].insert(0,str(radicando))
    entries[(0,1)].config(state="disabled", disabledbackground="#f0f0f0", disabledforeground="black")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)

# ------------------------- CÓDIGO BINARIO (botón "01/10") -------------------------
def dibujar_tabla_binaria(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    numero_str = simpledialog.askstring("Código binario", "Introduce un número:", parent=scrollable_frame)
    if not numero_str: return
    try:
        numero = int(numero_str)
    except ValueError:
        messagebox.showerror("Error","Debes introducir un número válido.")
        return

    def calcular_filas(valor: int) -> int:
        filas = 1
        while valor > 1:
            valor //= 2
            filas +=1
        return filas

    filas = calcular_filas(numero)
    columnas = filas

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    entries = {}
    fixed = {}
    if filas>0 and columnas>0: fixed[(0,0)] = numero_str
    if columnas>1: fixed[(0,1)] = "2"
    for i in range(1, filas):
        col = i+1
        if col < columnas: fixed[(i,col)] = "2"

    for i in range(filas):
        bloque.grid_rowconfigure(i, weight=1)
        for j in range(columnas):
            bloque.grid_columnconfigure(j, weight=1)
            e = tk.Entry(bloque, font=("Arial", font_size), justify="center", bd=2, relief="groove")
            e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
            entries[(i,j)] = e
            if (i,j) in fixed:
                e.insert(0,fixed[(i,j)])
                e.config(state="disabled")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)

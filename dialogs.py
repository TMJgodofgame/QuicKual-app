import tkinter as tk
from tkinter import simpledialog, messagebox
from decimal import Decimal, InvalidOperation
from bloques import _add_header_with_trash, mover_botones_abajo


# ====
# Utilidades para + y -
# ====

def _normalize_decimal_input(text: str) -> str:
    """
    Normaliza la entrada:
    - trim
    - reemplaza ',' por '.'
    """
    if text is None:
        return None
    text = text.strip()
    if not text:
        return None
    return text.replace(",", ".")


def _parse_decimal(text: str) -> Decimal:
    """Parsea a Decimal tras normalizar. Lanza InvalidOperation si no es válido."""
    norm = _normalize_decimal_input(text)
    if norm is None:
        raise InvalidOperation("Entrada vacía")
    return Decimal(norm)


def _split_parts_for_display(original_text: str) -> tuple[str, str, bool]:
    """
    Devuelve (entera, decimal, has_decimal) respetando lo que escribió el usuario.
    Se usa coma para la visualización.
    """
    if original_text is None:
        return "", "", False
    txt = original_text.strip()
    if not txt:
        return "", "", False

    # Mostrar coma en la UI
    txt = txt.replace(".", ",")

    if "," in txt:
        left, right = txt.split(",", 1)
        # Si left es "" o solo signo, convertimos a ±0
        if left in ("", "+", "-"):
            left = f"{'-' if left=='-' else ('+' if left=='+' else '')}0"
        return left, right, True
    return txt, "", False


def _compute_widths_for_two_numbers(a_ent: str, a_dec: str, a_has_dec: bool,
                                      b_ent: str, b_dec: str, b_has_dec: bool) -> tuple[int, int, bool]:
    max_entera = max(len(a_ent), len(b_ent))
    max_decimal = max(len(a_dec), len(b_dec))
    show_comma = (a_has_dec or b_has_dec)
    return max_entera, max_decimal, show_comma


def _build_grid_for_addsub(parent_content: tk.Frame, filas: int, columnas: int, font_size: int = 16, padding: int = 4):
    entries = {}
    for i in range(filas):
        parent_content.grid_rowconfigure(i, weight=1)
    for j in range(columnas):
        parent_content.grid_columnconfigure(j, weight=1)
        e = tk.Entry(parent_content, font=("Arial", font_size), justify="center", bd=2, relief="groove")
        e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
        entries[(i, j)] = e
    return entries


def _place_number_into_entries(entries: dict,
                                 fila: int,
                                 entera: str,
                                 decimal: str,
                                 max_entera: int,
                                 max_decimal: int,
                                 show_comma: bool,
                                 has_decimal: bool,    # decide si escribir la coma visual
                                 start_col: int = 0,
                                 font_disable: bool = True) -> None:
    """
    Inserta un número separando parte entera/decimal.
    - Parte entera a la derecha.
    - Coma solo si has_decimal es True.
    - Decimales a la izquierda después de la coma (si existe).
    """
    ent_str = entera
    if ent_str in ("", "+", "-"):
        ent_str = "0" if ent_str == "" else ent_str + "0"

    # Parte entera
    for i in range(max_entera):
        j = start_col + 1 + i  # col 0 reservada para símbolo operación en fila 2
        idx_ent = len(ent_str) - (max_entera - i)
        ch = ent_str[idx_ent] if 0 <= idx_ent < len(ent_str) else ""
        entries[(fila, j)].insert(0, ch)
        if font_disable:
            entries[(fila, j)].config(state="disabled")

    # Coma
    comma_col = start_col + 1 + max_entera
    if show_comma and has_decimal:
        entries[(fila, comma_col)].insert(0, ",")
        if font_disable:
            entries[(fila, comma_col)].config(state="disabled")

    # Decimales
    for d in range(max_decimal):
        j = (comma_col + 1 + d) if show_comma else (start_col + 1 + max_entera + d)
        ch = decimal[d] if d < len(decimal) else ""
        entries[(fila, j)].insert(0, ch)
        if font_disable:
            entries[(fila, j)].config(state="disabled")


# ====
# Bloque de texto (sin cambios)
# ====

def agregar_bloque_texto(scrollable_frame, botones_frame, canvas):
    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    bloque.pack_propagate(False)

    bloque.update_idletasks()
    ventana_altura = bloque.winfo_toplevel().winfo_height()
    if ventana_altura < 100:
        ventana_altura = 600
    bloque.config(height=int(ventana_altura * 0.25))

    content = _add_header_with_trash(bloque, botones_frame, canvas)

    text_widget = tk.Text(content, wrap="word", font=("Arial", 14), undo=True, borderwidth=0, bg="white")
    text_widget.pack(fill="both", expand=True, padx=5, pady=5)

    text_widget.focus_set()
    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)
    canvas.update_idletasks()


def mover_botones_abajo(botones_frame, canvas):
    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)
    canvas.update_idletasks()


# ====
# Diálogos personalizados
# ====

class SumaDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Ingrese el primer sumando:", font=("Arial", 14)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(master, text="Ingrese el segundo sumando:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", pady=5)

        self.entry_a = tk.Entry(master, font=("Arial", 14))
        self.entry_b = tk.Entry(master, font=("Arial", 14))
        self.entry_a.grid(row=0, column=1, padx=10, pady=5)
        self.entry_b.grid(row=1, column=1, padx=10, pady=5)
        return self.entry_a  # foco inicial

    def apply(self):
        self.a_text = self.entry_a.get()
        self.b_text = self.entry_b.get()


class RestaDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Ingrese el minuendo:", font=("Arial", 14)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(master, text="Ingrese el sustraendo:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", pady=5)

        self.entry_a = tk.Entry(master, font=("Arial", 14))
        self.entry_b = tk.Entry(master, font=("Arial", 14))
        self.entry_a.grid(row=0, column=1, padx=10, pady=5)
        self.entry_b.grid(row=1, column=1, padx=10, pady=5)
        return self.entry_a  # foco inicial

    def apply(self):
        self.a_text = self.entry_a.get()
        self.b_text = self.entry_b.get()


# ====
# Suma (decimales, 4 filas, sin resultado, fila 2 bloqueada)
# ====

def dibujar_tabla_suma(scrollable_frame, botones_frame, canvas):
    # Un único diálogo para ambos sumandos
    root_aux = tk.Tk()
    root_aux.withdraw()
    dialog = SumaDialog(root_aux, title="Suma")
    root_aux.destroy()

    a_text = getattr(dialog, "a_text", None)
    b_text = getattr(dialog, "b_text", None)
    if a_text is None or b_text is None:
        return

    try:
        _ = _parse_decimal(a_text)
        _ = _parse_decimal(b_text)
    except (InvalidOperation, ValueError):
        messagebox.showerror("Error", "Debes introducir números válidos (usa coma o punto para decimales).")
        return

    a_ent, a_dec, a_has_dec = _split_parts_for_display(a_text)
    b_ent, b_dec, b_has_dec = _split_parts_for_display(b_text)

    max_ent, max_dec, show_comma = _compute_widths_for_two_numbers(
        a_ent, a_dec, a_has_dec, b_ent, b_dec, b_has_dec
    )

    columnas = 1 + max_ent + (1 if show_comma else 0) + max_dec
    filas = 4  # estructura original

    tabla_frame = tk.Frame(scrollable_frame, bd=2, relief="groove", bg="white")
    tabla_frame.pack(side="top", fill="x", pady=5)

    content = _add_header_with_trash(tabla_frame, botones_frame, canvas)
    entries = _build_grid_for_addsub(content, filas, columnas, font_size=16, padding=4)

    # Fila 1: primer sumando
    _place_number_into_entries(
        entries, fila=1, entera=a_ent, decimal=a_dec,
        max_entera=max_ent, max_decimal=max_dec,
        show_comma=show_comma, has_decimal=a_has_dec,
        start_col=0, font_disable=True
    )

    # Fila 2: símbolo + y segundo sumando (bloqueada)
    entries[(2, 0)].insert(0, "+")
    entries[(2, 0)].config(state="disabled")

    _place_number_into_entries(
        entries, fila=2, entera=b_ent, decimal=b_dec,
        max_entera=max_ent, max_decimal=max_dec,
        show_comma=show_comma, has_decimal=b_has_dec,
        start_col=0, font_disable=True
    )

    # Bloquear TODA la fila 2
    for col in range(columnas):
        try:
            entries[(2, col)].config(state="disabled")
        except Exception:
            pass

    # Fila 3: vacía (no mostramos resultado)

    scrollable_frame.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)


# ====
# Resta (decimales, 4 filas, sin resultado, fila 2 bloqueada)
# ====

def dibujar_tabla_resta(scrollable_frame, botones_frame, canvas):
    # Un único diálogo para minuendo y sustraendo
    root_aux = tk.Tk()
    root_aux.withdraw()
    dialog = RestaDialog(root_aux, title="Resta")
    root_aux.destroy()

    a_text = getattr(dialog, "a_text", None)  # minuendo
    b_text = getattr(dialog, "b_text", None)  # sustraendo
    if a_text is None or b_text is None:
        return

    try:
        _ = _parse_decimal(a_text)
        _ = _parse_decimal(b_text)
    except (InvalidOperation, ValueError):
        messagebox.showerror("Error", "Debes introducir números válidos (usa coma o punto para decimales).")
        return

    a_ent, a_dec, a_has_dec = _split_parts_for_display(a_text)
    b_ent, b_dec, b_has_dec = _split_parts_for_display(b_text)

    max_ent, max_dec, show_comma = _compute_widths_for_two_numbers(
        a_ent, a_dec, a_has_dec, b_ent, b_dec, b_has_dec
    )

    columnas = 1 + max_ent + (1 if show_comma else 0) + max_dec
    filas = 4

    tabla_frame = tk.Frame(scrollable_frame, bd=2, relief="groove", bg="white")
    tabla_frame.pack(side="top", fill="x", pady=5)

    content = _add_header_with_trash(tabla_frame, botones_frame, canvas)
    entries = _build_grid_for_addsub(content, filas, columnas, font_size=16, padding=4)

    # Fila 1: minuendo
    _place_number_into_entries(
        entries, fila=1, entera=a_ent, decimal=a_dec,
        max_entera=max_ent, max_decimal=max_dec,
        show_comma=show_comma, has_decimal=a_has_dec,
        start_col=0, font_disable=True
    )

    # Fila 2: símbolo - y sustraendo (bloqueada)
    entries[(2, 0)].insert(0, "-")
    entries[(2, 0)].config(state="disabled")

    _place_number_into_entries(
        entries, fila=2, entera=b_ent, decimal=b_dec,
        max_entera=max_ent, max_decimal=max_dec,
        show_comma=show_comma, has_decimal=b_has_dec,
        start_col=0, font_disable=True
    )

    # Bloquear toda la fila 2
    for col in range(columnas):
        try:
            entries[(2, col)].config(state="disabled")
        except Exception:
            pass

    # Fila 3: vacía (no mostramos resultado)

    scrollable_frame.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)


# ====
# Multiplicación (sin cambios funcionales)
# ====

def dibujar_tabla_multiplicacion(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
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

    root_aux = tk.Tk()
    root_aux.withdraw()
    dialog = MultiplicacionDialog(root_aux, title="Introduce los números")
    root_aux.destroy()

    if dialog.a is None or dialog.b is None:
        return

    a, b = dialog.a, dialog.b

    def calcular_filas_columnas(a_val, b_val):
        filas_loc = 4
        if len(str(b_val)) > 1:
            filas_loc += len(str(b_val))
        columnas_loc = len(str(a_val * b_val)) + 1
        return filas_loc, columnas_loc

    filas, columnas = calcular_filas_columnas(a, b)

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    content = _add_header_with_trash(bloque, botones_frame, canvas)

    entries = {}
    a_str = str(a)
    b_str = str(b)

    for i in range(filas):
        content.grid_rowconfigure(i, weight=1)
    for j in range(columnas):
        content.grid_columnconfigure(j, weight=1)
        e = tk.Entry(content, font=("Arial", font_size), justify="center", bd=2, relief="groove")
        e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
        entries[(i, j)] = e

    start_col_a = columnas - len(a_str)
    for j in range(columnas):
        if j >= start_col_a:
            entries[(1, j)].insert(0, a_str[j - start_col_a])
            entries[(1, j)].config(state="disabled")

    start_col_b = columnas - len(b_str)
    for j in range(columnas):
        if j == 0:
            entries[(2, j)].insert(0, "X")
        elif j >= start_col_b:
            entries[(2, j)].insert(0, b_str[j - start_col_b])
        entries[(2, j)].config(state="disabled")

    if len(str(b)) > 1:
        entries[(filas - 2, 0)].insert(0, "+")
        entries[(filas - 2, 0)].config(state="disabled")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)


# ====
# División (sin cambios)
# ====

def dibujar_tabla_division(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
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

    content = _add_header_with_trash(bloque, botones_frame, canvas)

    entries = {}
    columnas = 2
    for i in range(filas):
        content.grid_rowconfigure(i, weight=1)
    for j in range(columnas):
        content.grid_columnconfigure(j, weight=1)
        e = tk.Entry(content, font=("Arial", font_size), justify="center", bd=2, relief="groove")
        e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
        entries[(i, j)] = e

    entries[(0, 0)].insert(0, str(dividendo))
    entries[(0, 0)].config(state="disabled", disabledbackground="#f0f0f0", disabledforeground="black")
    entries[(0, 1)].insert(0, str(divisor))
    entries[(0, 1)].config(state="disabled", disabledbackground="#f0f0f0", disabledforeground="black")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)


# ====
# Factorial (sin cambios)
# ====

def contar_filas(numero: int) -> int:
    if numero < 1:
        return 1
    n = numero
    count = 0
    d = 2
    while n > 1:
        if n % d == 0:
            n //= d
            count += 1
        else:
            d += 1
    return count + 1


def dibujar_tabla_factorial(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    numero = simpledialog.askinteger("Recomposición factorial", "Introduce un número:", parent=scrollable_frame)
    if numero is None:
        return

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    content = _add_header_with_trash(bloque, botones_frame, canvas)

    filas = contar_filas(numero)
    entries = {}
    for i in range(filas):
        content.grid_rowconfigure(i, weight=1)
    for j in range(2):
        content.grid_columnconfigure(j, weight=1)
        e = tk.Entry(content, font=("Arial", font_size), justify="center", bd=2, relief="groove")
        e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
        entries[(i, j)] = e
    entries[(0, 0)].insert(0, str(numero))
    entries[(0, 0)].config(state="disabled")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)


# ====
# Raíz (sin cambios)
# ====

class RaizDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Índice de la raíz:", font=("Arial", 14)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(master, text="Radicando:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_indice = tk.Entry(master, font=("Arial", 14))
        self.entry_radicando = tk.Entry(master, font=("Arial", 14))
        self.entry_indice.grid(row=0, column=1, padx=10, pady=5)
        self.entry_radicando.grid(row=1, column=1, padx=10, pady=5)
        return self.entry_indice

    def apply(self):
        try:
            self.indice = int(self.entry_indice.get())
            self.radicando = int(self.entry_radicando.get())
        except ValueError:
            self.indice = None
            self.radicando = None


def dibujar_tabla_raiz(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    root_aux = tk.Tk()
    root_aux.withdraw()
    dialog = RaizDialog(root_aux, title="Datos de la raíz")
    root_aux.destroy()
    if not dialog.indice or not dialog.radicando:
        return

    indice = dialog.indice
    radicando = dialog.radicando

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    content = _add_header_with_trash(bloque, botones_frame, canvas)

    filas = contar_filas(radicando)
    entries = {}
    for i in range(filas):
        content.grid_rowconfigure(i, weight=1)
    for j in range(3):
        content.grid_columnconfigure(j, weight=1)
        if (i, j) == (0, 0):
            frame_super = tk.Frame(content, bg="#e0e0e0")
            frame_super.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
            label_super = tk.Label(frame_super, text=str(indice), font=("Arial", font_size), bg="#e0e0e0")
            label_super.place(relx=0.9, rely=0.2, anchor="ne")
            entries[(i, j)] = frame_super
        else:
            e = tk.Entry(content, font=("Arial", font_size), justify="center", bd=2, relief="groove")
            e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
            entries[(i, j)] = e

    for i in range(1, filas):
        if isinstance(entries[(i, 0)], tk.Entry):
            entries[(i, 0)].config(state="disabled", disabledbackground="#e0e0e0", disabledforeground="black")

    entries[(0, 1)].insert(0, str(radicando))
    entries[(0, 1)].config(state="disabled", disabledbackground="#f0f0f0", disabledforeground="black")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)


# ====
# Binario (sin cambios)
# ====

def dibujar_tabla_binaria(scrollable_frame, botones_frame, canvas, font_size=16, padding=4):
    numero_str = simpledialog.askstring("Código binario", "Introduce un número:", parent=scrollable_frame)
    if not numero_str:
        return
    try:
        numero = int(numero_str)
    except ValueError:
        messagebox.showerror("Error", "Debes introducir un número válido.")
        return

    def calcular_filas(valor: int) -> int:
        filas_loc = 1
        while valor > 1:
            valor //= 2
            filas_loc += 1
        return filas_loc

    filas = calcular_filas(numero)
    columnas = filas

    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    content = _add_header_with_trash(bloque, botones_frame, canvas)

    entries = {}
    fixed = {}
    if filas > 0 and columnas > 0:
        fixed[(0, 0)] = numero_str
        if columnas > 1:
            fixed[(0, 1)] = "2"
        for i in range(1, filas):
            col = i + 1
            if col < columnas:
                fixed[(i, col)] = "2"

    for i in range(filas):
        content.grid_rowconfigure(i, weight=1)
    for j in range(columnas):
        content.grid_columnconfigure(j, weight=1)
        e = tk.Entry(content, font=("Arial", font_size), justify="center", bd=2, relief="groove")
        e.grid(row=i, column=j, sticky="nsew", padx=padding, pady=padding)
        entries[(i, j)] = e
        if (i, j) in fixed:
            e.insert(0, fixed[(i, j)])
            e.config(state="disabled")

    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)
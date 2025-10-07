import tkinter as tk
from dialogs import (
    dibujar_tabla_suma, dibujar_tabla_resta,
    dibujar_tabla_multiplicacion, dibujar_tabla_division,
    dibujar_tabla_factorial, dibujar_tabla_raiz,
    dibujar_tabla_binaria
)

def abrir_submenu(scrollable_frame, botones_frame, canvas):
    popup = tk.Toplevel(scrollable_frame)
    popup.title("QuicKual - Operaciones")
    popup.transient(scrollable_frame)
    popup.grab_set()

    mid_font = ("Arial", 18, "bold")
    small_font = ("Arial", 12, "bold")

    # Botones principales
    for i, simbolo in enumerate(['+','−','X','÷']):
        btn = tk.Button(popup, text=simbolo, font=("Arial",24,"bold"), width=5, height=2,
                        command=lambda s=simbolo: accion_operacion(s, scrollable_frame, botones_frame, canvas, popup))
        btn.grid(row=0, column=i, padx=10, pady=10)

    # Botones adicionales
    for i, simbolo in enumerate(['|','√','01\n10']):
        btn = tk.Button(popup, text=simbolo, font=mid_font, width=5, height=2,
                        command=lambda s=simbolo: accion_operacion(s, scrollable_frame, botones_frame, canvas, popup))
        btn.grid(row=1, column=i, padx=10, pady=10)

def accion_operacion(simbolo, scrollable_frame, botones_frame, canvas, popup):
    popup.destroy()
    if simbolo=='+': dibujar_tabla_suma(scrollable_frame, botones_frame, canvas)
    elif simbolo=='−': dibujar_tabla_resta(scrollable_frame, botones_frame, canvas)
    elif simbolo=='X': dibujar_tabla_multiplicacion(scrollable_frame, botones_frame, canvas)
    elif simbolo=='÷': dibujar_tabla_division(scrollable_frame, botones_frame, canvas)
    elif simbolo=='|': dibujar_tabla_factorial(scrollable_frame, botones_frame, canvas)
    elif simbolo=='√': dibujar_tabla_raiz(scrollable_frame, botones_frame, canvas)
    elif simbolo=='01\n10': dibujar_tabla_binaria(scrollable_frame, botones_frame, canvas)
